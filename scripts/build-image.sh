#!/bin/bash
# Docker Build Script for Fitness AI API
# Builds optimized Docker image for production deployment

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

echo "🏗️ Building Docker Image for Fitness AI API"
echo "=============================================="
echo "📦 Repository: $REPOSITORY_NAME"
echo "🏷️ Tag: $IMAGE_TAG"
echo "🌐 Full Image: $FULL_IMAGE_NAME"
echo ""

# Build the Docker image
echo "🔨 Building Docker image..."
echo "This may take a few minutes..."
echo ""

# Record build start time
BUILD_START_TIME=$(date +%s)

docker build \
    --no-cache \
    --platform linux/amd64 \
    --target production \
    --tag "${REPOSITORY_NAME}:${IMAGE_TAG}" \
    --tag "${REPOSITORY_NAME}:latest" \
    --tag "${FULL_IMAGE_NAME}" \
    --build-arg BUILDTIME=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VERSION=${IMAGE_TAG} \
    .

BUILD_END_TIME=$(date +%s)
BUILD_DURATION=$((BUILD_END_TIME - BUILD_START_TIME))

echo ""
echo "✅ Docker image built successfully!"
echo "⏱️ Build time: ${BUILD_DURATION} seconds"
echo ""

# Display image information
echo "📊 Image Details:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedSince}}" | grep -E "(REPOSITORY|${REPOSITORY_NAME})"
echo ""

# Test the image locally
echo "🧪 Testing image locally..."

# Clean up any existing test container
docker stop fitness-api-test 2>/dev/null || true
docker rm fitness-api-test 2>/dev/null || true

CONTAINER_ID=$(docker run -d -p 8001:8000 --name fitness-api-test "${REPOSITORY_NAME}:${IMAGE_TAG}")

echo "Waiting for container to start..."
sleep 10

# Test health endpoint
if curl -f http://localhost:8001/health/live > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID
    docker rm $CONTAINER_ID
    exit 1
fi

# Test API root endpoint
if curl -f http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ API root endpoint responding!"
else
    echo "⚠️ API root endpoint not responding"
fi

# Clean up test container
docker stop $CONTAINER_ID
docker rm $CONTAINER_ID
echo "🧹 Test container cleaned up"

echo ""
echo "🎉 Image build and test completed successfully!"
echo ""
echo "Image tags created:"
echo "  - ${REPOSITORY_NAME}:${IMAGE_TAG}"
echo "  - ${REPOSITORY_NAME}:latest" 
echo "  - ${FULL_IMAGE_NAME}"
echo ""
echo "Next steps:"
echo "1. Push to ECR: ./scripts/push-image.sh ${IMAGE_TAG}"
echo "2. Deploy to EKS: kubectl apply -f k8s-production-api.yaml"