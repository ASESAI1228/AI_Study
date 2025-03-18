variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "ap-northeast-1"
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "legal-app"
}

variable "environment" {
  description = "The deployment environment (e.g., development, staging, production)"
  type        = string
  default     = "development"
}

variable "availability_zones" {
  description = "The availability zones to deploy resources"
  type        = list(string)
  default     = ["ap-northeast-1a", "ap-northeast-1c"]
}

variable "db_name" {
  description = "The name of the database"
  type        = string
  default     = "legaldb"
}

variable "db_username" {
  description = "The username for the database"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "The password for the database"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "The OpenAI API key"
  type        = string
  sensitive   = true
} 