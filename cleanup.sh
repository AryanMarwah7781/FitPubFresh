#!/bin/bash

# Cleanup Script for AI Fitness EKS Cluster
# This script helps manage and clean up the cluster to control costs

set -e

CLUSTER_NAME="ai-fitness-dev"
REGION="us-east-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
}

# Function to show current cluster status
show_status() {
    log "Current cluster status:"
    echo ""
    
    # Check if cluster exists
    if ! eksctl get cluster --name="$CLUSTER_NAME" --region="$REGION" &> /dev/null; then
        warning "Cluster $CLUSTER_NAME not found in region $REGION"
        return 1
    fi
    
    echo "📊 Cluster: $CLUSTER_NAME"
    echo "🌍 Region: $REGION"
    echo ""
    
    # Show nodes
    echo "🖥️  Nodes:"
    kubectl get nodes -o wide 2>/dev/null || echo "   Unable to connect to cluster"
    echo ""
    
    # Show running workloads
    echo "🏗️  Running workloads:"
    kubectl get pods -A --field-selector=status.phase=Running 2>/dev/null | head -10 || echo "   Unable to get pod information"
    echo ""
    
    # Estimate current costs
    NODE_COUNT=$(kubectl get nodes --no-headers 2>/dev/null | wc -l || echo 0)
    DAILY_COST=$(echo "($NODE_COUNT * 0.5) + 2.4" | bc -l)
    echo "💰 Estimated daily cost: \$$(printf "%.2f" $DAILY_COST)"
    echo "📅 Estimated monthly cost: \$$(echo "$DAILY_COST * 30" | bc -l)"
}

# Function to scale down cluster
scale_down() {
    log "Scaling down cluster (keeping control plane)..."
    
    warning "This will scale all node groups to 0 nodes"
    warning "Workloads will be stopped but not deleted"
    warning "Control plane will continue running (~\$2.40/day)"
    
    read -p "Continue? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        log "Scale down cancelled"
        return 0
    fi
    
    # Scale down node groups
    log "Scaling down node groups..."
    
    # Get all node groups
    NODEGROUPS=$(eksctl get nodegroup --cluster="$CLUSTER_NAME" --region="$REGION" -o json | jq -r '.[].Name' 2>/dev/null || echo "")
    
    if [ -z "$NODEGROUPS" ]; then
        warning "No node groups found or unable to retrieve them"
        return 1
    fi
    
    for ng in $NODEGROUPS; do
        log "Scaling down node group: $ng"
        eksctl scale nodegroup --cluster="$CLUSTER_NAME" --region="$REGION" --name="$ng" --nodes=0 --wait
        success "Node group $ng scaled to 0"
    done
    
    success "Cluster scaled down successfully!"
    echo "💰 You're now only paying for the EKS control plane (~\$2.40/day)"
    echo "🔄 To scale back up, run: $0 --scale-up"
}

# Function to scale up cluster
scale_up() {
    log "Scaling up cluster..."
    
    # Scale up managed node group first (more reliable)
    log "Scaling up managed-workers node group to 1 node..."
    eksctl scale nodegroup --cluster="$CLUSTER_NAME" --region="$REGION" --name="managed-workers" --nodes=1 --wait
    success "Cluster scaled back up!"
    
    # Wait for nodes to be ready
    log "Waiting for nodes to be ready..."
    kubectl wait --for=condition=Ready nodes --all --timeout=300s
    success "Nodes are ready"
    
    # Check pod status
    log "Checking pod status..."
    kubectl get pods -A
}

# Function to delete test resources only
cleanup_test() {
    log "Cleaning up test resources..."
    
    warning "This will delete test applications but keep the cluster"
    read -p "Continue? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        log "Test cleanup cancelled"
        return 0
    fi
    
    # Delete test namespace and resources
    kubectl delete namespace test-apps --ignore-not-found=true
    success "Test resources cleaned up"
}

# Function to completely delete cluster
delete_cluster() {
    log "Preparing to delete cluster completely..."
    
    error "⚠️  DANGER ZONE ⚠️"
    echo ""
    echo "This will:"
    echo "❌ Delete the entire EKS cluster"
    echo "❌ Delete all worker nodes"  
    echo "❌ Delete all applications and data"
    echo "❌ Delete VPC and networking resources"
    echo "❌ Remove all associated AWS resources"
    echo ""
    echo "💰 This will stop ALL charges for this cluster"
    echo "⏰ This action CANNOT be undone"
    echo ""
    
    read -p "Type 'DELETE' to confirm complete cluster deletion: " confirm
    if [ "$confirm" != "DELETE" ]; then
        log "Cluster deletion cancelled"
        return 0
    fi
    
    read -p "Are you absolutely sure? Type 'YES': " final_confirm
    if [ "$final_confirm" != "YES" ]; then
        log "Cluster deletion cancelled"
        return 0
    fi
    
    log "Deleting cluster... This will take 10-15 minutes"
    eksctl delete cluster --name="$CLUSTER_NAME" --region="$REGION" --wait
    success "Cluster deleted successfully!"
    echo "💰 All charges for this cluster have stopped"
}

# Function to show help
show_help() {
    echo "AI Fitness EKS Cluster Cleanup Tool"
    echo "===================================="
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --status       Show current cluster status and costs"
    echo "  --scale-down   Scale cluster to 0 nodes (keep control plane)"
    echo "  --scale-up     Scale cluster back up to 1 node"
    echo "  --cleanup-test Delete only test applications"
    echo "  --delete       Completely delete the cluster (DESTRUCTIVE)"
    echo "  --help         Show this help message"
    echo ""
    echo "Cost Management:"
    echo "  Scale down when not in use: $0 --scale-down"
    echo "  Scale up when needed:      $0 --scale-up"
    echo "  Monitor costs regularly:    ./cost-monitoring.sh"
    echo ""
    echo "Examples:"
    echo "  $0 --status                # Check current status"
    echo "  $0 --scale-down           # Save money overnight"
    echo "  $0 --scale-up             # Resume work"
    echo ""
}

# Main function
main() {
    case "${1:-}" in
        --status)
            show_status
            ;;
        --scale-down)
            show_status
            echo ""
            scale_down
            ;;
        --scale-up)
            scale_up
            show_status
            ;;
        --cleanup-test)
            cleanup_test
            ;;
        --delete)
            show_status
            echo ""
            delete_cluster
            ;;
        --help)
            show_help
            ;;
        "")
            show_help
            echo ""
            show_status
            ;;
        *)
            error "Unknown option: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"