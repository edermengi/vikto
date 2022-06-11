terraform plan \
  -var-file "./env/eu-west-1-dev.tfvars" \
  -var "environment=dev" \
  -var "region=eu-west-1" \
  -var "profile=vikto" \
  -input=false -out .terraform/local.plan
