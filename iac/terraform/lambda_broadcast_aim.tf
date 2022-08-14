locals {
  broadcast_lambda_role_name = "${local.name_prefix}-broadcastLambdaRole-${local.name_suffix}"
}

resource "aws_iam_role" "broadcast_lambda_role" {
  name               = local.broadcast_lambda_fn_name
  assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "lambda.amazonaws.com"
          },
          "Effect" : "Allow",
          "Sid" : ""
        }
      ]
    })

  tags = merge(local.tags, {
    Name = local.broadcast_lambda_fn_name
  })
}

# ATTACHMENTS

resource "aws_iam_role_policy_attachment" "broadcast_lambda_logs" {
  role       = aws_iam_role.broadcast_lambda_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_role_policy_attachment" "broadcast_dynamodb_policy_attachment" {
  role       = aws_iam_role.broadcast_lambda_role.name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}

resource "aws_iam_role_policy_attachment" "broadcast_api_gateway_manage_policy_attachment" {
  role       = aws_iam_role.broadcast_lambda_role.name
  policy_arn = aws_iam_policy.api_gateway_manage_connections.arn
}

