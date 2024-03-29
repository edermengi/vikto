locals {
  game_table_name    = "${local.name_prefix}-game-${var.environment}"
  session_table_name = "${local.name_prefix}-session-${var.environment}"
  user_table_name = "${local.name_prefix}-user-${var.environment}"
  quiz_table_name = "${local.name_prefix}-quiz-${var.environment}"
}

resource "aws_dynamodb_table" "game_table" {
  name         = local.game_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "gameId"
  range_key    = "entity"

  attribute {
    name = "gameId"
    type = "S"
  }

  attribute {
    name = "entity"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = merge(local.tags, {
    Name = local.game_table_name
  })
}

resource "aws_dynamodb_table" "session_table" {
  name         = local.session_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "connectionId"
  range_key    = "entity"

  attribute {
    name = "connectionId"
    type = "S"
  }

  attribute {
    name = "entity"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = merge(local.tags, {
    Name = local.session_table_name
  })
}

resource "aws_dynamodb_table" "user_table" {
  name         = local.user_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "userId"
  range_key    = "entity"

  attribute {
    name = "userId"
    type = "S"
  }

  attribute {
    name = "entity"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = merge(local.tags, {
    Name = local.user_table_name
  })
}

resource "aws_dynamodb_table" "quiz_table" {
  name         = local.quiz_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  range_key    = "entity"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "entity"
    type = "S"
  }

  tags = merge(local.tags, {
    Name = local.quiz_table_name
  })
}