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
          "Resource" : "arn:aws:states:::lambda:invoke.waitForTaskToken",
          "Parameters" : {
            "FunctionName": aws_lambda_function.flow_lambda_fn.function_name
            "Payload" : {
              "event": "waitPlayersReady",
              "gameId.$" : "$.gameId",
              "taskToken.$" : "$$.Task.Token"
            }
          },
          "End" : true
        }
      }
    })

  tags = merge(local.tags, {
    Name = local.game_sf_name
  })

}
