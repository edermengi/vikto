locals {
  broadcast_lambda_fn_name = "${local.name_prefix}-broadcast-${local.name_suffix}"
  broadcast_package_file   = "../../dist/broadcast.zip"
}

resource "aws_lambda_function" "broadcast_lambda_fn" {
  function_name    = local.broadcast_lambda_fn_name
  filename         = local.broadcast_package_file
  role             = aws_iam_role.broadcast_lambda_role.arn
  handler          = "broadcast.main.handler"
  source_code_hash = filebase64sha256(local.broadcast_package_file)
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
    Name = local.wsapi_lambda_fn_name
  })
}

resource "aws_cloudwatch_log_group" "broadcast_lambda_loggroup" {
  name              = "/aws/lambda/${local.broadcast_lambda_fn_name}"
  retention_in_days = var.log_retention_in_days
  tags              = merge(local.tags, {
    Name = local.broadcast_lambda_fn_name
  })
}