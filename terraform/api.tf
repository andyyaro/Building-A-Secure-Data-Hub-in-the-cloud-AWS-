# ---------------------------------------------------------------------------
# API LAYER
#
# Two REST APIs, each behind a Cognito authorizer pinned to a specific app
# client. The client API's mapping template is the file already committed at
# apigw/ClientApp/mapping_template.vtl - it is read from disk rather than
# duplicated here, so the deployed template and the reviewed one cannot drift.
# ---------------------------------------------------------------------------

resource "aws_cognito_user_pool" "clients" {
  name = "${var.project}-clients"

  password_policy {
    minimum_length                   = 12
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = true
    temporary_password_validity_days = 3
  }

  # The tenant identifier the mapping template reads. Immutable: a user whose
  # client_id could change is a user who can read another tenant's record.
  schema {
    name                     = "client_id"
    attribute_data_type      = "String"
    mutable                  = false
    developer_only_attribute = false

    string_attribute_constraints {
      min_length = 1
      max_length = 64
    }
  }

  mfa_configuration = "OPTIONAL"

  software_token_mfa_configuration {
    enabled = true
  }
}

resource "aws_cognito_user_pool_client" "client_portal" {
  name         = "${var.project}-client-portal"
  user_pool_id = aws_cognito_user_pool.clients.id

  # Public SPA: no secret, authorization-code flow with PKCE.
  generate_secret                      = false
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["openid", "email"]
  supported_identity_providers         = ["COGNITO"]

  callback_urls = ["${var.client_portal_origin}/callback.html"]
  logout_urls   = [var.client_portal_origin]

  # Implicit flow is not offered at all, so a token cannot arrive in a URL fragment.
  explicit_auth_flows = ["ALLOW_USER_SRP_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"]

  access_token_validity  = 1
  id_token_validity      = 1
  refresh_token_validity = 1

  token_validity_units {
    access_token  = "hours"
    id_token      = "hours"
    refresh_token = "days"
  }
}

# -------------------------------------------------------------------- client API

resource "aws_api_gateway_rest_api" "client" {
  name        = "${var.project}-client-api"
  description = "Client portal. Returns exactly one record, chosen by a validated token claim."

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_authorizer" "client" {
  name          = "${var.project}-client-pool"
  rest_api_id   = aws_api_gateway_rest_api.client.id
  type          = "COGNITO_USER_POOLS"
  provider_arns = [aws_cognito_user_pool.clients.arn]

  # Pins acceptance to one app client rather than any token the pool issued.
  identity_validation_expression = "^${aws_cognito_user_pool_client.client_portal.id}$"
  identity_source                = "method.request.header.Authorization"
}

resource "aws_api_gateway_resource" "client_root" {
  rest_api_id = aws_api_gateway_rest_api.client.id
  parent_id   = aws_api_gateway_rest_api.client.root_resource_id
  path_part   = "client"
}

resource "aws_api_gateway_resource" "client_profile" {
  rest_api_id = aws_api_gateway_rest_api.client.id
  parent_id   = aws_api_gateway_resource.client_root.id
  path_part   = "profile"
}

resource "aws_api_gateway_method" "client_get" {
  rest_api_id   = aws_api_gateway_rest_api.client.id
  resource_id   = aws_api_gateway_resource.client_profile.id
  http_method   = "GET"
  authorization = "COGNITO_USER_POOLS"
  authorizer_id = aws_api_gateway_authorizer.client.id
}

resource "aws_api_gateway_integration" "client_get" {
  rest_api_id = aws_api_gateway_rest_api.client.id
  resource_id = aws_api_gateway_resource.client_profile.id
  http_method = aws_api_gateway_method.client_get.http_method

  type                    = "AWS"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.client.invoke_arn
  passthrough_behavior    = "NEVER" # no template, no request

  request_templates = {
    # The reviewed template, read from the repository. The tenant identifier is
    # taken from $context.authorizer.claims and never from caller input.
    "application/json" = file("${path.module}/../apigw/ClientApp/mapping_template.vtl")
  }
}

resource "aws_api_gateway_method_response" "client_get_200" {
  rest_api_id = aws_api_gateway_rest_api.client.id
  resource_id = aws_api_gateway_resource.client_profile.id
  http_method = aws_api_gateway_method.client_get.http_method
  status_code = "200"
}

resource "aws_api_gateway_integration_response" "client_get_200" {
  rest_api_id = aws_api_gateway_rest_api.client.id
  resource_id = aws_api_gateway_resource.client_profile.id
  http_method = aws_api_gateway_method.client_get.http_method
  status_code = aws_api_gateway_method_response.client_get_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = "'${var.client_portal_origin}'"
  }

  depends_on = [aws_api_gateway_integration.client_get]
}

resource "aws_lambda_permission" "client_api" {
  statement_id  = "AllowClientApiInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.client.function_name
  principal     = "apigateway.amazonaws.com"

  # Scoped to this API and this method, not to API Gateway generally.
  source_arn = "${aws_api_gateway_rest_api.client.execution_arn}/*/GET/client/profile"
}

resource "aws_api_gateway_deployment" "client" {
  rest_api_id = aws_api_gateway_rest_api.client.id

  triggers = {
    redeploy = sha1(jsonencode([
      aws_api_gateway_resource.client_profile.id,
      aws_api_gateway_method.client_get.id,
      aws_api_gateway_integration.client_get.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "client" {
  rest_api_id          = aws_api_gateway_rest_api.client.id
  deployment_id        = aws_api_gateway_deployment.client.id
  stage_name           = "prod"
  xray_tracing_enabled = true
}

resource "aws_api_gateway_method_settings" "client" {
  rest_api_id = aws_api_gateway_rest_api.client.id
  stage_name  = aws_api_gateway_stage.client.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "ERROR"

    # A tenant identifier in an access log is still a tenant identifier.
    data_trace_enabled = false

    throttling_rate_limit  = 50
    throttling_burst_limit = 100
  }
}
