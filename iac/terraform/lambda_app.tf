locals {
  app_lambda_fn_name = "${local.name_prefix}-app-${local.name_suffix}"
  app_package_file   = "../../dist/app/app.zip"
}

resource "aws_lambda_function" "app_lambda_fn" {
  function_name    = local.app_lambda_fn_name
  filename         = local.app_package_file
  role             = aws_iam_role.app_lambda_role.arn
  publish          = true
  handler          = "connect.handler"
  source_code_hash = filebase64sha256(local.app_package_file)
  runtime          = "python3.9"
  environment {
    variables = {
      CONTENT_BUCKET = "todo"
    }
  }
  tags = merge(local.tags, {
    Name = local.app_lambda_fn_name
  })
}


resource "aws_iam_role" "app_lambda_role" {
  name               = "iam_for_lambda"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    },
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "lambda_logging" {
  name        = "lambda_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.app_lambda_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_policy" "lambda_invoke" {
  name        = "lambda_invoke"
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
          #          "Resource" : "${aws_apigatewayv2_api.ws_api.execution_arn}/*/*",
          "Effect" : "Allow"
        }
      ]
    })
}

resource "aws_iam_role_policy_attachment" "lambda_invoke_policy_attachment" {
  role       = aws_iam_role.app_lambda_role.name
  policy_arn = aws_iam_policy.lambda_invoke.arn
}
