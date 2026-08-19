# ---------------------------------------------------------------------------
# APPLICATION ACCOUNT
#
# The two Lambda functions and the roles they run as. Neither role is granted
# any DynamoDB or KMS permission: the only way either function reaches data is
# by assuming a role in the data account.
#
# This is the property the committed admin policy currently violates - see the
# strict xfail in tests/test_iam_policies.py. This configuration expresses the
# intended shape for both paths.
# ---------------------------------------------------------------------------

data "aws_iam_policy_document" "lambda_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# ------------------------------------------------------------- client function

resource "aws_iam_role" "client_lambda" {
  name               = "${var.project}-app-client-lambda"
  description        = "Execution role for the client portal function. Logs, and one AssumeRole."
  assume_role_policy = data.aws_iam_policy_document.lambda_trust.json
}

data "aws_iam_policy_document" "client_lambda" {
  statement {
    sid       = "WriteOwnLogs"
    effect    = "Allow"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.client.arn}:*"]
  }

  statement {
    sid       = "AssumeDataAccountReadRole"
    effect    = "Allow"
    actions   = ["sts:AssumeRole"]
    resources = [aws_iam_role.data_client_read.arn] # exactly one trust edge
  }
}

resource "aws_iam_role_policy" "client_lambda" {
  name   = "${var.project}-app-client-lambda"
  role   = aws_iam_role.client_lambda.id
  policy = data.aws_iam_policy_document.client_lambda.json
}

resource "aws_cloudwatch_log_group" "client" {
  name              = "/aws/lambda/${var.project}-client-profile"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "client" {
  function_name = "${var.project}-client-profile"
  role          = aws_iam_role.client_lambda.arn
  handler       = "LambdaFunctionForBaseTable_Client.lambda_handler"
  runtime       = "python3.12"
  timeout       = 10
  memory_size   = 256

  filename         = data.archive_file.client.output_path
  source_code_hash = data.archive_file.client.output_base64sha256

  # The DynamoDB Encryption SDK and its transitive cryptography wheels are too
  # large for an inline deployment package, hence the layer.
  layers = [aws_lambda_layer_version.ddb_encryption.arn]

  environment {
    variables = {
      DATA_ACCOUNT_ROLE_ARN = aws_iam_role.data_client_read.arn
      CLIENTS_TABLE_NAME    = aws_dynamodb_table.clients_base.name
      KMS_KEY_ALIAS         = aws_kms_alias.clients.name
    }
  }

  depends_on = [aws_cloudwatch_log_group.client]
}

# -------------------------------------------------------------- admin function

resource "aws_iam_role" "admin_lambda" {
  name               = "${var.project}-app-admin-lambda"
  description        = "Execution role for the admin portal function. Logs, and one AssumeRole."
  assume_role_policy = data.aws_iam_policy_document.lambda_trust.json
}

data "aws_iam_policy_document" "admin_lambda" {
  statement {
    sid       = "WriteOwnLogs"
    effect    = "Allow"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.admin.arn}:*"]
  }

  statement {
    sid       = "AssumeDataAccountSummaryRole"
    effect    = "Allow"
    actions   = ["sts:AssumeRole"]
    resources = [aws_iam_role.data_admin_summary.arn]
  }

  # Note the absence of any dynamodb:* statement here. The admin function's
  # Scan permission lives on the role it assumes in the data account, not on
  # its own execution role.
}

resource "aws_iam_role_policy" "admin_lambda" {
  name   = "${var.project}-app-admin-lambda"
  role   = aws_iam_role.admin_lambda.id
  policy = data.aws_iam_policy_document.admin_lambda.json
}

resource "aws_cloudwatch_log_group" "admin" {
  name              = "/aws/lambda/${var.project}-admin-list"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "admin" {
  function_name = "${var.project}-admin-list"
  role          = aws_iam_role.admin_lambda.arn
  handler       = "LambdaFunctionForSummaryTable_Admin.lambda_handler"
  runtime       = "python3.12"
  timeout       = 10
  memory_size   = 256

  filename         = data.archive_file.admin.output_path
  source_code_hash = data.archive_file.admin.output_base64sha256

  environment {
    variables = {
      DATA_ACCOUNT_ROLE_BLUE_ARN = aws_iam_role.data_admin_summary.arn
      CLIENTS_SUMMARY_TABLE_NAME = aws_dynamodb_table.clients_summary.name
    }
  }

  depends_on = [aws_cloudwatch_log_group.admin]
}

# ----------------------------------------------------------------- packaging

data "archive_file" "client" {
  type        = "zip"
  source_file = "${path.module}/../lambda/LambdaFunctionForBaseTable_Client.py"
  output_path = "${path.module}/.build/client.zip"
}

data "archive_file" "admin" {
  type        = "zip"
  source_file = "${path.module}/../lambda/LambdaFunctionForSummaryTable_Admin.py"
  output_path = "${path.module}/.build/admin.zip"
}

resource "aws_lambda_layer_version" "ddb_encryption" {
  layer_name          = "${var.project}-ddb-encryption"
  description         = "DynamoDB Encryption SDK, AWS Encryption SDK, cryptography, boto3"
  filename            = "${path.module}/../lambda/ddb-encryption-layer.zip"
  compatible_runtimes = ["python3.12"]
}
