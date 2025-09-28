#!/bin/bash
# Docker Push Script for Fitness AI API
# Pushes Docker image to AWS ECR for EKS deployment

set -e  # Exit on any error

# Configuration
AWS_REGION="us-east-1"
REPOSITORY_NAME="fitness-ai-api"
IMAGE_TAG="${1:-latest}"

# Get AWS account ID
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS CLI not configured or no valid credentials"
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FULL_IMAGE_NAME="${ECR_REGISTRY}/${REPOSITORY_NAME}:${IMAGE_TAG}"

echo "🚀 Pushing Docker Image to AWS ECR"
echo "===================================="
echo "📦 Repository: $REPOSITORY_NAME"
echo "🏷️ Tag: $IMAGE_TAG"
echo "🌐 Full Image: $FULL_IMAGE_NAME"
echo ""

# Check if the local image exists
if ! docker image inspect "${REPOSITORY_NAME}:${IMAGE_TAG}" >/dev/null 2>&1; then
    echo "❌ Local image '${REPOSITORY_NAME}:${IMAGE_TAG}' not found"
    echo "Please build the image first: ./scripts/build-image.sh ${IMAGE_TAG}"
    exit 1
fi

# Check if ECR repository exists
echo "🔍 Checking ECR repository..."
if ! aws ecr describe-repositories --repository-names $REPOSITORY_NAME --region $AWS_REGION >/dev/null 2>&1; then
    echo "❌ ECR repository '$REPOSITORY_NAME' not found"
    echo "Please create the repository first: ./scripts/setup-ecr.sh"
    exit 1
fi

echo "✅ ECR repository exists"

# Authenticate Docker to ECR
echo ""
echo "🔑 Authenticating Docker with ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

if [ $? -eq 0 ]; then
    echo "✅ Successfully authenticated with ECR"
else
    echo "❌ Failed to authenticate with ECR"
    exit 1
fi

# Tag the image for ECR
echo ""
echo "🏷️ Tagging image for ECR..."
docker tag "${REPOSITORY_NAME}:${IMAGE_TAG}" "$FULL_IMAGE_NAME"

# Also tag as latest if not already latest
if [ "$IMAGE_TAG" != "latest" ]; then
    docker tag "${REPOSITORY_NAME}:${IMAGE_TAG}" "${ECR_REGISTRY}/${REPOSITORY_NAME}:latest"
    echo "✅ Tagged as both $IMAGE_TAG and latest"
else
    echo "✅ Tagged as $IMAGE_TAG"
fi

# Push the image
echo ""
echo "⬆️ Pushing image to ECR..."
echo "This may take several minutes depending on image size and network speed..."

PUSH_START_TIME=$(date +%s)

# Push specific tag
docker push "$FULL_IMAGE_NAME"

# Push latest tag if not the same
if [ "$IMAGE_TAG" != "latest" ]; then
    docker push "${ECR_REGISTRY}/${REPOSITORY_NAME}:latest"
fi

PUSH_END_TIME=$(date +%s)
PUSH_DURATION=$((PUSH_END_TIME - PUSH_START_TIME))

echo ""
echo "✅ Successfully pushed to ECR!"
echo "⏱️ Push time: ${PUSH_DURATION} seconds"

# Verify the image in ECR
echo ""
echo "🔍 Verifying image in ECR..."
IMAGES=$(aws ecr list-images --repository-name $REPOSITORY_NAME --region $AWS_REGION --query 'imageIds[*].imageTag' --output text)

if echo "$IMAGES" | grep -q "$IMAGE_TAG"; then
    echo "✅ Image $IMAGE_TAG successfully available in ECR"
else
    echo "❌ Image $IMAGE_TAG not found in ECR"
    exit 1
fi

# Display ECR repository information
echo ""
echo "📊 ECR Repository Status:"
aws ecr describe-repositories --repository-names $REPOSITORY_NAME --region $AWS_REGION --query 'repositories[0].[repositoryName,registryId,repositoryUri]' --output table

echo ""
echo "📦 Available Images:"
aws ecr list-images --repository-name $REPOSITORY_NAME --region $AWS_REGION --query 'imageIds[*].[imageTag,imagePushedAt]' --output table

echo ""
echo "🎉 Image push completed successfully!"
echo ""
echo "🌐 Image URI: $FULL_IMAGE_NAME"
echo ""
echo "Next steps:"
echo "1. Update k8s-production-api.yaml with the image URI"
echo "2. Deploy to EKS: kubectl apply -f k8s-production-api.yaml"
echo "3. Verify deployment: kubectl get pods -l app=fitness-ai-api"

# Provide kubectl update command
echo ""
echo "💡 Quick deploy command:"
echo "kubectl set image deployment/fitness-ai-api fitness-ai-api=$FULL_IMAGE_NAME"