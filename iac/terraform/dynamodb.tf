locals {
  games_table_name = "${local.name_prefix}-games-${var.environment}"
}

resource "aws_dynamodb_table" "games_table" {
  name         = local.games_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "GameId"
  range_key    = "Entity"

  attribute {
    name = "GameId"
    type = "S"
  }

  attribute {
    name = "Entity"
    type = "S"
  }

  ttl {
    attribute_name = "TTL"
    enabled        = true
  }

  tags = merge(local.tags, {
    Name = local.games_table_name
  })
}