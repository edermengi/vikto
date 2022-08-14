locals {
  game_sf_role_name              = "${local.name_prefix}-sfGameRole-${local.name_suffix}"
  game_sf_policy_name            = "${local.name_prefix}-sfGamePolicy-${local.name_suffix}"
  flow_lambda_invoke_policy_name = "${local.name_prefix}-flowLambdaInvokePolicy-${local.name_suffix}"
  game_sf_invoke_policy_name     = "${local.name_prefix}-sfGameInvokePolicy-${local.name_suffix}"
}

resource "aws_iam_role" "game_sf_role" {
  name               = local.game_sf_role_name
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
            "Service" : "states.amazonaws.com"
          },
          "Effect" : "Allow",
          "Sid" : ""
        }
      ]
    })

  tags = merge(local.tags, {
    Name = local.game_sf_role_name
  })
}


resource "aws_iam_policy" "flow_lambda_invoke" {
  name        = local.flow_lambda_invoke_policy_name
  path        = "/"
  description = "IAM policy for invoking flow lambda"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : [
            "lambda:InvokeFunction"
          ],
          "Resource" : aws_lambda_function.flow_lambda_fn.arn,
          "Effect" : "Allow"
        }
      ]
    })
}


resource "aws_iam_role_policy_attachment" "sf_low__lambda_invoke_policy_attachment" {
  role       = aws_iam_role.game_sf_role.name
  policy_arn = aws_iam_policy.flow_lambda_invoke.arn
}

resource "aws_iam_policy" "game_sf_invoke" {
  name        = local.game_sf_invoke_policy_name
  path        = "/"
  description = "IAM policy for invoking game step function"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : [
            "states:StartExecution"
          ],
          "Resource" : aws_sfn_state_machine.sfn_state_machine.arn,
          "Effect" : "Allow"
        }
      ]
    })
}
