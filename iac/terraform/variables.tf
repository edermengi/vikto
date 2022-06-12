variable "profile" {
  type = string
}

variable "region" {
  type = string
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "application_name" {
  type    = string
  default = "vikto"
}

variable "aws_cli_execution_command" {
  type    = string
  default = "aws"
}

variable "log_retention_in_days" {
  type    = number
  default = 7
}

variable "stage_name" {
  type    = string
  default = "v1"
}