# Secure Data Hub — a multi-account AWS architecture for sensitive client data

A serverless reference build for storing and serving client PII across **separate AWS accounts**,
so that compromising the application tier does not expose the data tier.

Two portals — a **client** portal and an **admin** portal — each front their own API Gateway REST
API behind a Cognito authorizer. Neither Lambda can reach the data directly. Both assume a role
into a separate data account via STS and operate there with temporary credentials only.

The full architecture is documented as a **31-slide deck with 7 demo videos** further down this
page. This section explains the parts that are implemented in code here, and the decisions behind
them.

---

## The four decisions worth reading

### 1. The application account holds no data access

Both Lambda handlers call `sts:AssumeRole` into a separate data account and construct a boto3
session from the returned temporary credentials. There are no long-lived keys, and the application
account's own role cannot read the table.

The IAM policies are split to match that boundary:

| Role | Account | Permitted actions |
|---|---|---|
| `...-role-sdh-app-client` | Application | CloudWatch Logs, plus `sts:AssumeRole` on **one** role ARN |
| `...-role-sdh-data` | Data | `dynamodb:GetItem`, `dynamodb:DescribeTable` on **one** table ARN |
| `...-role-sdh-app-admin` | Application | CloudWatch Logs, plus `sts:AssumeRole` on one role ARN |
| `...-role-blue-sdh-data` | Data | Scan on the summary table only |

Each is scoped to a single resource ARN rather than a wildcard. The client path can read exactly
one item type from exactly one table, and nothing else.

### 2. The tenant identifier never comes from the caller

The most common way a multi-tenant API leaks data is trusting a client-supplied ID. Here the
identifier is extracted in the **API Gateway mapping template**, from a claim the Cognito
authorizer has already validated — before the request ever reaches Lambda:

```velocity
#set($client_id = $context.authorizer.claims['custom:client_id'])

#if(!$client_id)
  #set($context.responseOverride.status = 400)
  { "message": "Missing Client Id." }
#else
  { "client_id": "$client_id", ... }
#end
```

`$context.authorizer.claims` is populated by API Gateway from the decoded and verified JWT. A
caller cannot influence it. If the claim is absent the request is rejected with a 400 at the
gateway, so the function is never invoked without a tenant identity.

Both APIs use Cognito User Pool authorizers pinned to a specific app client via
`identityValidationExpression`, rather than accepting any token the pool issued.

### 3. A subtle credentials bug in the encryption path

Client PII is encrypted at the item level in DynamoDB using the DynamoDB Encryption SDK with a
KMS customer-managed key, referenced by alias.

The non-obvious part: `AwsKmsCryptographicMaterialsProvider` takes a **`botocore.session.Session`**,
not the `boto3.Session` you just built from the assumed-role credentials. If you do not pass one
explicitly, the SDK silently falls back to the default session — which inside Lambda means the
**execution role's** credentials, not the assumed data-account role.

It does not raise. It just quietly performs KMS operations as the wrong principal, defeating the
account boundary the rest of the design exists to enforce.

```python
session = boto3.Session(
    aws_access_key_id=temp_credentials["AccessKeyId"],
    aws_secret_access_key=temp_credentials["SecretAccessKey"],
    aws_session_token=temp_credentials["SessionToken"],
    region_name=AWS_REGION,
)

# boto3.Session wraps a botocore session as `_session`; the Encryption SDK needs that one.
aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(
    key_id=KMS_KEY_ALIAS,
    botocore_session=session._session,
)
```

The reasoning is written up at length in `lambda/LambdaFunctionForBaseTable_Client.py`, including
the relevant excerpt from the SDK's own class definition.

### 4. The broad permission never touches the sensitive table

The admin portal needs to list clients, which means a `Scan` — a permission you do not want
anywhere near encrypted PII. So the data is split across two tables:

- **`ClientsBase`** — encrypted PII, `GetItem` only, one record at a time, by validated tenant claim.
- **A separate summary table** — non-sensitive fields only, which the admin path scans with
  `AttributesToGet=['id', 'firstName', 'lastName']` and `Limit=20`.

The admin role's `Scan` permission is scoped to the summary table. Even a total compromise of the
admin path cannot enumerate protected fields, because the permission does not exist on that table.

---

## What is in this repository

```
lambda/
  LambdaFunctionForBaseTable_Client.py     client path: STS → KMS-decrypted GetItem
  LambdaFunctionForSummaryTable_Admin.py   admin path: STS → scoped Scan
  IAM_policies/*.json                      4 policies, split across the trust boundary
  ddb-encryption-layer.zip                 Lambda layer: DynamoDB Encryption SDK 3.3.0,
                                           AWS Encryption SDK 4.0.3, cryptography 46.0.3, boto3 1.40.73
apigw/
  ClientApp/mapping_template.vtl           tenant identity from the validated JWT claim
  ClientApp/RESTAPIConfiguration_*.json    exported OpenAPI 3.0.1 definition
  AdminApp/RESTAPIConfiguration_*.json     exported OpenAPI 3.0.1 definition
application_webpages/
  AdminApp/                                OIDC authorization-code SPA (oidc-client-ts, no client secret)
cognito/                                   token retrieval notes
readme_images/                             the 31-slide architecture deck
```

The admin SPA runs the OIDC authorization-code flow against the Cognito Hosted UI with no client
secret, and clears cached tokens from browser storage before redirecting to Cognito's `/logout`
endpoint on sign-out.

CORS on the admin API is set to a single explicit origin with an allow-list of headers
(`Content-Type`, `Authorization`) and methods (`GET`, `OPTIONS`) — configured on both the `GET`
integration response and the `OPTIONS` mock integration, rather than left as a wildcard.

---

## Scope and honest limits

**Implemented in this repository:** the two Lambda handlers, the four IAM policies, both exported
API definitions, the VTL mapping template, the encryption layer, and the admin SPA.

**Designed and diagrammed, but not deployed as code here:** the nine-account AWS Organizations
landing zone (Management plus Prod and Dev organizational units, each holding Admin / Data /
Client / Security accounts), the Service Control Policies, IAM Identity Center permission sets,
per-account budget alerting, and the organization-wide detection pipeline — a CloudTrail
organization trail with log file integrity validation writing to a central bucket in the Security
account, per-account EventBridge routing of `AccessDenied` and `UnauthorizedOperation` events to a
Security-account bus with an SNS target, CloudWatch metric filters and alarms for service-behaviour
failures CloudTrail does not record, and GuardDuty consuming VPC Flow Logs, Route 53 resolver query
logs and CloudTrail management events across five accounts.

Those are architecture, not artifacts. They are in the slide deck below and were built by hand in
the console; there is no Terraform in this repository, and there are no automated tests. Both are
tracked as follow-up work.

The IAM policy files use `<ACCOUNT_ID>`, `<REGION>` and `<SUMMARY_TABLE_NAME>` placeholders and the
API definitions require substitution before use — hence the `REPLACE_PLACEHOLDERS` filenames.

---

## Configuration

The client Lambda expects:

| Variable | Purpose |
|---|---|
| `DATA_ACCOUNT_ROLE_ARN` | Role to assume in the data account |
| `CLIENTS_TABLE_NAME` | Encrypted base table |
| `KMS_KEY_ALIAS` | Customer-managed key alias — must keep the `alias/` prefix |
| `AWS_REGION` | Defaults to `us-east-1`; Lambda normally sets this |

The admin Lambda takes the equivalent values for the summary table.

---

## Architecture deck

The 31 slides and 7 demo videos below walk through the account topology, the request path, the IAM
trust relationships, the encryption flow, and the detection and alerting design, with recordings of
the working system.

![](readme_images/image1.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image2.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image3.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image4.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------


https://github.com/user-attachments/assets/96597fb0-4cb8-4132-a3d3-9610b06ecefa


------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image5.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image6.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------


https://github.com/user-attachments/assets/01c409a2-2f7e-47e7-ba75-7296a657f166


------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image7.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image8.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------


https://github.com/user-attachments/assets/063d46a6-f981-47c6-8927-8f3b3a91beaf


------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image9.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image10.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------


https://github.com/user-attachments/assets/85999e9c-fae4-48b6-83e0-98ffd51decbe


------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image11.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image12.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image13.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image14.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image15.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image16.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image17.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image18.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image19.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------


https://github.com/user-attachments/assets/1adf84b5-c427-4363-8e3d-d801bc0f36e2


------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image20.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image21.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------


https://github.com/user-attachments/assets/9d945449-d18f-4fc7-91b8-010bf45d0a38


------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image22.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image23.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image24.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------


https://github.com/user-attachments/assets/23eeb829-3069-46bd-81be-3b3e172e0f2e


------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image25.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image26.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image27.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image28.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image29.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image30.png)
------------------------------------------------------------------------------------------------------------------------------------------------------------------
![](readme_images/image31.png)

---

## Planned: Infrastructure as Code

The deck's final section is the Terraform and GitHub Actions plan for provisioning the above
rather than clicking it. It is design work, not yet built — included here so the intended end
state is on the record.

![](readme_images/image32.png)
