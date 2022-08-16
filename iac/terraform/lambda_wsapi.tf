locals {
  wsapi_lambda_fn_name = "${local.name_prefix}-wsapi-${local.name_suffix}"
  wsapi_package_file   = "../../dist/wsapi.zip"
}

resource "aws_lambda_function" "app_lambda_fn" {
  function_name    = local.wsapi_lambda_fn_name
  filename         = local.wsapi_package_file
  role             = aws_iam_role.app_lambda_role.arn
  handler          = "wsapi.main.handler"
  source_code_hash = filebase64sha256(local.wsapi_package_file)
  runtime          = "python3.9"
  timeout          = 10

  environment {
    variables = {
      LOG_LEVEL                   = "INFO"
      CONTENT_BUCKET              = aws_s3_bucket.content_bucket.bucket
      DYNAMODB_SESSION_TABLE_NAME = aws_dynamodb_table.session_table.name
      DYNAMODB_GAME_TABLE_NAME    = aws_dynamodb_table.game_table.name
      DYNAMODB_USER_TABLE_NAME    = aws_dynamodb_table.user_table.name
      BROADCAST_LAMBDA_NAME       = aws_lambda_function.broadcast_lambda_fn.function_name
      GAME_SFN_ARN                = aws_sfn_state_machine.sfn_state_machine.arn
    }
  }
  tags = merge(local.tags, {
    Name = local.wsapi_lambda_fn_name
  })
}

resource "aws_cloudwatch_log_group" "wsapi_lambda_loggroup" {
  name              = "/aws/lambda/${local.wsapi_lambda_fn_name}"
  retention_in_days = var.log_retention_in_days
  tags              = merge(local.tags, {
    Name = local.wsapi_lambda_fn_name
  })
}