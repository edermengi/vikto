locals {
  flow_lambda_role_name = "${local.name_prefix}-flowLambdaRole-${local.name_suffix}"
}

resource "aws_iam_role" "flow_lambda_role" {
  name               = local.flow_lambda_fn_name
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
        }
      ]
    })

  tags = merge(local.tags, {
    Name = local.flow_lambda_role_name
  })
}

# ATTACHMENTS

resource "aws_iam_role_policy_attachment" "flow_lambda_logs" {
  role       = aws_iam_role.flow_lambda_role.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_iam_role_policy_attachment" "flow_dynamodb_policy_attachment" {
  role       = aws_iam_role.flow_lambda_role.name
  policy_arn = aws_iam_policy.dynamodb_access.arn
}

resource "aws_iam_role_policy_attachment" "flow_broadcast_lambda_invoke_policy_attachment" {
  role       = aws_iam_role.flow_lambda_role.name
  policy_arn = aws_iam_policy.broadcast_lambda_invoke.arn
}

resource "aws_iam_role_policy_attachment" "flow_content_s3_read_access_policy_attachment" {
  role       = aws_iam_role.flow_lambda_role.name
  policy_arn = aws_iam_policy.content_s3_read_access.arn
}


// POLICIES

resource "aws_iam_policy" "content_s3_read_access" {
  name        = "${local.name_prefix}-contentS3ReadPolicy-${local.name_suffix}"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Action" : [
            "s3:GetObject",
            "s3:ListBucket"
          ],
          "Resource" : [
            aws_s3_bucket.content_bucket.arn,
            "${aws_s3_bucket.content_bucket.arn}/*"
          ]
          "Effect" : "Allow"
        }
      ]
    })
}
