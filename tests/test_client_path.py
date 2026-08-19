"""Client path: cross-account assumption, encryption wiring, and tenant scoping.

These are regression tests for the security properties the architecture depends on,
not coverage for its own sake. Each one fails if a specific boundary is weakened.
"""

import importlib
import json
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def client_mod():
    mod = importlib.import_module("LambdaFunctionForBaseTable_Client")
    return importlib.reload(mod)


# --------------------------------------------------------------------- STS boundary

def test_assumes_the_configured_data_account_role(client_mod, temp_credentials):
    """The app account must reach data only by assuming the one configured role."""
    sts = MagicMock()
    sts.assume_role.return_value = {"Credentials": temp_credentials}

    with patch.object(client_mod.boto3, "client", return_value=sts) as boto_client:
        got = client_mod.assume_role_in_data_account()

    boto_client.assert_called_once_with("sts", region_name=client_mod.AWS_REGION)
    sts.assume_role.assert_called_once()
    assert sts.assume_role.call_args.kwargs["RoleArn"] == client_mod.DATA_ACCOUNT_ROLE_ARN
    assert got == temp_credentials


def test_no_long_lived_credentials_are_read_from_the_environment(client_mod):
    """Nothing in the handler should reach for static access keys."""
    source = (client_mod.__file__ or "")
    with open(source, encoding="utf-8") as fh:
        text = fh.read()
    for forbidden in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
        assert f'os.environ["{forbidden}"]' not in text
        assert f'os.environ.get("{forbidden}"' not in text


# ------------------------------------------------------------- the credentials bug

def test_kms_provider_receives_the_assumed_role_session_not_the_default(
    client_mod, temp_credentials
):
    """The bug this whole test file exists for.

    AwsKmsCryptographicMaterialsProvider takes a botocore.session.Session. If one is
    not passed explicitly it falls back to the default session, which inside Lambda
    is the *execution role* -- so KMS operations run as the wrong principal and the
    cross-account boundary is silently defeated. It does not raise; it just works
    as the wrong identity.

    This asserts the provider is handed the botocore session belonging to the
    assumed-role boto3 session, and nothing else.
    """
    session = MagicMock(name="assumed_role_session")

    with patch.object(client_mod.boto3, "Session", return_value=session) as mk_session, \
         patch.object(client_mod, "AwsKmsCryptographicMaterialsProvider") as mk_cmp, \
         patch.object(client_mod, "EncryptedTable") as mk_encrypted:
        mk_encrypted.return_value.get_item.return_value = {"Item": {"id": "c-1"}}
        client_mod.retrieve_client_info("c-1", temp_credentials)

    # the session was built from the temporary credentials, not ambient ones
    assert mk_session.call_args.kwargs["aws_access_key_id"] == temp_credentials["AccessKeyId"]
    assert mk_session.call_args.kwargs["aws_session_token"] == temp_credentials["SessionToken"]

    # and the KMS provider got *that* session's botocore session
    assert mk_cmp.call_args.kwargs["botocore_session"] is session._session
    assert mk_cmp.call_args.kwargs["key_id"] == client_mod.KMS_KEY_ALIAS


def test_kms_key_is_referenced_by_alias_not_raw_key_id(client_mod):
    """Aliases let the key rotate without a code change."""
    assert client_mod.KMS_KEY_ALIAS.startswith("alias/")


def test_reads_go_through_the_encrypted_table_wrapper(client_mod, temp_credentials):
    """A plain Table handle would return ciphertext and skip KMS entirely."""
    session = MagicMock()

    with patch.object(client_mod.boto3, "Session", return_value=session), \
         patch.object(client_mod, "AwsKmsCryptographicMaterialsProvider"), \
         patch.object(client_mod, "EncryptedTable") as mk_encrypted:
        mk_encrypted.return_value.get_item.return_value = {"Item": {"id": "c-1"}}
        client_mod.retrieve_client_info("c-1", temp_credentials)

    mk_encrypted.assert_called_once()
    mk_encrypted.return_value.get_item.assert_called_once()
    # the raw table handle itself was never queried
    session.resource.return_value.Table.return_value.get_item.assert_not_called()


# ------------------------------------------------------------------ tenant scoping

def test_lookup_is_keyed_by_the_identifier_from_the_event(client_mod, temp_credentials):
    """The key must be the caller's validated claim, not a scan or a wildcard."""
    session = MagicMock()

    with patch.object(client_mod.boto3, "Session", return_value=session), \
         patch.object(client_mod, "AwsKmsCryptographicMaterialsProvider"), \
         patch.object(client_mod, "EncryptedTable") as mk_encrypted:
        mk_encrypted.return_value.get_item.return_value = {"Item": {"id": "tenant-42"}}
        client_mod.retrieve_client_info("tenant-42", temp_credentials)

    mk_encrypted.return_value.get_item.assert_called_once_with(Key={"id": "tenant-42"})


def test_client_id_comes_only_from_the_mapped_event_field(client_mod):
    """API Gateway's mapping template puts the validated claim in `client_id`."""
    assert client_mod.parse_client_id({"client_id": "tenant-42"}) == "tenant-42"


def test_a_request_without_a_client_id_fails_rather_than_defaulting(client_mod):
    """No silent fallback to a default tenant, empty string, or scan-everything."""
    with pytest.raises(KeyError):
        client_mod.parse_client_id({"request_id": "abc", "source": "client-portal"})


def test_the_client_path_never_scans(client_mod):
    source = client_mod.__file__
    with open(source, encoding="utf-8") as fh:
        text = fh.read()
    assert ".scan(" not in text, "the encrypted PII table must only ever be read by key"


# ----------------------------------------------------------------------- handler

def test_handler_returns_the_decrypted_item_as_json(client_mod, temp_credentials):
    item = {"id": "tenant-42", "firstName": "Ada", "lastName": "Lovelace"}

    with patch.object(client_mod, "assume_role_in_data_account", return_value=temp_credentials), \
         patch.object(client_mod, "retrieve_client_info", return_value=item) as mk_retrieve:
        response = client_mod.lambda_handler({"client_id": "tenant-42"}, MagicMock())

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == item
    # the identifier reached the data layer unchanged
    assert mk_retrieve.call_args.args[0] == "tenant-42"
