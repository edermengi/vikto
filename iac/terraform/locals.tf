locals {
  tags = {
    "environment" = var.environment
    "application" = var.application_name
  }
  region_short_names = {
    "eu-west-1"      = "euw1"
    "ap-southeast-1" = "apse1"
  }
  name_prefix               = var.application_name
  current_region_short_name = lookup(local.region_short_names, data.aws_region.current.name)
  name_suffix               = "${var.environment}-${local.current_region_short_name}"
}
