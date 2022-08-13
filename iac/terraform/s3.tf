locals {
  content_s3_bucket_name = "${local.name_prefix}-content-${local.name_suffix}"
}

resource "aws_s3_bucket" "content_bucket" {
  bucket = local.content_s3_bucket_name
}