locals {
  game_sf_role_name   = "${local.name_prefix}-sfGameRole-${local.name_suffix}"
  game_sf_policy_name = "${local.name_prefix}-sfGamePolicy-${local.name_suffix}"
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
            "Service" : "apigateway.amazonaws.com"
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