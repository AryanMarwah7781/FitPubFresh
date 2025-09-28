#!/bin/bash
# Master deployment script for Fitness AI API - Day 3
# Orchestrates the complete containerization and deployment process

set -e  # Exit on any error

# Configuration
IMAGE_TAG="${1:-$(date +%Y%m%d-%H%M%S)}"
SKIP_TESTS="${2:-false}"

echo "🚀 Fitness AI API - Complete Deployment Pipeline"
echo "================================================"
echo "🏷️ Image Tag: $IMAGE_TAG"
echo "🧪 Skip Tests: $SKIP_TESTS"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not installed"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed"
    exit 1
fi

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not installed"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon not running"
    exit 1
fi

echo "✅ All prerequisites met"
echo ""

# Step 1: Setup ECR Repository
echo "🔧 Step 1: Setting up ECR repository..."
./scripts/setup-ecr.sh
echo "✅ ECR setup completed"
echo ""

# Step 2: Build Docker Image
echo "🏗️ Step 2: Building Docker image..."
./scripts/build-image.sh "$IMAGE_TAG"
echo "✅ Image build completed"
echo ""

# Step 3: Push to ECR
echo "📤 Step 3: Pushing image to ECR..."
./scripts/push-image.sh "$IMAGE_TAG"
echo "✅ Image push completed"
echo ""

# Step 4: Test EKS Deployment (optional)
if [ "$SKIP_TESTS" != "true" ]; then
    echo "🧪 Step 4: Testing EKS deployment..."
    ./scripts/test-eks-deployment.sh "$IMAGE_TAG"
    echo "✅ EKS deployment test completed"
else
    echo "⏭️ Step 4: Skipping EKS deployment tests"
fi
echo ""

# Get AWS account ID for final instructions
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com"
FULL_IMAGE_NAME="${ECR_REGISTRY}/fitness-ai-api:${IMAGE_TAG}"

# Update Kubernetes deployment with new image
echo "🔄 Step 5: Updating Kubernetes deployment file..."
sed -i.bak "s|ACCOUNT_ID\.dkr\.ecr\.us-east-1\.amazonaws\.com/fitness-ai-api:latest|${FULL_IMAGE_NAME}|g" k8s-production-api.yaml
echo "✅ Kubernetes deployment file updated"
echo ""

echo "🎉 Deployment pipeline completed successfully!"
echo ""
echo "📋 Summary:"
echo "  🏷️ Image Tag: $IMAGE_TAG"  
echo "  🌐 ECR URI: $FULL_IMAGE_NAME"
echo "  📁 Updated: k8s-production-api.yaml"
echo ""
echo "🚀 Next Steps:"
echo "1. Deploy to EKS:"
echo "   kubectl apply -f k8s-production-api.yaml"
echo ""
echo "2. Monitor deployment:"
echo "   kubectl get pods -l app=fitness-ai-api --watch"
echo ""
echo "3. Test the deployment:"
echo "   kubectl port-forward svc/fitness-ai-api-service 8080:80"
echo "   curl http://localhost:8080/health"
echo ""
echo "4. Check logs:"
echo "   kubectl logs -l app=fitness-ai-api -f"
echo ""
echo "🔄 To rollback (if needed):"
echo "   kubectl rollout undo deployment/fitness-ai-api"