#!/bin/sh


cd ../

pigar generate -f requirements.txt ./

EMBEDFUNC=embedfunc

# Login, tag, push
ACCOUNT_ID=406848153313
REGION=us-east-1

TAG=v$(date +%Y%m%d-%H%M%S)
IMAGE_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${EMBEDFUNC}:${TAG}"

# 2) Build single-arch and LOAD into classic docker engine (schema2)
docker buildx build . \
  --platform=linux/amd64 \
  --provenance=false --sbom=false \
  --load \
  -t "$IMAGE_URI"

# Create ECR repo (once)
#aws ecr create-repository --repository-name ${EMBEDFUNC}



aws ecr get-login-password --region "$REGION" \
 | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

#docker tag ${EMBEDFUNC}:latest "$IMAGE_URI"
docker push "$IMAGE_URI"

set -x

## Create (or update) the Lambda
#aws lambda create-function \
#  --function-name ${EMBEDFUNC} \
#  --package-type Image \
#  --code ImageUri="$IMAGE_URI" \
#  --role arn:aws:iam::$ACCOUNT_ID:role/service-role/embedfuncrole \
#  --architectures x86_64 \
#  --memory-size 3072 \
#  --timeout 30
# (Later updates use: aws lambda update-function-code --function-name ${EMBEDFUNC} --image-uri "$IMAGE_URI")
aws lambda update-function-code --function-name ${EMBEDFUNC} --image-uri "$IMAGE_URI"
docker buildx imagetools inspect "$IMAGE_URI"


