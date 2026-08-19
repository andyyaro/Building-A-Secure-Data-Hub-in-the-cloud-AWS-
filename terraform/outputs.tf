output "client_api_invoke_url" {
  description = "Base URL of the client portal API."
  value       = aws_api_gateway_stage.client.invoke_url
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.clients.id
}

output "cognito_app_client_id" {
  description = "The app client the authorizer is pinned to."
  value       = aws_cognito_user_pool_client.client_portal.id
}

output "data_client_read_role_arn" {
  description = "Role the client function assumes to reach the encrypted table."
  value       = aws_iam_role.data_client_read.arn
}

output "data_admin_summary_role_arn" {
  description = "Role the admin function assumes to scan the summary table."
  value       = aws_iam_role.data_admin_summary.arn
}

output "kms_key_alias" {
  value = aws_kms_alias.clients.name
}
