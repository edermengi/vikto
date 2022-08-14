locals {
  game_sf_name = "${local.name_prefix}-game-${local.name_suffix}"
}

resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = local.game_sf_name
  role_arn = aws_iam_role.game_sf_role.arn

  definition = jsonencode(
    {
      "StartAt" : "WaitPlayersReady",
      "States" : {
        "WaitPlayersReady" : {
          "Type" : "Task",
          "Resource" : aws_lambda_function.app_lambda_fn.arn
          "End" : true
        }
      }
    })

  tags = merge(local.tags, {
    Name = local.game_sf_name
  })

}
