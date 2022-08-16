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
            "FunctionName" : aws_lambda_function.flow_lambda_fn.function_name
            "Payload" : {
              "event" : "waitPlayersReady",
              "gameId.$" : "$.gameId",
              "taskToken.$" : "$$.Task.Token"
            }
          },
          "ResultPath" : "$.result",
          "Next" : "AskQuestion"
        },
        "AskQuestion" : {
          "Type" : "Task",
          "Resource" : "arn:aws:states:::lambda:invoke.waitForTaskToken",
          "Parameters" : {
            "FunctionName" : aws_lambda_function.flow_lambda_fn.function_name
            "Payload" : {
              "event" : "askQuestion",
              "gameId.$" : "$.gameId",
              "taskToken.$" : "$$.Task.Token"
            }
          },
          "ResultPath" : "$.result",
          "Next" : "ShowAnswer"
        },
        "ShowAnswer" : {
          "Type" : "Task",
          "Resource" : "arn:aws:states:::lambda:invoke",
          "Parameters" : {
            "FunctionName" : aws_lambda_function.flow_lambda_fn.function_name
            "Payload" : {
              "event" : "showAnswer",
              "gameId.$" : "$.gameId"
            }
          },
          "ResultPath" : "$.result",
          "Next" : "ChoiceState"
        },
        "ChoiceState" : {
          "Type" : "Choice",
          "Choices" : [
            {
              "Variable" : "$.stop",
              "IsPresent" : true,
              "Next" : "Stop"
            }
          ],
          "Default" : "WaitBeforeAskQuestion"
        },
        "WaitBeforeAskQuestion": {
          "Type": "Wait",
          "Seconds": 3,
          "Next": "AskQuestion"
        }
        "Stop" : {
          "Type" : "Succeed"
        }
      }
    })

  tags = merge(local.tags, {
    Name = local.game_sf_name
  })

}
