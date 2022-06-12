#resource "aws_api_gateway_rest_api" "api" {
#  name = "${local.name_prefix}-api-${local.name_suffix}"
#  endpoint_configuration {
#    types = ["REGIONAL"]
#  }
#  tags = merge(local.tags, {
#    Name = "${local.name_prefix}-api-${local.name_suffix}"
#  })
#}
#
#resource "aws_api_gateway_stage" "aws_api_gateway_stage_v1" {
#  deployment_id = aws_api_gateway_deployment.api_deployment.id
#  rest_api_id   = aws_api_gateway_rest_api.api.id
#  stage_name    = var.stage_name
#  description   = "Deployed at ${timestamp()}"
#
#  tags = merge(local.tags, {
#    Name = aws_api_gateway_rest_api.api.name
#  })
#
#  provisioner "local-exec" {
#    command = "${var.aws_cli_execution_command} apigateway create-deployment --rest-api-id ${aws_api_gateway_rest_api.api.id} --stage-name ${aws_api_gateway_stage.aws_api_gateway_stage_v1.stage_name}"
#  }
#}
#
#resource "aws_api_gateway_deployment" "api_deployment" {
#  rest_api_id       = aws_api_gateway_rest_api.api.id
#  description       = "Deployed at ${timestamp()}"
#  stage_description = md5(file("${path.module}/api_gateway.tf"))
#  lifecycle {
#    create_before_destroy = true
#    ignore_changes        = [description]
#  }
#
#  variables = {
#    # force deployment every times terraform apply
#    deployed_at = timestamp()
#  }
#
#  depends_on = [
#    aws_api_gateway_rest_api.api,
#  ]
#}
#
#resource "aws_api_gateway_resource" "app_resource" {
#  rest_api_id = aws_api_gateway_rest_api.api.id
#  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
#  path_part   = "app"
#}
#
#resource "aws_api_gateway_method" "app_method" {
#  rest_api_id   = aws_api_gateway_rest_api.api.id
#  resource_id   = aws_api_gateway_resource.app_resource.id
#  http_method   = "POST"
#  authorization = "NONE"
#}
