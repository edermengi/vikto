locals {
  app_lambda_fn_name = "${local.name_prefix}-app-${local.name_suffix}"
  app_package_file   = "../../dist/app.zip"
}

resource "aws_lambda_function" "app_lambda_fn" {
  function_name    = local.app_lambda_fn_name
  filename         = local.app_package_file
  role             = aws_iam_role.app_lambda_role.arn
  handler          = "main.handler"
  source_code_hash = filebase64sha256(local.app_package_file)
  runtime          = "python3.9"
  timeout          = 10

  environment {
    variables = {
      CONTENT_BUCKET              = aws_s3_bucket.content_bucket.bucket
      DYNAMODB_SESSION_TABLE_NAME = aws_dynamodb_table.session_table.name
      DYNAMODB_GAME_TABLE_NAME    = aws_dynamodb_table.game_table.name
      DYNAMODB_USER_TABLE_NAME    = aws_dynamodb_table.user_table.name
      WS_API_GATEWAY_URL          = "${replace(aws_apigatewayv2_api.ws_api.api_endpoint, "wss", "https")}/${local.stage_name}"
    }
  }
  tags = merge(local.tags, {
    Name = local.app_lambda_fn_name
  })
}
