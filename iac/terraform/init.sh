terraform init \
  -backend-config="profile=vikto" \
  -backend-config="region=eu-west-1" \
  -backend-config="bucket=vikto-terraform" \
  -backend-config="key=vikto/dev/terraform.tfstate"
