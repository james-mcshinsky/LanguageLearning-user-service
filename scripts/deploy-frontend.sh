#!/bin/bash
set -e

# Build the frontend
npm run build

BUCKET="${1:-$DEPLOY_BUCKET}"

if [[ -z "$BUCKET" ]]; then
  echo "Usage: DEPLOY_BUCKET=<bucket> $0 or $0 <bucket>" >&2
  exit 1
fi

aws s3 sync dist/ "s3://$BUCKET"
