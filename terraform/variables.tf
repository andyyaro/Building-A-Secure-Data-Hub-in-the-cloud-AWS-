variable "region" {
  description = "AWS region for every resource in this configuration."
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Name prefix applied to every resource."
  type        = string
  default     = "sdh"
}

variable "data_account_deploy_role_arn" {
  description = <<-EOT
    Role Terraform assumes to create resources in the DATA account. The data
    account is a separate AWS account by design; this is the only way this
    configuration reaches into it.
  EOT
  type        = string
}

variable "data_account_id" {
  description = "Account id of the data account. Used to build trust policies."
  type        = string

  validation {
    condition     = can(regex("^[0-9]{12}$", var.data_account_id))
    error_message = "data_account_id must be a 12-digit AWS account id."
  }
}

variable "app_account_id" {
  description = "Account id of the application account."
  type        = string

  validation {
    condition     = can(regex("^[0-9]{12}$", var.app_account_id))
    error_message = "app_account_id must be a 12-digit AWS account id."
  }
}

variable "client_portal_origin" {
  description = <<-EOT
    Exact origin allowed to call the admin API. A single origin, never "*" - a
    wildcard would let any site call the API with a signed-in user's token.
  EOT
  type        = string

  validation {
    condition     = var.client_portal_origin != "*"
    error_message = "A wildcard CORS origin is not permitted on an authenticated API."
  }
}

variable "admin_list_page_size" {
  description = "Upper bound on items returned by the admin list view."
  type        = number
  default     = 20

  validation {
    condition     = var.admin_list_page_size > 0 && var.admin_list_page_size <= 100
    error_message = "Keep the admin list view bounded; 1-100."
  }
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention. Never 0 (never expire)."
  type        = number
  default     = 30

  validation {
    condition     = var.log_retention_days > 0
    error_message = "Set an explicit retention period rather than keeping logs forever."
  }
}
