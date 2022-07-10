locals {
  enable_access_logging_global_role_name       = "enableAccessLoggingGlobalRole"
  enable_access_logging_global_policy_name     = "enableAccessLoggingGlobalPolicy"
  enable_access_logging_global_attachment_name = "enableAccessLoggingGlobalPolicyAttachment"
}

resource "aws_api_gateway_account" "demo" {
  cloudwatch_role_arn = aws_iam_role.enable_access_logging_role.arn
}

resource "aws_iam_role" "enable_access_logging_role" {
  name = local.enable_access_logging_global_role_name

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "",
        "Effect" : "Allow",
        "Principal" : {
          "Service" : [
            "apigateway.amazonaws.com"
          ]
        },
        "Action" : [
          "sts:AssumeRole"
        ]
      }
    ]
  })
}

data "aws_iam_policy" "AmazonAPIGatewayPushToCloudWatchLogs" {
  arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

resource "aws_iam_policy_attachment" "push_to_cloudwatch_policy_attachment" {
  name       = local.enable_access_logging_global_attachment_name
  roles      = [aws_iam_role.enable_access_logging_role.name]
  policy_arn = data.aws_iam_policy.AmazonAPIGatewayPushToCloudWatchLogs.arn
}