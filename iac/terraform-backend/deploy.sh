#!/usr/bin/env bash
PROFILE=$1
REGION=$2
AWS_CMD="aws --profile ${PROFILE}  --region ${REGION}"
STACK_NAME="terraform-s3"

$AWS_CMD cloudformation deploy \
    --stack-name     "${STACK_NAME}" \
    --template-file  terraform-s3.yaml
