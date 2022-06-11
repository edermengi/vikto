
provider "aws" {
  region  = var.region
  profile = var.profile
}

provider "aws" {
  alias   = "eu-west-1"
  region  = "eu-west-1"
  profile = var.profile
}

provider "aws" {
  alias   = "ap-southeast-1"
  region  = "ap-southeast-1"
  profile = var.profile
}
