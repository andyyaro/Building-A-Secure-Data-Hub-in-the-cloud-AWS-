# Secure Data Hub launch film: every claim and its source

Every name and figure in the film comes from this repository as it stood on `main` at `c197b22`.
Paths are from the repository root. Times are film seconds.

## Narration

| Time | Line | Source |
|---|---|---|
| 0.6 | One stolen credential. | The hook. In the picture it is a red key; no real credential is shown |
| 2.4 | In most apps, that opens every client's record. | The single-account case the design exists to avoid ([README](../../README.md), opening paragraph). The nine records are the mark's nine squares, not data |
| 6.3 | Here, breaking into the app doesn't expose the data. | README: "compromising the application tier does not expose the data tier" |
| 12.1 | This is Secure Data Hub. | The project's name and logo (`docs/assets/brand/`) |
| 14.3 | A multi-account AWS architecture for sensitive client data. | The README's title |
| 20.2 | The app account holds no data access. | README, decision 1; `lambda/IAM_policies/LambdaFunctionForBaseTable_Client-role-sdh-app-client.json` (CloudWatch Logs and `sts:AssumeRole` on one role ARN, no DynamoDB) |
| 22.7 | To read one record, it assumes a role in a separate data account, with temporary credentials. | `lambda/LambdaFunctionForBaseTable_Client.py`: `assume_role_in_data_account()`, then a `boto3.Session` built from the returned `AccessKeyId`, `SecretAccessKey` and `SessionToken` |
| 29.7 | The tenant ID never comes from the caller. | README, decision 2; `apigw/ClientApp/mapping_template.vtl` |
| 32.6 | The gateway takes it from a verified token, before any code runs. | `mapping_template.vtl`: `#set($client_id = $context.authorizer.claims['custom:client_id'])`, filled by the Cognito authorizer before the Lambda is called |
| 39.3 | Each record is encrypted with a customer-managed key, used only as the data account. | README, decision 3; `LambdaFunctionForBaseTable_Client.py`: `AwsKmsCryptographicMaterialsProvider(key_id=KMS_KEY_ALIAS, botocore_session=session._session)`, then `EncryptedTable.get_item` |
| 45.0 | And the admin's broad permission never touches the sensitive table. | README, decision 4; `lambda/LambdaFunctionForSummaryTable_Admin.py`; `lambda/IAM_policies/LambdaFunctionForSummaryTable_Admin-role-blue-sdh-data.json` (Scan on the summary table only) |
| 49.6 | Fifty-one tests pin these boundaries in place. | `pytest -q` at `c197b22`: 51 passed, 1 xfailed. Run again for this commit on 2026-11-02: the same |
| 55.2 | Secure Data Hub. | The end card |

## On screen

| Scene | Claim | Source |
|---|---|---|
| Open | "In most apps · one account holds it all", "9 of 9 client records exposed" | An illustration of the single-account case, not a measurement |
| Open | "Here · the data lives in its own account", "0 of 9 client records exposed" | The design: the data account is reached only by assuming a role (decision 1) |
| Title | API Gateway · Cognito · Lambda · STS · DynamoDB · KMS · Terraform | `apigw/`, `cognito/`, `lambda/`, `terraform/` |
| Decision 1 | "No direct read" between the Client Lambda and ClientsBase | `...-role-sdh-app-client.json` has no DynamoDB action; `tests/test_iam_policies.py::test_client_app_account_role_cannot_touch_data_directly` |
| Decision 1 | "sts:AssumeRole · on one role ARN" | `...-role-sdh-app-client.json`; `test_client_app_role_can_assume_exactly_one_role` |
| Decision 1 | "GetItem, DescribeTable · on one table" | `lambda/IAM_policies/LambdaFunctionForBaseTable_Client-role-sdh-data.json` (`table/ClientsBase`) |
| Decision 1 | "Temporary credentials: AccessKeyId, SecretAccessKey, SessionToken · no long-lived keys" | `LambdaFunctionForBaseTable_Client.py`; `tests/test_client_path.py::test_no_long_lived_credentials_are_read_from_the_environment` |
| Decision 2 | The caller's request: `GET /client/profile`, `Authorization: Bearer token`, `client_id: 9ab3f1`, struck out and "ignored" | The path is the test event's (`lambda/Test_Event_LambdaFunctionForBaseTable_Client.json`). `9ab3f1` stands for any ID a caller might send; the template never reads one (`tests/test_api_gateway_config.py::test_tenant_id_is_never_read_from_caller_controlled_input`) |
| Decision 2 | "Verified token · Cognito", `custom:client_id` = `25xwe2` | The claim the template reads; `25xwe2` is the test event's `client_id` |
| Decision 2 | "API Gateway · Cognito authorizer" | Both exported API definitions in `apigw/`; `test_api_uses_a_cognito_user_pool_authorizer` |
| Decision 2 | `client_id ← claims['custom:client_id']`, "event client_id: 25xwe2" | `mapping_template.vtl`; the test event |
| Decision 2 | "400 · Missing Client Id.", "never invoked" | `mapping_template.vtl` (`responseOverride.status = 400`, `"Missing Client Id."`); README: "the function is never invoked without a tenant identity"; `test_a_missing_claim_is_rejected_at_the_gateway` |
| Decision 3 | One ClientsBase item: `id` 25xwe2, `firstName` Ada, `lastName` Lovelace, `signature`; locked, then "Decrypted in the Lambda, as the data role" | An illustration: the ID is the test event's and the name is the tests' sample item (`tests/test_client_path.py`, `tests/test_admin_path.py`). The signature row stands for the signature the DynamoDB Encryption SDK keeps with each item it encrypts |
| Decision 3 | "KMS key · customer managed, by alias" | `KMS_KEY_ALIAS` in `LambdaFunctionForBaseTable_Client.py`; `test_kms_key_is_referenced_by_alias_not_raw_key_id` |
| Decision 3 | "Lambda's own role · the SDK's silent default", refused | README, decision 3: without `botocore_session` the SDK falls back to the execution role's credentials; `test_kms_provider_receives_the_assumed_role_session_not_the_default` |
| Decision 4 | "Admin Lambda · its own data role", `dynamodb:Scan` | `LambdaFunctionForSummaryTable_Admin.py`; `tests/test_admin_path.py::test_assumes_the_summary_role_not_the_base_table_role` |
| Decision 4 | "ClientsSummary · id, firstName, lastName", "Scan · limit 20" | `LambdaFunctionForSummaryTable_Admin.py`: `table.scan(AttributesToGet=['id', 'firstName', 'lastName'], Limit=20)`; `test_scan_projects_only_non_pii_attributes`, `test_scan_is_bounded` |
| Decision 4 | "ClientsBase · encrypted PII, GetItem only", "no grant on this table" | `...-role-blue-sdh-data.json` names only the summary table; `test_admin_path_never_references_the_encrypted_base_table` |
| Proof | 51 | `pytest -q`: 51 passed, 1 xfailed |
| Proof | One role to assume, through STS | `test_assumes_the_configured_data_account_role`, `test_client_app_role_can_assume_exactly_one_role` |
| Proof | No long-lived keys in the environment | `test_no_long_lived_credentials_are_read_from_the_environment` |
| Proof | Tenant ID only from the token's claim | `test_tenant_id_is_read_from_the_authorizer_claims`, `test_client_id_comes_only_from_the_mapped_event_field` |
| Proof | KMS runs as the assumed data role | `test_kms_provider_receives_the_assumed_role_session_not_the_default` |
| Proof | Admin Scan: three fields, 20 at most | `test_scan_projects_only_non_pii_attributes`, `test_scan_is_bounded` |
| Proof | No wildcard actions, no open endpoints | `test_no_statement_allows_every_action`, `test_no_service_wide_wildcards_on_data_actions`, `test_no_endpoint_is_left_unauthorized` |
| Proof | "1 known export defect, pinned as xfail." | `tests/test_iam_policies.py::test_admin_app_account_role_cannot_touch_data_directly` (strict xfail); README's note on the admin path; `docs/FIX_ADMIN_ROLE_POLICY.md` |
| Proof | "Terraform for both accounts, validated in CI." | `terraform/app_account.tf`, `terraform/data_account.tf`; the `terraform` job in `.github/workflows/ci.yml` (`fmt -check`, `init -backend=false`, `validate`) |
| End card | Breaking into the app doesn't expose the data. · github.com/andyyaro/Building-A-Secure-Data-Hub-in-the-cloud-AWS- | The film's line; the repository |

## Left out on purpose

The nine-account AWS Organizations landing zone in the architecture deck is a design, not code in
this repository (README, "Scope and honest limits"), so the film does not show it.
