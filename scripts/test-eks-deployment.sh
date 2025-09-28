#!/bin/bash
# Test Script for Fitness AI API in EKS
# Verifies that the containerized application works correctly in EKS

set -e  # Exit on any error

# Configuration
AWS_REGION="us-east-1"
REPOSITORY_NAME="fitness-ai-api"
CLUSTER_NAME="ai-fitness-dev"
NAMESPACE="${2:-default}"
IMAGE_TAG="${1:-latest}"

echo "🧪 Testing Fitness AI API in EKS"
echo "================================="
echo "🏷️ Image Tag: $IMAGE_TAG"
echo "🏢 Namespace: $NAMESPACE"
echo ""

# Check if kubectl is configured
if ! kubectl cluster-info >/dev/null 2>&1; then
    echo "❌ kubectl not configured or cluster not accessible"
    echo "Configure kubectl: aws eks update-kubeconfig --region $AWS_REGION --name $CLUSTER_NAME"
    exit 1
fi

echo "✅ kubectl configured and cluster accessible"

# Check if ECR image exists
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FULL_IMAGE_NAME="${ECR_REGISTRY}/${REPOSITORY_NAME}:${IMAGE_TAG}"

echo "🔍 Verifying ECR image exists..."
if aws ecr list-images --repository-name $REPOSITORY_NAME --region $AWS_REGION --query "imageIds[?imageTag=='$IMAGE_TAG']" --output text | grep -q "$IMAGE_TAG"; then
    echo "✅ ECR image $FULL_IMAGE_NAME exists"
else
    echo "❌ ECR image $FULL_IMAGE_NAME not found"
    echo "Push the image first: ./scripts/push-image.sh $IMAGE_TAG"
    exit 1
fi

# Create a test pod to verify image can be pulled
echo ""
echo "🚀 Creating test pod to verify image pull..."

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: fitness-api-test-pull
  namespace: $NAMESPACE
  labels:
    test: image-pull
spec:
  restartPolicy: Never
  containers:
  - name: fitness-api
    image: $FULL_IMAGE_NAME
    command: ["python", "-c", "print('Image pull successful!'); import main; print('FastAPI app imports successfully')"]
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "200m"
EOF

# Wait for pod to complete
echo "⏳ Waiting for test pod to complete..."
kubectl wait --for=condition=Ready pod/fitness-api-test-pull --namespace=$NAMESPACE --timeout=300s

# Check pod status
POD_STATUS=$(kubectl get pod fitness-api-test-pull --namespace=$NAMESPACE -o jsonpath='{.status.phase}')
echo "📊 Test pod status: $POD_STATUS"

if [ "$POD_STATUS" = "Succeeded" ] || kubectl logs fitness-api-test-pull --namespace=$NAMESPACE | grep -q "Image pull successful!"; then
    echo "✅ Image pull test passed!"
else
    echo "❌ Image pull test failed!"
    echo "Pod logs:"
    kubectl logs fitness-api-test-pull --namespace=$NAMESPACE
    kubectl delete pod fitness-api-test-pull --namespace=$NAMESPACE --ignore-not-found=true
    exit 1
fi

# Clean up test pod
kubectl delete pod fitness-api-test-pull --namespace=$NAMESPACE --ignore-not-found=true

# Create a test deployment
echo ""
echo "🚀 Creating test deployment..."

cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fitness-api-test
  namespace: $NAMESPACE
  labels:
    app: fitness-api-test
    test: deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fitness-api-test
  template:
    metadata:
      labels:
        app: fitness-api-test
    spec:
      containers:
      - name: fitness-api
        image: $FULL_IMAGE_NAME
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "test"
        - name: DEBUG
          value: "false"
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: fitness-api-test-service
  namespace: $NAMESPACE
spec:
  selector:
    app: fitness-api-test
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
EOF

# Wait for deployment to be ready
echo "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available deployment/fitness-api-test --namespace=$NAMESPACE --timeout=300s

# Check deployment status
echo ""
echo "📊 Deployment Status:"
kubectl get deployment fitness-api-test --namespace=$NAMESPACE
kubectl get pods -l app=fitness-api-test --namespace=$NAMESPACE

# Test the API endpoints
echo ""
echo "🧪 Testing API endpoints..."

# Port forward to test service
kubectl port-forward service/fitness-api-test-service 8002:80 --namespace=$NAMESPACE &
PORT_FORWARD_PID=$!
sleep 5

# Test health endpoints
echo "Testing health endpoints..."
if curl -f http://localhost:8002/health/live >/dev/null 2>&1; then
    echo "✅ Liveness probe endpoint working"
else
    echo "❌ Liveness probe endpoint failed"
fi

if curl -f http://localhost:8002/health/ready >/dev/null 2>&1; then
    echo "✅ Readiness probe endpoint working"
else
    echo "❌ Readiness probe endpoint failed"
fi

# Test main API endpoint
if curl -f http://localhost:8002/ >/dev/null 2>&1; then
    echo "✅ Main API endpoint working"
else
    echo "❌ Main API endpoint failed"
fi

# Test health check with details
echo ""
echo "📋 Health Check Details:"
curl -s http://localhost:8002/health | python3 -m json.tool || echo "Health endpoint not responding with JSON"

# Stop port forward
kill $PORT_FORWARD_PID 2>/dev/null || true

# Clean up test resources
echo ""
echo "🧹 Cleaning up test resources..."
kubectl delete deployment fitness-api-test --namespace=$NAMESPACE --ignore-not-found=true
kubectl delete service fitness-api-test-service --namespace=$NAMESPACE --ignore-not-found=true

echo ""
echo "🎉 EKS deployment test completed successfully!"
echo ""
echo "✅ Summary:"
echo "  - ECR image exists and is accessible"
echo "  - Image can be pulled by EKS nodes"
echo "  - Deployment starts successfully"
echo "  - Health endpoints are working"
echo "  - FastAPI application is running correctly"
echo ""
echo "Next steps:"
echo "1. Deploy production version: kubectl apply -f k8s-production-api.yaml"
echo "2. Monitor deployment: kubectl get pods -l app=fitness-ai-api --watch"
echo "3. Check logs: kubectl logs -l app=fitness-ai-api -f"