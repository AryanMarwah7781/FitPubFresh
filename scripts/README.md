# Container Registry Scripts - Day 3

This directory contains automated scripts for containerizing and deploying the Fitness AI FastAPI application to AWS ECR and EKS.

## 📋 Prerequisites

Before running these scripts, ensure you have:

- **AWS CLI v2** configured with appropriate permissions
- **Docker** installed and running
- **kubectl** configured for your EKS cluster
- **Bash shell** (macOS/Linux)

### Required AWS Permissions

Your AWS credentials need the following permissions:
- ECR: `ecr:*` (for repository management and image push/pull)
- EKS: `eks:DescribeCluster` (for cluster verification)
- STS: `sts:GetCallerIdentity` (for account ID retrieval)

## 🚀 Quick Start

### 1. Setup ECR Repository
```bash
./setup-ecr.sh
```
This will:
- Create the `fitness-ai-api` ECR repository in `us-east-1`
- Configure repository policies for EKS access
- Set up lifecycle policies for image cleanup
- Verify EKS cluster access

### 2. Build Docker Image
```bash
./build-image.sh [tag]
```
Example:
```bash
./build-image.sh v1.0.0
./build-image.sh latest  # default
```

This will:
- Build optimized multi-stage Docker image
- Tag for local use and ECR
- Run local health checks
- Display image information

### 3. Push to ECR
```bash
./push-image.sh [tag]
```
Example:
```bash
./push-image.sh v1.0.0
./push-image.sh latest  # default
```

This will:
- Authenticate Docker with ECR
- Push image to ECR repository
- Verify successful upload
- Provide deployment commands

### 4. Test EKS Deployment
```bash
./test-eks-deployment.sh [tag] [namespace]
```
Example:
```bash
./test-eks-deployment.sh latest default
./test-eks-deployment.sh v1.0.0 production
```

This will:
- Verify ECR image accessibility
- Test image pull on EKS cluster  
- Deploy test pod and service
- Test API endpoints
- Clean up test resources

## 📁 Script Details

### setup-ecr.sh
**Purpose**: Initialize AWS ECR repository for the Fitness AI API

**Features**:
- Creates ECR repository with encryption
- Configures security policies
- Sets up image lifecycle management
- Validates EKS cluster access

**Configuration**:
```bash
AWS_REGION="us-east-1"
REPOSITORY_NAME="fitness-ai-api"
CLUSTER_NAME="ai-fitness-dev"
```

### build-image.sh
**Purpose**: Build optimized Docker image for production deployment

**Features**:
- Multi-stage Docker build for size optimization
- Platform-specific build (linux/amd64)
- Local health testing
- Multiple image tagging

**Build Arguments**:
- `BUILDTIME`: Current timestamp
- `VERSION`: Image tag/version

**Tags Created**:
- `fitness-ai-api:latest`
- `fitness-ai-api:{tag}`
- `{ecr-registry}/fitness-ai-api:{tag}`

### push-image.sh  
**Purpose**: Push Docker image to AWS ECR

**Features**:
- ECR authentication
- Image verification before push
- Progress tracking and timing
- Repository status reporting

**Verification**:
- Checks local image exists
- Validates ECR repository exists  
- Confirms successful push
- Lists available images

### test-eks-deployment.sh
**Purpose**: Validate containerized app works in EKS

**Test Steps**:
1. **Image Pull Test**: Verify EKS can pull from ECR
2. **Deployment Test**: Create test deployment and service
3. **Health Checks**: Test liveness and readiness probes
4. **API Testing**: Verify endpoints respond correctly
5. **Cleanup**: Remove test resources

## 🔧 Configuration

### Environment Variables
You can customize behavior with environment variables:

```bash
# AWS Configuration
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID="123456789012"

# Repository Configuration  
export REPOSITORY_NAME="fitness-ai-api"
export CLUSTER_NAME="ai-fitness-dev"

# Docker Configuration
export DOCKER_BUILDKIT=1  # Enable BuildKit for faster builds
```

### Dockerfile Configuration
The Dockerfile supports these build arguments:
- `BUILDTIME`: Build timestamp
- `VERSION`: Application version
- `ENVIRONMENT`: Target environment

## 🔍 Troubleshooting

### Common Issues

#### 1. AWS Authentication Failed
```bash
# Check AWS credentials
aws sts get-caller-identity

# Configure AWS CLI
aws configure
```

#### 2. Docker Build Failed
```bash
# Check Docker daemon
docker info

# Clear Docker cache
docker system prune -a
```

#### 3. ECR Push Failed
```bash
# Re-authenticate with ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin {account-id}.dkr.ecr.us-east-1.amazonaws.com

# Check repository exists
aws ecr describe-repositories --repository-names fitness-ai-api
```

#### 4. EKS Access Issues
```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name ai-fitness-dev

# Test cluster connectivity
kubectl cluster-info
```

#### 5. Image Pull Errors in EKS
- Verify ECR repository policies allow EKS access
- Check EKS node group IAM roles have ECR permissions
- Ensure image exists in ECR repository

### Debugging Commands

```bash
# Check ECR images
aws ecr list-images --repository-name fitness-ai-api

# View EKS node permissions
kubectl describe nodes

# Check pod events
kubectl describe pod {pod-name}

# View application logs
kubectl logs -l app=fitness-ai-api
```

## 📊 Monitoring

### Image Size Optimization
The multi-stage Dockerfile optimizes for:
- **Base Image**: `python:3.9-slim` (~45MB)
- **Dependencies**: Virtual environment isolation
- **Security**: Non-root user execution
- **Performance**: Minimal runtime dependencies

### Resource Usage
Default pod resources:
- **Requests**: 256Mi memory, 200m CPU
- **Limits**: 512Mi memory, 500m CPU
- **Health Checks**: 30s liveness, 10s readiness

## 🔄 CI/CD Integration

These scripts are designed for:
- **Local Development**: Manual execution
- **GitHub Actions**: Automated builds on push
- **GitOps**: ArgoCD/Flux integration
- **Production**: Blue/green deployments

### Example GitHub Actions Usage
```yaml
- name: Build and Push to ECR
  run: |
    ./scripts/setup-ecr.sh
    ./scripts/build-image.sh ${{ github.sha }}
    ./scripts/push-image.sh ${{ github.sha }}
    ./scripts/test-eks-deployment.sh ${{ github.sha }}
```

## 📝 Next Steps

After successful containerization:

1. **Production Deployment**: Update image tag in `k8s-production-api.yaml`
2. **Monitoring**: Add Prometheus metrics and Grafana dashboards
3. **Scaling**: Implement HPA (Horizontal Pod Autoscaler)
4. **Security**: Add network policies and security contexts
5. **Persistence**: Add database and persistent storage
6. **CI/CD**: Set up automated deployment pipelines

## 🏷️ Version Management

Recommended tagging strategy:
- `latest`: Current development build
- `v1.0.0`: Semantic versioning for releases
- `prod-{timestamp}`: Production deployments
- `staging-{branch}`: Feature branch testing

## 🆘 Support

For issues with these scripts:
1. Check script logs for specific error messages
2. Verify AWS permissions and connectivity
3. Test Docker and kubectl functionality
4. Review EKS cluster status and node health
5. Validate ECR repository configuration

Remember to clean up test resources and monitor AWS costs! 💰