terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Two providers, because this architecture is two accounts. Everything the
# application tier owns is created by `aws`; everything holding client data is
# created by `aws.data`. Keeping them as separate provider configurations means
# the split is enforced by the code rather than remembered by the operator.

provider "aws" {
  region = var.region
  alias  = "app"
}

provider "aws" {
  region = var.region
}

provider "aws" {
  region = var.region
  alias  = "data"

  assume_role {
    role_arn     = var.data_account_deploy_role_arn
    session_name = "secure-data-hub-terraform"
  }
}
