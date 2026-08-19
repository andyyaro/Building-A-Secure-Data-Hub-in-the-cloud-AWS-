"""Admin path: the broad Scan permission must never reach encrypted PII.

The admin portal lists clients, which needs a Scan. Scan is exactly the permission
you do not want near the encrypted base table, so the data is split in two and the
admin role is scoped to the summary table only. These tests pin that split.
"""

import importlib
from unittest.mock import MagicMock, patch

import pytest

NON_PII_ATTRIBUTES = {"id", "firstName", "lastName"}


@pytest.fixture
def admin_mod():
    mod = importlib.import_module("LambdaFunctionForSummaryTable_Admin")
    return importlib.reload(mod)


def test_assumes_the_summary_role_not_the_base_table_role(admin_mod, temp_credentials):
    """A separate role from the client path, with a narrower grant."""
    sts = MagicMock()
    sts.assume_role.return_value = {"Credentials": temp_credentials}

    with patch.object(admin_mod.boto3, "client", return_value=sts):
        admin_mod.assume_role_in_data_account()

    assert sts.assume_role.call_args.kwargs["RoleArn"] == admin_mod.DATA_ACCOUNT_ROLE_BLUE_ARN


def test_scan_targets_the_summary_table(admin_mod, temp_credentials):
    session = MagicMock()
    table = session.resource.return_value.Table.return_value
    table.scan.return_value = {"Count": 0, "Items": []}

    with patch.object(admin_mod.boto3, "Session", return_value=session):
        admin_mod.retrieve_client_info(temp_credentials)

    session.resource.return_value.Table.assert_called_once_with(
        admin_mod.CLIENTS_SUMMARY_TABLE_NAME
    )
    assert admin_mod.CLIENTS_SUMMARY_TABLE_NAME != "ClientsBase"


def test_scan_projects_only_non_pii_attributes(admin_mod, temp_credentials):
    """Data minimisation: the admin list view cannot pull protected fields."""
    session = MagicMock()
    table = session.resource.return_value.Table.return_value
    table.scan.return_value = {"Count": 0, "Items": []}

    with patch.object(admin_mod.boto3, "Session", return_value=session):
        admin_mod.retrieve_client_info(temp_credentials)

    requested = set(table.scan.call_args.kwargs["AttributesToGet"])
    assert requested == NON_PII_ATTRIBUTES, (
        "widening this projection is how PII leaks into the admin view"
    )


def test_scan_is_bounded(admin_mod, temp_credentials):
    """An unbounded scan is both a cost and an exposure problem."""
    session = MagicMock()
    table = session.resource.return_value.Table.return_value
    table.scan.return_value = {"Count": 0, "Items": []}

    with patch.object(admin_mod.boto3, "Session", return_value=session):
        admin_mod.retrieve_client_info(temp_credentials)

    assert table.scan.call_args.kwargs["Limit"] == 20


def test_admin_session_uses_the_temporary_credentials(admin_mod, temp_credentials):
    session = MagicMock()
    session.resource.return_value.Table.return_value.scan.return_value = {
        "Count": 0, "Items": []
    }

    with patch.object(admin_mod.boto3, "Session", return_value=session) as mk_session:
        admin_mod.retrieve_client_info(temp_credentials)

    kwargs = mk_session.call_args.kwargs
    assert kwargs["aws_access_key_id"] == temp_credentials["AccessKeyId"]
    assert kwargs["aws_secret_access_key"] == temp_credentials["SecretAccessKey"]
    assert kwargs["aws_session_token"] == temp_credentials["SessionToken"]


def test_admin_path_never_references_the_encrypted_base_table(admin_mod):
    with open(admin_mod.__file__, encoding="utf-8") as fh:
        text = fh.read()
    assert "ClientsBase" not in text
    assert "EncryptedTable" not in text, (
        "the admin path has no business decrypting anything"
    )


def test_handler_reports_count_and_items(admin_mod, temp_credentials):
    items = [{"id": "a", "firstName": "Ada", "lastName": "Lovelace"}]

    with patch.object(admin_mod, "assume_role_in_data_account", return_value=temp_credentials), \
         patch.object(admin_mod, "retrieve_client_info", return_value=(items, 1)):
        response = admin_mod.lambda_handler({}, MagicMock())

    assert response["statusCode"] == 200
    assert response["count"] == 1
