#!/usr/bin/env bash
PROFILE=$1
REGION=$2
AWS_CMD="aws --profile ${PROFILE}  --region ${REGION}"
STACK_NAME="terraform-s3"

read -p "Are you sure to remove stack ${STACK_NAME}?" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  exit 1
fi

$AWS_CMD cloudformation delete-stack \
  --stack-name "${STACK_NAME}"
