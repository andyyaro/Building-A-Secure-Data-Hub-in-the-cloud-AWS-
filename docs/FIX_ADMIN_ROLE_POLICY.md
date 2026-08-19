# Runbook: correct the admin execution-role policy

**Status:** open · pinned by a `strict=True` xfail in `tests/test_iam_policies.py`

## The problem

`lambda/IAM_policies/LambdaFunctionForSummaryTable_Admin-role-sdh-app-admin.json` is the policy
attached to the **admin Lambda's execution role**, in the application account. It is a
near-duplicate of the *data-account* policy sitting beside it:

```json
{ "Sid": "DDB_Scan_SummaryTable",
  "Effect": "Allow",
  "Action": "dynamodb:Scan",
  "Resource": "arn:aws:dynamodb:<REGION>:<ACCOUNT_ID>:table/<SUMMARY_TABLE_NAME>" }
```

Two things follow from that.

**It grants a permission the function does not use.** `LambdaFunctionForSummaryTable_Admin.py`
never calls DynamoDB with its own credentials. It assumes a role in the data account and scans
with the temporary credentials that come back. This grant is dead weight that also punches a hole
in the account boundary the client path enforces.

**It omits the permission the function does need.** The handler calls:

```python
sts_client.assume_role(RoleArn=DATA_ACCOUNT_ROLE_BLUE_ARN, RoleSessionName="AssumeRoleInDataAccount")
```

There is no `sts:AssumeRole` statement anywhere in the policy. As committed, that call fails with
`AccessDenied`.

Compare the client-side equivalent, `...-role-sdh-app-client.json`, which is correct: CloudWatch
Logs plus `sts:AssumeRole` on exactly one role ARN, and no data permission at all.

## The correction

Replace the policy contents with:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Logs_CreateLogGroup",
      "Effect": "Allow",
      "Action": "logs:CreateLogGroup",
      "Resource": "arn:aws:logs:<REGION>:<ACCOUNT_ID>:*"
    },
    {
      "Sid": "Logs_WriteLambdaLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": [
        "arn:aws:logs:<REGION>:<ACCOUNT_ID>:log-group:/aws/lambda/LambdaFunctionForSummaryTable_Admin:*"
      ]
    },
    {
      "Sid": "AssumeDataAccountSummaryRole",
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "ROLE_ARN_IN_DATA_ACCOUNT"
    }
  ]
}
```

The `dynamodb:Scan` grant does not move to the execution role — it already exists on the
data-account role in `...-role-blue-sdh-data.json`, which is where it belongs.

## Applying it

Either apply the Terraform, which already expresses this shape:

```bash
cd terraform
terraform plan    # aws_iam_role_policy.admin_lambda is the relevant resource
terraform apply
```

or patch the live policy directly:

```bash
# 1. find the policy attached to the admin execution role
aws iam list-attached-role-policies --role-name <ADMIN_EXECUTION_ROLE_NAME>

# 2. create a new default version from the corrected document above
aws iam create-policy-version \
  --policy-arn arn:aws:iam::<APP_ACCOUNT_ID>:policy/<POLICY_NAME> \
  --policy-document file://corrected.json \
  --set-as-default

# 3. confirm the data-account role trusts the admin execution role
aws iam get-role --role-name <DATA_SUMMARY_ROLE_NAME> \
  --query 'Role.AssumeRolePolicyDocument'
```

Then re-export the policy over the file in `lambda/IAM_policies/`, with the account id replaced by
`<ACCOUNT_ID>` as the other three files already do.

## Verifying

```bash
pytest tests/test_iam_policies.py -q
```

`test_admin_app_account_role_cannot_touch_data_directly` is marked `xfail(strict=True)`. Once the
policy is corrected the test will **pass**, and because the mark is strict, pytest reports an
unexpected pass as a **failure**. That is intentional: it forces the mark to be removed rather
than left behind as stale scaffolding.

Then delete the `@pytest.mark.xfail` block above that test, and the note in the README under
"The four decisions worth reading".
