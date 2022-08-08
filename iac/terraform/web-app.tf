locals {
  web_s3_bucket_name     = "${local.name_prefix}-web-${local.name_suffix}"
  web_ip_white_list_file = "templates/web-ip-white-list.local"
  web_ip_white_list      = fileexists(local.web_ip_white_list_file) ? jsondecode(file(local.web_ip_white_list_file)) : [
    "0.0.0.0/0"
  ]
}

resource "aws_s3_bucket" "web_bucket" {
  bucket = local.web_s3_bucket_name
}

resource "aws_s3_bucket_website_configuration" "web_bucket_website_configuration" {
  bucket = aws_s3_bucket.web_bucket.bucket

  index_document {
    suffix = "index.html"
  }

}

resource "aws_s3_bucket_policy" "allow_public_access" {
  bucket = aws_s3_bucket.web_bucket.id
  policy = data.aws_iam_policy_document.public_access_document.json
}

data "aws_iam_policy_document" "public_access_document" {
  statement {
    principals {
      type        = "*"
      identifiers = ["*"]
    }

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]

    condition {
      test     = "IpAddress"
      values   = local.web_ip_white_list
      variable = "aws:SourceIp"
    }

    resources = [
      aws_s3_bucket.web_bucket.arn,
      "${aws_s3_bucket.web_bucket.arn}/*",
    ]
  }
}