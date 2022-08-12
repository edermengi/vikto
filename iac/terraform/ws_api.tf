locals {
  ws_api_name = "${local.name_prefix}-wsApi-${local.name_suffix}"
  stage_name  = var.environment
}
resource "aws_apigatewayv2_api" "ws_api" {
  name                       = local.ws_api_name
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"

  tags = merge(local.tags, {
    Name = local.ws_api_name
  })
}

resource "aws_apigatewayv2_route" "connect" {
  api_id             = aws_apigatewayv2_api.ws_api.id
  route_key          = "$connect"
  authorization_type = "NONE"
  target             = "integrations/${aws_apigatewayv2_integration.websockets_connect_integration.id}"
}

resource "aws_apigatewayv2_route" "disconnect" {
  api_id    = aws_apigatewayv2_api.ws_api.id
  route_key = "$disconnect"
  target    = "integrations/${aws_apigatewayv2_integration.websockets_disconnect_integration.id}"
}

resource "aws_apigatewayv2_route" "default" {
  api_id                     = aws_apigatewayv2_api.ws_api.id
  route_key                  = "$default"
  target                     = "integrations/${aws_apigatewayv2_integration.websockets_default_integration.id}"
  model_selection_expression = "\\$default"

  request_models = {
    "$default" = aws_apigatewayv2_model.default.name
  }
}

resource "aws_apigatewayv2_model" "default" {
  api_id       = aws_apigatewayv2_api.ws_api.id
  content_type = "application/json"
  name         = "default"

  schema = file("${path.module}/templates/ws_api_models.json")
}

resource "aws_apigatewayv2_integration" "websockets_connect_integration" {
  api_id                    = aws_apigatewayv2_api.ws_api.id
  integration_type          = "AWS_PROXY"
  integration_method        = "POST"
  integration_uri           = aws_lambda_function.app_lambda_fn.invoke_arn
  passthrough_behavior      = "WHEN_NO_MATCH"
  #  credentials_arn           = aws_iam_role.app_lambda_role.arn
  content_handling_strategy = "CONVERT_TO_TEXT"
}

resource "aws_apigatewayv2_integration" "websockets_disconnect_integration" {
  api_id                    = aws_apigatewayv2_api.ws_api.id
  integration_type          = "AWS_PROXY"
  integration_method        = "POST"
  integration_uri           = aws_lambda_function.app_lambda_fn.invoke_arn
  passthrough_behavior      = "WHEN_NO_MATCH"
  credentials_arn           = aws_iam_role.app_lambda_role.arn
  content_handling_strategy = "CONVERT_TO_TEXT"
}

resource "aws_apigatewayv2_integration" "websockets_default_integration" {
  api_id                    = aws_apigatewayv2_api.ws_api.id
  integration_type          = "AWS_PROXY"
  integration_method        = "POST"
  integration_uri           = aws_lambda_function.app_lambda_fn.invoke_arn
  passthrough_behavior      = "WHEN_NO_MATCH"
  credentials_arn           = aws_iam_role.app_lambda_role.arn
  content_handling_strategy = "CONVERT_TO_TEXT"
}

resource "aws_lambda_permission" "apigw_invoke_lambda_connect" {
  statement_id  = "AllowConnectionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.app_lambda_fn.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.ws_api.execution_arn}/*/*"
}

resource "aws_apigatewayv2_stage" "stage" {
  api_id        = aws_apigatewayv2_api.ws_api.id
  name          = local.stage_name
  deployment_id = aws_apigatewayv2_deployment.websocket_deploy.id

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.dante_api_loggroup.arn
    format          = "$context.identity.sourceIp,$context.identity.caller,$context.identity.user,$context.requestTime,$context.eventType,$context.routeKey,$context.connectionId,$context.status,$context.requestId"
  }

  default_route_settings {
    throttling_rate_limit    = 10
    throttling_burst_limit   = 20
    data_trace_enabled       = true
    detailed_metrics_enabled = true
    logging_level            = "INFO"
  }
}

resource "aws_apigatewayv2_deployment" "websocket_deploy" {
  api_id = aws_apigatewayv2_api.ws_api.id

    lifecycle {
      create_before_destroy = true
    }

  triggers = {
    redeployment = sha1(jsonencode([
      aws_apigatewayv2_integration.websockets_connect_integration,
      aws_apigatewayv2_integration.websockets_disconnect_integration,
      aws_apigatewayv2_integration.websockets_default_integration,

      aws_apigatewayv2_route.connect,
      aws_apigatewayv2_route.disconnect,
      aws_apigatewayv2_route.default
    ]))
  }
}

resource "aws_cloudwatch_log_group" "dante_api_loggroup" {
  name              = "/aws/apigateway/${aws_apigatewayv2_api.ws_api.id}/${local.stage_name}"
  retention_in_days = var.log_retention_in_days
  tags              = merge(local.tags, {
    Name = "${local.ws_api_name}_logs"
  })
}