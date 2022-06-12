#!/usr/bin/env bash

if [ "$#" -ne 2 ]; then
  echo >&2 "Usage deploy.sh <aws_profile> <aws_region> "
  exit 1
fi

PROFILE=$1
REGION=$2
AWS_CMD="aws --profile ${PROFILE}  --region ${REGION}"
STACK_NAME="terraform-s3"

$AWS_CMD cloudformation deploy \
  --stack-name "${STACK_NAME}" \
  --template-file terraform-s3.yaml
