AWS_REGION := eu-west-1
AWS_PROFILE := vikto
ENV := dev
TERRAFORM_LOCAL = .terraform/local.plan

clean:
	rm -rf dist

package:
	mkdir -p dist/app
	pip install -r app/requirements.txt --target dist/app
	cp -r app/* dist/app/
	cd dist/app && zip -r ../app.zip .

test:
	cd app && python -m unittest discover -v -s ./test -t .

# run it only once on new account
init_terraform_infrastructure:
	cd "iac/terraform-backend" && ./deploy.sh $(AWS_PROFILE) $(AWS_REGION)

terraform_init:
	cd "iac/terraform" && \
	terraform init \
		-backend-config="profile=$(AWS_PROFILE)" \
		-backend-config="region=$(AWS_REGION)" \
		-backend-config="bucket=vikto-terraform" \
		-backend-config="key=vikto/$(ENV)/terraform.tfstate"

terraform_plan:
	cd "iac/terraform" && \
	terraform plan \
		-var-file "./env/$(ENV)-eu-west-1.tfvars" \
		-var "environment=$(ENV)" \
		-var "region=$(AWS_REGION)" \
		-var "profile=$(AWS_PROFILE)" \
		-input=false -out $(TERRAFORM_LOCAL)

terraform_apply:
	cd "iac/terraform" && \
	terraform apply $(TERRAFORM_LOCAL)

terraform_destroy:
	cd "iac/terraform" && \
	terraform destroy \
		-var-file "./env/$(ENV)-eu-west-1.tfvars" \
		-var "environment=$(ENV)" \
		-var "region=$(AWS_REGION)" \
		-var "profile=$(AWS_PROFILE)" \

deploy: test clean package terraform_init terraform_plan terraform_apply

destroy: clean package terraform_init terraform_plan terraform_destroy

