# AI Fitness Development EKS Cluster

A cost-optimized AWS EKS cluster setup for AI fitness application development and learning.

## 🏗️ Infrastructure Overview

- **Cluster Name**: `ai-fitness-dev`
- **Region**: `us-east-1`
- **Environment**: Development/Learning
- **Cost Optimization**: Spot instances, auto-scaling, minimal resources

### 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AWS EKS Cluster                      │
│                   ai-fitness-dev                        │
├─────────────────────────────────────────────────────────┤
│  Control Plane (Managed by AWS)                        │
│  ├── API Server                                        │
│  ├── etcd                                              │
│  └── Controller Manager                                │
├─────────────────────────────────────────────────────────┤
│  Worker Nodes (Auto-scaling: 1-4 nodes)                │
│  ├── Node Group: ai-fitness-workers (Spot)             │
│  ├── Instance Type: t3.medium                          │
│  ├── OS: Amazon Linux 2                                │
│  └── Storage: 20GB gp3 (encrypted)                     │
├─────────────────────────────────────────────────────────┤
│  Add-ons & Monitoring                                  │
│  ├── VPC CNI                                           │
│  ├── CoreDNS                                           │
│  ├── kube-proxy                                        │
│  ├── EBS CSI Driver                                    │
│  └── CloudWatch Logging                                │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI v2** with configured credentials
2. **eksctl** (>= 0.147.0)
3. **kubectl** (>= 1.28)
4. **Git** for version control

#### Install Prerequisites (macOS)

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Install eksctl
brew tap weaveworks/tap
brew install weaveworks/tap/eksctl

# Install kubectl
brew install kubectl

# Verify installations
aws --version
eksctl version
kubectl version --client
```

#### Configure AWS Credentials

```bash
# Option 1: AWS CLI configure
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 🏁 Cluster Deployment

#### Step 1: Clone and Setup

```bash
git clone https://github.com/AryanMarwah7781/FitPubFresh.git
cd FitPubFresh
git checkout feature/eks-cluster-setup
```

#### Step 2: Create the EKS Cluster

```bash
# Deploy the cluster (15-20 minutes)
eksctl create cluster -f cluster-config.yaml

# Verify cluster creation
kubectl get nodes
kubectl cluster-info
```

#### Step 3: Deploy Test Application

```bash
# Deploy hello-world test application
kubectl apply -f test-deployment.yaml

# Verify deployment
kubectl get pods -n test-apps
kubectl get services -n test-apps
```

#### Step 4: Test Cluster Functionality

```bash
# Port-forward to test application
kubectl port-forward -n test-apps service/hello-world-service 8080:80

# Open browser to http://localhost:8080
# You should see the AI Fitness Dev welcome page
```

## 💰 Cost Management

### Current Cost Estimate

| Resource | Quantity | Monthly Cost (USD) |
|----------|----------|-------------------|
| EKS Control Plane | 1 | ~$73.00 |
| t3.medium Spot Instances | 1-4 nodes | ~$15.00/node |
| EBS gp3 Storage | 20GB/node | ~$2.00/node |
| Data Transfer | Est. | ~$5.00 |
| **Total Estimated** | | **~$95-140/month** |

### 📊 Cost Monitoring

Run the cost monitoring script to track usage:

```bash
# Run cost monitoring dashboard
./cost-monitoring.sh

# Set up automated monitoring (optional)
chmod +x cost-monitoring.sh
```

### 💡 Cost Optimization Features

- ✅ **Spot Instances**: 60-90% savings on compute costs
- ✅ **Auto-scaling**: Scale down to 1 node when idle
- ✅ **Right-sized Storage**: 20GB gp3 volumes
- ✅ **Short Log Retention**: 7 days for CloudWatch logs
- ✅ **Resource Limits**: Prevent resource waste

### 🛑 Cost Control Commands

```bash
# Scale down cluster (keep control plane)
eksctl scale nodegroup --cluster=ai-fitness-dev --region=us-east-1 --name=managed-workers --nodes=0

# Scale back up
eksctl scale nodegroup --cluster=ai-fitness-dev --region=us-east-1 --name=managed-workers --nodes=1

# Complete cleanup (WARNING: Deletes everything)
eksctl delete cluster --name=ai-fitness-dev --region=us-east-1
```

## 🔧 Verification Commands

### Cluster Health Checks

```bash
# Check cluster status
kubectl get nodes -o wide
kubectl get pods -A
kubectl top nodes  # Requires metrics-server

# Check system pods
kubectl get pods -n kube-system

# Verify auto-scaling
kubectl get hpa -A
kubectl describe nodes

# Test DNS resolution
kubectl run test-dns --image=busybox --rm -it -- nslookup kubernetes.default
```

### Application Testing

```bash
# Check test deployment
kubectl get all -n test-apps

# View application logs
kubectl logs -n test-apps deployment/hello-world

# Test service connectivity
kubectl exec -n test-apps deployment/hello-world -- wget -qO- http://hello-world-service

# Check resource usage
kubectl top pods -n test-apps
```

### AWS Integration Testing

```bash
# Verify EBS CSI driver
kubectl get storageclass

# Check IAM roles and service accounts
kubectl get serviceaccounts -A
kubectl describe serviceaccount -n kube-system cluster-autoscaler

# Verify VPC and subnets
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=ai-fitness-dev-vpc"
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Cluster Creation Fails
```bash
# Check AWS credentials and permissions
aws sts get-caller-identity

# Verify required IAM permissions for eksctl
# Minimum required: EC2, EKS, CloudFormation, IAM permissions
```

#### 2. Nodes Not Ready
```bash
# Check node status
kubectl describe nodes

# Check system pods
kubectl get pods -n kube-system

# Verify security groups and networking
kubectl get events --sort-by=.metadata.creationTimestamp
```

#### 3. High Costs
```bash
# Run cost monitoring
./cost-monitoring.sh

# Check for unused resources
kubectl get pods -A --field-selector=status.phase=Pending
kubectl get pv | grep Available

# Scale down if needed
eksctl scale nodegroup --cluster=ai-fitness-dev --region=us-east-1 --name=managed-workers --nodes=1
```

### 📞 Getting Help

1. **AWS EKS Documentation**: https://docs.aws.amazon.com/eks/
2. **eksctl Documentation**: https://eksctl.io/
3. **Kubernetes Documentation**: https://kubernetes.io/docs/
4. **Cost Optimization Guide**: https://aws.amazon.com/eks/pricing/

## 🛡️ Security Considerations

- ✅ Private networking for worker nodes
- ✅ Encrypted EBS volumes
- ✅ Instance metadata service v2 (IMDSv2)
- ✅ RBAC enabled by default
- ✅ VPC security groups configured
- ⚠️ SSH access disabled by default (enable only if needed)

## 🔄 Next Steps

1. **Set up CI/CD pipeline** with GitHub Actions
2. **Configure monitoring** with Prometheus/Grafana
3. **Add ingress controller** for external access
4. **Implement GitOps** with ArgoCD or Flux
5. **Deploy sample AI applications**
6. **Set up development workflows**

## 📝 Development Workflow

This cluster follows GitOps principles:

```bash
# Feature development
git checkout -b feature/your-feature
# Make changes
git commit -m "feat: add your feature"
git push origin feature/your-feature
# Create Pull Request
```

## 🏷️ Tags and Labels

All resources are properly tagged for cost tracking:
- `Environment: development`
- `Project: ai-fitness`
- `CostCenter: development`
- `AutoShutdown: true`

## 📋 Maintenance

### Regular Tasks

- [ ] Weekly cost review using `./cost-monitoring.sh`
- [ ] Monthly security updates for nodes
- [ ] Quarterly cluster version updates
- [ ] Monitor and clean up unused resources

### Automated Cleanup

Consider setting up automated shutdown for nights/weekends to save costs:

```bash
# Example: Scale down at night (add to cron)
# 0 22 * * 1-5 eksctl scale nodegroup --cluster=ai-fitness-dev --region=us-east-1 --name=managed-workers --nodes=0
# 0 8 * * 1-5 eksctl scale nodegroup --cluster=ai-fitness-dev --region=us-east-1 --name=managed-workers --nodes=1
```

---

**⚡ Happy Learning and Building!** 🚀

This infrastructure is designed for learning and development. Remember to monitor costs and scale resources based on your actual usage.