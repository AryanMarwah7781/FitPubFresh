#!/bin/bash
# ECR Setup Script for Fitness AI API
# Creates ECR repository and configures access for EKS deployment

set -e  # Exit on any error

# Configuration
AWS_REGION="us-east-1"
REPOSITORY_NAME="fitness-ai-api"
CLUSTER_NAME="ai-fitness-dev"

echo "🚀 Setting up ECR Repository for Fitness AI API"
echo "================================================"

# Check if AWS CLI is configured
echo "📋 Checking AWS CLI configuration..."
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS CLI not configured or no valid credentials"
    echo "Please run: aws configure"
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS Account ID: $AWS_ACCOUNT_ID"
echo "✅ Region: $AWS_REGION"

# Create ECR repository if it doesn't exist
echo ""
echo "📦 Creating ECR repository: $REPOSITORY_NAME"

if aws ecr describe-repositories --repository-names $REPOSITORY_NAME --region $AWS_REGION >/dev/null 2>&1; then
    echo "✅ ECR repository '$REPOSITORY_NAME' already exists"
else
    echo "🔨 Creating ECR repository..."
    aws ecr create-repository \
        --repository-name $REPOSITORY_NAME \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    
    echo "✅ ECR repository created successfully"
fi

# Set repository policy for security
echo ""
echo "🔒 Configuring repository policies..."

# Create policy document for EKS cluster access
cat > /tmp/ecr-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowEKSClusterAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::${AWS_ACCOUNT_ID}:root"
        ]
      },
      "Action": [
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetAuthorizationToken"
      ]
    }
  ]
}
EOF

# Apply the policy
aws ecr set-repository-policy \
    --repository-name $REPOSITORY_NAME \
    --region $AWS_REGION \
    --policy-text file:///tmp/ecr-policy.json

echo "✅ Repository policy configured"

# Enable lifecycle policy to manage old images
echo ""
echo "🔄 Configuring lifecycle policy..."

cat > /tmp/lifecycle-policy.json <<EOF
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 10 production images",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["v", "prod"],
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {
        "type": "expire"
      }
    },
    {
      "rulePriority": 2,
      "description": "Keep untagged images for 1 day",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 1
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
EOF

aws ecr put-lifecycle-policy \
    --repository-name $REPOSITORY_NAME \
    --region $AWS_REGION \
    --lifecycle-policy-text file:///tmp/lifecycle-policy.json

echo "✅ Lifecycle policy configured"

# Get ECR login command
echo ""
echo "🔑 ECR Authentication:"
echo "Repository URI: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPOSITORY_NAME}"
echo ""
echo "To authenticate Docker with ECR, run:"
echo "aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Verify EKS cluster can access ECR
echo ""
echo "🔍 Verifying EKS cluster access to ECR..."

if kubectl get nodes >/dev/null 2>&1; then
    echo "✅ kubectl is configured and cluster is accessible"
    
    # Check if EKS nodes have ECR permissions
    echo "📋 EKS Node Groups:"
    aws eks describe-cluster --name $CLUSTER_NAME --region $AWS_REGION --query 'cluster.status' --output text
    
else
    echo "⚠️  kubectl not configured for EKS cluster"
    echo "To configure kubectl for EKS:"
    echo "aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME"
fi

# Clean up temporary files
rm -f /tmp/ecr-policy.json /tmp/lifecycle-policy.json

echo ""
echo "🎉 ECR setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Build your Docker image: ./scripts/build-image.sh"
echo "2. Push to ECR: ./scripts/push-image.sh"
echo "3. Deploy to EKS: kubectl apply -f k8s-production-api.yaml"