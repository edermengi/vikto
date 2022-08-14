locals {
  flow_lambda_fn_name = "${local.name_prefix}-flow-${local.name_suffix}"
  flow_package_file   = "../../dist/flow.zip"
}

resource "aws_lambda_function" "flow_lambda_fn" {
  function_name    = local.flow_lambda_fn_name
  filename         = local.flow_package_file
  role             = aws_iam_role.flow_lambda_role.arn
  handler          = "flow.main.handler"
  source_code_hash = filebase64sha256(local.flow_package_file)
  runtime          = "python3.9"
  timeout          = 10

  environment {
    variables = {
      CONTENT_BUCKET              = aws_s3_bucket.content_bucket.bucket
      DYNAMODB_SESSION_TABLE_NAME = aws_dynamodb_table.session_table.name
      DYNAMODB_GAME_TABLE_NAME    = aws_dynamodb_table.game_table.name
      DYNAMODB_USER_TABLE_NAME    = aws_dynamodb_table.user_table.name
      BROADCAST_LAMBDA_NAME       = aws_lambda_function.broadcast_lambda_fn.function_name
    }
  }
  tags = merge(local.tags, {
    Name = local.wsapi_lambda_fn_name
  })
}

resource "aws_cloudwatch_log_group" "flow_lambda_loggroup" {
  name              = "/aws/lambda/${local.flow_lambda_fn_name}"
  retention_in_days = var.log_retention_in_days
  tags              = merge(local.tags, {
    Name = local.flow_lambda_fn_name
  })
}