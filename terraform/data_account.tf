# ---------------------------------------------------------------------------
# DATA ACCOUNT
#
# The encrypted client table, the KMS key that protects it, the low-sensitivity
# summary table, and the two roles the application account is allowed to assume.
# Nothing here trusts the application account beyond those two named roles.
# ---------------------------------------------------------------------------

resource "aws_kms_key" "clients" {
  provider = aws.data

  description             = "Item-level encryption for ${var.project} client PII"
  enable_key_rotation     = true
  deletion_window_in_days = 30
}

resource "aws_kms_alias" "clients" {
  provider = aws.data

  # The handlers reference the key by alias, so the key can be rotated or
  # replaced without a code change.
  name          = "alias/${var.project}-clients-base"
  target_key_id = aws_kms_key.clients.key_id
}

# The PII table. Reachable by primary key only - see the IAM policy below,
# which grants GetItem and deliberately not Scan or Query.
resource "aws_dynamodb_table" "clients_base" {
  provider = aws.data

  name         = "${var.project}-ClientsBase"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  # Belt and braces alongside the client-side encryption the handler performs:
  # this protects the storage layer, the Encryption SDK protects the item.
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.clients.arn
  }

  point_in_time_recovery {
    enabled = true
  }

  deletion_protection_enabled = true
}

# The summary table exists so the admin list view never needs Scan on the table
# above. It holds no protected fields.
resource "aws_dynamodb_table" "clients_summary" {
  provider = aws.data

  name         = "${var.project}-ClientsSummary"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }
}

# --------------------------------------------------------------- trust policies

# Only these two specific application-account roles may assume into data. Not the
# account root, and not a wildcard principal.
data "aws_iam_policy_document" "trust_client_lambda" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.client_lambda.arn]
    }
  }
}

data "aws_iam_policy_document" "trust_admin_lambda" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.admin_lambda.arn]
    }
  }
}

# ------------------------------------------------------------------ data roles

resource "aws_iam_role" "data_client_read" {
  provider = aws.data

  name               = "${var.project}-data-client-read"
  description        = "Assumed by the client Lambda. Reads one item by key from the encrypted table."
  assume_role_policy = data.aws_iam_policy_document.trust_client_lambda.json
}

data "aws_iam_policy_document" "data_client_read" {
  statement {
    sid    = "ReadOneClientByKey"
    effect = "Allow"

    # GetItem only. Adding Scan or Query here would make the encrypted table
    # enumerable and defeat the two-table split.
    actions = [
      "dynamodb:GetItem",
      "dynamodb:DescribeTable",
    ]

    resources = [aws_dynamodb_table.clients_base.arn]
  }

  statement {
    sid    = "DecryptClientItems"
    effect = "Allow"

    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
    ]

    resources = [aws_kms_key.clients.arn]

    # The key may only be used for DynamoDB, by this account.
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["dynamodb.${var.region}.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "data_client_read" {
  provider = aws.data

  name   = "${var.project}-data-client-read"
  role   = aws_iam_role.data_client_read.id
  policy = data.aws_iam_policy_document.data_client_read.json
}

resource "aws_iam_role" "data_admin_summary" {
  provider = aws.data

  name               = "${var.project}-data-admin-summary"
  description        = "Assumed by the admin Lambda. Scans the summary table only."
  assume_role_policy = data.aws_iam_policy_document.trust_admin_lambda.json
}

data "aws_iam_policy_document" "data_admin_summary" {
  statement {
    sid    = "ScanSummaryTableOnly"
    effect = "Allow"

    actions = ["dynamodb:Scan"]

    # Scoped to the summary table. This grant must never name clients_base.
    resources = [aws_dynamodb_table.clients_summary.arn]
  }
}

resource "aws_iam_role_policy" "data_admin_summary" {
  provider = aws.data

  name   = "${var.project}-data-admin-summary"
  role   = aws_iam_role.data_admin_summary.id
  policy = data.aws_iam_policy_document.data_admin_summary.json
}
