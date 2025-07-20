#!/bin/bash
set -e

# AWS Deployment Script for Language Learning Website
#
# Usage:
#   AWS_ACCOUNT_ID=<id> AWS_REGION=<region> ./deploy-aws.sh
#   ./deploy-aws.sh <account_id> <region>
#
# Run `eb init` before using this script so the Elastic Beanstalk CLI is
# configured for your application. If the environment does not yet exist,
# create it with `eb create` (using the provided `docker-compose.yml` when
# deploying a multi-container setup).
#
# The script builds the Docker image, pushes it to ECR and then runs
# `eb deploy` to update the environment.

ACCOUNT_ID="${AWS_ACCOUNT_ID:-$1}"
REGION="${AWS_REGION:-$2}"

if [[ -z "$ACCOUNT_ID" || -z "$REGION" ]]; then
  echo "Error: AWS account ID and region must be provided." >&2
  echo "Usage: AWS_ACCOUNT_ID=<id> AWS_REGION=<region> $0" >&2
  echo "   or: $0 <account_id> <region>" >&2
  exit 1
fi

REPO="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

echo "Building Docker image..."
docker build -t language-learning-backend:latest .

echo "Tagging image for AWS..."
docker tag language-learning-backend:latest "$REPO/language-learning-backend:latest"

echo "Pushing to ECR..."
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$REPO"
docker push "$REPO/language-learning-backend:latest"

echo "Deploying to Elastic Beanstalk..."
eb deploy

echo "Deployment complete!"
