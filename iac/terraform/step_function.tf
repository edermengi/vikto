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
          "Next" : "AskTopic"
        },
        "AskTopic" : {
          "Type" : "Task",
          "Resource" : "arn:aws:states:::lambda:invoke.waitForTaskToken",
          "Parameters" : {
            "FunctionName" : aws_lambda_function.flow_lambda_fn.function_name
            "Payload" : {
              "event" : "askTopic",
              "gameId.$" : "$.gameId",
              "taskToken.$" : "$$.Task.Token"
            }
          },
          "ResultPath" : "$.result",
          "Next" : "ShowTopic"
        },
        "ShowTopic" : {
          "Type" : "Task",
          "Resource" : "arn:aws:states:::lambda:invoke",
          "Parameters" : {
            "FunctionName" : aws_lambda_function.flow_lambda_fn.function_name
            "Payload" : {
              "event" : "showTopic",
              "gameId.$" : "$.gameId"
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
          "Next" : "WaitBeforeChoice"
        },
        "WaitBeforeChoice" : {
          "Type" : "Wait",
          "Seconds" : 3,
          "Next" : "ChoiceState"
        }
        "ChoiceState" : {
          "Type" : "Choice",
          "Choices" : [
            {
              "Variable" : "$.remainingRounds",
              "NumericGreaterThan" : 0,
              "Next" : "AskTopic"
            },
            {
              "Variable" : "$.remainingQuestions",
              "NumericGreaterThan" : 0,
              "Next" : "AskQuestion"
            }
          ],
          "Default" : "ShowWinner"
        },
        "ShowWinner" : {
          "Type" : "Task",
          "Resource" : "arn:aws:states:::lambda:invoke",
          "Parameters" : {
            "FunctionName" : aws_lambda_function.flow_lambda_fn.function_name
            "Payload" : {
              "event" : "showWinner",
              "gameId.$" : "$.gameId"
            }
          },
          "ResultPath" : "$.result",
          "End" : true
        }
      }
    })

  tags = merge(local.tags, {
    Name = local.game_sf_name
  })

}
