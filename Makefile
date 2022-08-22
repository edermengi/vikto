AWS_REGION := eu-west-1
AWS_PROFILE := vikto
ENV := dev
TERRAFORM_LOCAL = .terraform/local.plan
package_wsapi:P=wsapi
package_broadcast:P=broadcast
package_flow:P=flow

clean:
	rm -rf dist

package_wsapi:
	mkdir -p dist/$P
	pip install -r app/requirements.txt --target dist/$P
	cp -r app/common app/$P dist/$P/
	cd dist/$P && zip -r ../$P.zip . -x '*test*' '*pycache*'

package_broadcast:
	mkdir -p dist/$P
	pip install -r app/requirements.txt --target dist/$P
	cp -r app/common app/$P dist/$P/
	cd dist/$P && zip -r ../$P.zip . -x '*test*' '*pycache*'

package_flow:
	mkdir -p dist/$P
	pip install -r app/requirements.txt --target dist/$P
	cp -r app/common app/$P dist/$P/
	cd dist/$P && zip -r ../$P.zip . -x '*test*' '*pycache*'

package:  package_wsapi package_broadcast package_flow

test:
	cd app/common && python -m unittest discover -v -s ./test -t ..
	cd app/flow && python -m unittest discover -v -s ./test -t ..
	cd app/broadcast && python -m unittest discover -v -s ./test -t ..

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
		-var-file "./env/$(ENV)-$(AWS_REGION).tfvars" \
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
		-var-file "./env/$(ENV)-$(AWS_REGION).tfvars" \
		-var "environment=$(ENV)" \
		-var "region=$(AWS_REGION)" \
		-var "profile=$(AWS_PROFILE)" \

deploy: test clean package terraform_init terraform_plan terraform_apply

destroy: clean package terraform_init terraform_plan terraform_destroy

