locals {
  app_lambda_role_name          = "${local.name_prefix}-appLambdaRole-${local.name_suffix}"
  app_lambda_invoke_policy_name = "${local.name_prefix}-appLambdaInvokePolicy-${local.name_suffix}"
  logging_policy_name           = "${local.name_prefix}-loggingPolicy-${local.name_suffix}"
  dynamodb_policy_name          = "${local.name_prefix}-dynamoDbPolicy-${local.name_suffix}"
  apigw_manage_policy_name      = "${local.name_prefix}-apigwManagePolicy-${local.name_suffix}"
}

resource "aws_iam_role" "app_lambda_role" {
  name               = local.app_lambda_role_name
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
        },
        {
          "Action" : "sts:AssumeRole",
          "Principal" : {
            "Service" : "apigateway.amazonaws.com"
          },
          "Effect" : "Allow",
          "Sid" : ""
        }
      ]
    })

  tags = merge(local.tags, {
    Name = local.app_lambda_role_name
  })
}

# ATTACHMENTS

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.app_lambda_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_role_policy_attachment" "lambda_invoke_policy_attachment" {
  role       = aws_iam_role.app_lambda_role.name
  policy_arn = aws_iam_policy.app_lambda_invoke.arn
}

resource "aws_iam_role_policy_attachment" "dynamodb_policy_attachment" {
  role       = aws_iam_role.app_lambda_role.name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}

resource "aws_iam_role_policy_attachment" "api_gateway_manage_policy_attachment" {
  role       = aws_iam_role.app_lambda_role.name
  policy_arn = aws_iam_policy.api_gateway_manage_connections.arn
}


# POLICIES

resource "aws_iam_policy" "lambda_logging" {
  name        = local.logging_policy_name
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          "Resource" : "arn:aws:logs:*:*:*",
          "Effect" : "Allow"
        }
      ]
    })
}

resource "aws_iam_policy" "app_lambda_invoke" {
  name        = local.app_lambda_invoke_policy_name
  path        = "/"
  description = "IAM policy for invoking lambda from ApiGateway"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : [
            "lambda:InvokeFunction"
          ],
          "Resource" : aws_lambda_function.app_lambda_fn.arn,
          "Effect" : "Allow"
        }
      ]
    })
}

resource "aws_iam_policy" "dynamodb_access" {
  name        = local.dynamodb_policy_name
  path        = "/"
  description = "IAM policy for invoking lambda from ApiGateway"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : [
            "dynamodb:PutItem",
            "dynamodb:GetItem",
            "dynamodb:UpdateItem",
            "dynamodb:DeleteItem",
            "dynamodb:Query",
          ],
          "Resource" : [
            aws_dynamodb_table.session_table.arn, aws_dynamodb_table.game_table.arn,
            aws_dynamodb_table.user_table.arn, aws_dynamodb_table.quiz_table.arn
          ]
          "Effect" : "Allow"
        }
      ]
    })
}

resource "aws_iam_policy" "api_gateway_manage_connections" {
  name        = local.apigw_manage_policy_name
  path        = "/"
  description = "IAM policy for executing manage connections"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : [
            "execute-api:ManageConnections",
          ],
          "Resource" : [
            "${aws_apigatewayv2_api.ws_api.execution_arn}/*/*"
          ]
          "Effect" : "Allow"
        }
      ]
    })
}
