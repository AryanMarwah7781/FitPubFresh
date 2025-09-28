#!/bin/bash

# Setup Script for AI Fitness EKS Cluster
# This script automates the entire cluster setup process

set -e

CLUSTER_NAME="ai-fitness-dev"
REGION="us-east-1"
CONFIG_FILE="cluster-config.yaml"
TEST_FILE="test-deployment.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is not installed. Please install it first."
    fi
    success "AWS CLI found"
    
    # Check eksctl
    if ! command -v eksctl &> /dev/null; then
        error "eksctl is not installed. Please install it first."
    fi
    success "eksctl found"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed. Please install it first."
    fi
    success "kubectl found"
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured. Run 'aws configure' first."
    fi
    success "AWS credentials configured"
    
    # Check if cluster already exists
    if eksctl get cluster --name="$CLUSTER_NAME" --region="$REGION" &> /dev/null; then
        warning "Cluster $CLUSTER_NAME already exists!"
        echo "Do you want to:"
        echo "1) Continue with existing cluster"
        echo "2) Delete and recreate cluster"
        echo "3) Exit"
        read -p "Enter choice (1-3): " choice
        
        case $choice in
            1) 
                log "Using existing cluster..."
                return 0
                ;;
            2)
                log "Deleting existing cluster..."
                eksctl delete cluster --name="$CLUSTER_NAME" --region="$REGION" --wait
                ;;
            3)
                log "Exiting..."
                exit 0
                ;;
            *)
                error "Invalid choice"
                ;;
        esac
    fi
}

# Function to create cluster
create_cluster() {
    log "Creating EKS cluster: $CLUSTER_NAME"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        error "Cluster configuration file $CONFIG_FILE not found!"
    fi
    
    log "This will take approximately 15-20 minutes..."
    log "Cluster configuration:"
    echo "  - Name: $CLUSTER_NAME"
    echo "  - Region: $REGION"
    echo "  - Node Type: t3.medium (Spot instances)"
    echo "  - Initial Nodes: 2"
    echo "  - Auto-scaling: 1-4 nodes"
    
    read -p "Continue with cluster creation? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        log "Cluster creation cancelled"
        exit 0
    fi
    
    # Create cluster
    eksctl create cluster -f "$CONFIG_FILE"
    success "Cluster created successfully!"
    
    # Update kubeconfig
    aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER_NAME"
    success "kubeconfig updated"
}

# Function to verify cluster
verify_cluster() {
    log "Verifying cluster setup..."
    
    # Check nodes
    log "Checking nodes..."
    kubectl get nodes -o wide
    
    # Check system pods
    log "Checking system pods..."
    kubectl get pods -n kube-system
    
    # Wait for nodes to be ready
    log "Waiting for nodes to be ready..."
    kubectl wait --for=condition=Ready nodes --all --timeout=300s
    success "All nodes are ready"
    
    # Check cluster info
    kubectl cluster-info
    success "Cluster verification completed"
}

# Function to deploy test application
deploy_test_app() {
    log "Deploying test application..."
    
    if [ ! -f "$TEST_FILE" ]; then
        error "Test deployment file $TEST_FILE not found!"
    fi
    
    # Deploy test application
    kubectl apply -f "$TEST_FILE"
    
    # Wait for deployment to be ready
    log "Waiting for test application to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/hello-world -n test-apps
    success "Test application deployed successfully"
    
    # Show deployment status
    kubectl get all -n test-apps
}

# Function to setup monitoring
setup_monitoring() {
    log "Setting up basic monitoring..."
    
    # Install metrics server
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    
    # Wait for metrics server
    log "Waiting for metrics server to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/metrics-server -n kube-system
    success "Metrics server installed"
    
    # Test metrics
    log "Testing metrics (may take a few moments)..."
    sleep 30
    kubectl top nodes || warning "Metrics not yet available - try again in a few minutes"
}

# Function to run cost monitoring
run_cost_monitoring() {
    log "Running initial cost monitoring..."
    
    if [ -f "cost-monitoring.sh" ]; then
        ./cost-monitoring.sh
    else
        warning "Cost monitoring script not found"
    fi
}

# Function to show next steps
show_next_steps() {
    success "🎉 EKS Cluster Setup Complete!"
    echo ""
    echo "📋 Cluster Information:"
    echo "  - Name: $CLUSTER_NAME"
    echo "  - Region: $REGION"
    echo "  - Endpoint: $(kubectl cluster-info | grep 'control plane' | awk '{print $NF}')"
    echo ""
    echo "🧪 Test Your Cluster:"
    echo "  kubectl get nodes"
    echo "  kubectl get pods -n test-apps"
    echo "  kubectl port-forward -n test-apps service/hello-world-service 8080:80"
    echo "  # Then open http://localhost:8080"
    echo ""
    echo "💰 Monitor Costs:"
    echo "  ./cost-monitoring.sh"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  kubectl get all -A                    # View all resources"
    echo "  kubectl top nodes                     # Node resource usage"
    echo "  kubectl describe node <node-name>     # Node details"
    echo ""
    echo "⚠️  Remember to monitor costs and scale down when not in use:"
    echo "  eksctl scale nodegroup --cluster=$CLUSTER_NAME --region=$REGION --name=managed-workers --nodes=0"
    echo ""
    echo "📚 Next Steps:"
    echo "  1. Deploy your applications"
    echo "  2. Set up CI/CD pipelines"
    echo "  3. Configure ingress controller"
    echo "  4. Add monitoring and observability"
    echo "  5. Implement GitOps workflows"
}

# Main function
main() {
    echo ""
    echo "🚀 AI Fitness EKS Cluster Setup"
    echo "==============================="
    echo ""
    
    check_prerequisites
    create_cluster
    verify_cluster
    deploy_test_app
    setup_monitoring
    run_cost_monitoring
    show_next_steps
    
    success "Setup completed successfully! 🎉"
}

# Handle script interruption
trap 'error "Setup interrupted. You may need to clean up resources manually."' INT TERM

# Run main function
main "$@"