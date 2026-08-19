"""The API layer: tenant identity from a validated claim, and no permissive CORS.

The mapping template is where multi-tenant isolation is actually enforced. If the
tenant identifier ever comes from caller-controlled input instead of the authorizer's
validated claims, every downstream control is moot.
"""

import json

import pytest

VTL = "apigw/ClientApp/mapping_template.vtl"
CLIENT_API = "apigw/ClientApp/RESTAPIConfiguration_REPLACE_PLACEHOLDERS.json"
ADMIN_API = "apigw/AdminApp/RESTAPIConfiguration_REPLACE_PLACEHOLDERS.json"


@pytest.fixture
def vtl(repo_root):
    return (repo_root / VTL).read_text()


# ------------------------------------------------------------------ mapping template

def test_tenant_id_is_read_from_the_authorizer_claims(vtl):
    assert "$context.authorizer.claims['custom:client_id']" in vtl


def test_tenant_id_is_never_read_from_caller_controlled_input(vtl):
    """These are all attacker-controlled. None may feed the tenant identifier."""
    for source in (
        "$input.params",
        "$input.path",
        "$input.json",
        "$input.body",
        "$context.requestOverride",
        "method.request.querystring",
        "method.request.header",
        "method.request.path",
    ):
        assert source not in vtl, (
            f"tenant identity must not derive from {source} -- that is the IDOR"
        )


def test_a_missing_claim_is_rejected_at_the_gateway(vtl):
    """Reject before invoking Lambda, rather than letting the function decide."""
    assert "#if(!$client_id)" in vtl
    assert "$context.responseOverride.status = 400" in vtl


def test_the_request_is_only_built_when_a_claim_is_present(vtl):
    """The #else branch is what constructs the event; there is no fallthrough."""
    assert "#else" in vtl and "#end" in vtl
    guard = vtl.index("#if(!$client_id)")
    build = vtl.index('"client_id": "$client_id"')
    assert guard < build, "the payload must be built inside the guarded branch"


# --------------------------------------------------------------------- authorizers

@pytest.mark.parametrize("path", [CLIENT_API, ADMIN_API])
def test_api_uses_a_cognito_user_pool_authorizer(repo_root, path):
    spec = json.loads((repo_root / path).read_text())
    blob = json.dumps(spec)
    assert "cognito_user_pools" in blob, f"{path}: no Cognito authorizer configured"


@pytest.mark.parametrize("path", [CLIENT_API, ADMIN_API])
def test_authorizer_is_pinned_to_a_specific_app_client(repo_root, path):
    """Without identityValidationExpression any token the pool issued is accepted."""
    blob = json.dumps(json.loads((repo_root / path).read_text()))
    assert "identityValidationExpression" in blob, (
        f"{path}: authorizer accepts any token from the pool"
    )


@pytest.mark.parametrize("path", [CLIENT_API, ADMIN_API])
def test_no_endpoint_is_left_unauthorized(repo_root, path):
    """Every method except the CORS preflight must carry a security requirement."""
    spec = json.loads((repo_root / path).read_text())
    for route, methods in spec.get("paths", {}).items():
        for verb, operation in methods.items():
            if verb.lower() == "options":
                continue  # preflight is a mock integration and carries no data
            assert operation.get("security"), f"{path}: {verb.upper()} {route} is unauthenticated"


# --------------------------------------------------------------------------- CORS

def test_admin_api_does_not_allow_every_origin(repo_root):
    blob = (repo_root / ADMIN_API).read_text()
    assert "'*'" not in blob.replace("Access-Control-Allow-Headers", ""), (
        "a wildcard origin would let any site call the admin API with a user's token"
    )
