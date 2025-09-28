#!/bin/bash

# Cost Monitoring Script for AI Fitness EKS Cluster
# This script helps monitor and manage costs for the development environment

set -e

CLUSTER_NAME="ai-fitness-dev"
REGION="us-east-1"
NAMESPACE="cost-monitoring"

echo "🔍 AI Fitness EKS Cost Monitoring Dashboard"
echo "==========================================="

# Function to check if required tools are installed
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI not found. Please install it first."
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl not found. Please install it first."
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Function to get cluster cost information
get_cluster_costs() {
    echo ""
    echo "💰 Current Cluster Resource Usage"
    echo "================================="
    
    # Get node information
    echo "📊 Node Information:"
    kubectl get nodes -o wide --show-labels
    
    echo ""
    echo "📈 Resource Usage by Node:"
    kubectl top nodes 2>/dev/null || echo "⚠️  Metrics server not available - install it for detailed metrics"
    
    echo ""
    echo "🏗️  Workload Distribution:"
    kubectl get pods -A -o wide
    
    echo ""
    echo "💾 Persistent Volume Usage:"
    kubectl get pv,pvc -A
}

# Function to estimate costs
estimate_costs() {
    echo ""
    echo "💲 Cost Estimation (USD/month)"
    echo "=============================="
    
    # Get node count and types
    NODE_COUNT=$(kubectl get nodes --no-headers | wc -l)
    
    echo "🖥️  EKS Control Plane: ~$73.00/month"
    echo "🔧 Worker Nodes ($NODE_COUNT x t3.medium spot): ~$$(echo "$NODE_COUNT * 15" | bc).00/month"
    echo "💾 EBS Storage (20GB per node): ~$$(echo "$NODE_COUNT * 2" | bc).00/month"
    echo "📡 Data Transfer: ~$5.00/month (estimated)"
    
    TOTAL_ESTIMATE=$(echo "$NODE_COUNT * 17 + 78" | bc)
    echo "📊 Total Estimated Cost: ~$${TOTAL_ESTIMATE}.00/month"
    
    echo ""
    echo "💡 Cost Optimization Tips:"
    echo "- Using Spot instances (60-90% savings on compute)"
    echo "- Auto-scaling configured (1-4 nodes)"
    echo "- gp3 volumes for better cost/performance"
    echo "- Short log retention (7 days)"
    echo "- Consider stopping cluster when not in use"
}

# Function to check for cost optimization opportunities
check_optimization() {
    echo ""
    echo "🔍 Cost Optimization Check"
    echo "========================="
    
    # Check for unused resources
    echo "🔄 Checking for optimization opportunities..."
    
    # Check pod resource requests vs limits
    echo "📊 Resource Efficiency:"
    kubectl top pods -A 2>/dev/null | head -10 || echo "⚠️  Install metrics-server for detailed analysis"
    
    # Check for pending pods (might indicate over-provisioning)
    PENDING_PODS=$(kubectl get pods -A --field-selector=status.phase=Pending --no-headers | wc -l)
    if [ "$PENDING_PODS" -gt 0 ]; then
        echo "⚠️  $PENDING_PODS pending pods found - check resource requests"
    else
        echo "✅ No pending pods - good resource allocation"
    fi
    
    # Check for empty namespaces
    echo ""
    echo "🏷️  Namespace Usage:"
    kubectl get namespaces --no-headers | while read ns rest; do
        POD_COUNT=$(kubectl get pods -n "$ns" --no-headers 2>/dev/null | wc -l)
        echo "   $ns: $POD_COUNT pods"
    done
}

# Function to set up cost alerts (CloudWatch)
setup_cost_alerts() {
    echo ""
    echo "🚨 Setting up Cost Alerts"
    echo "========================"
    
    # Create CloudWatch alarm for billing
    aws cloudwatch put-metric-alarm \
        --region "$REGION" \
        --alarm-name "EKS-ai-fitness-dev-cost-alert" \
        --alarm-description "Alert when EKS costs exceed $100/month" \
        --metric-name EstimatedCharges \
        --namespace AWS/Billing \
        --statistic Maximum \
        --period 86400 \
        --threshold 100 \
        --comparison-operator GreaterThanThreshold \
        --dimensions Name=Currency,Value=USD Name=ServiceName,Value=AmazonEKS \
        --evaluation-periods 1 \
        --treat-missing-data notBreaching \
        --alarm-actions "arn:aws:sns:$REGION:$(aws sts get-caller-identity --query Account --output text):eks-cost-alerts" \
        2>/dev/null && echo "✅ Cost alert configured (if SNS topic exists)" || echo "⚠️  Cost alert setup requires SNS topic configuration"
}

# Function to show cleanup commands
show_cleanup_commands() {
    echo ""
    echo "🧹 Cleanup Commands (to avoid ongoing costs)"
    echo "============================================"
    echo ""
    echo "To temporarily stop the cluster (delete nodes, keep control plane):"
    echo "   eksctl scale nodegroup --cluster=$CLUSTER_NAME --region=$REGION --name=ai-fitness-workers --nodes=0"
    echo "   eksctl scale nodegroup --cluster=$CLUSTER_NAME --region=$REGION --name=managed-workers --nodes=0"
    echo ""
    echo "To restart the cluster:"
    echo "   eksctl scale nodegroup --cluster=$CLUSTER_NAME --region=$REGION --name=managed-workers --nodes=1"
    echo ""
    echo "To completely delete the cluster:"
    echo "   eksctl delete cluster --name=$CLUSTER_NAME --region=$REGION"
    echo ""
    echo "⚠️  WARNING: Complete deletion will remove all data and configurations!"
}

# Main execution
main() {
    check_prerequisites
    
    echo ""
    echo "🎯 Monitoring cluster: $CLUSTER_NAME in $REGION"
    
    # Check if cluster is accessible
    if ! kubectl cluster-info &>/dev/null; then
        echo "❌ Cannot connect to cluster. Make sure:"
        echo "   1. Cluster is created and running"
        echo "   2. kubectl is configured: aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME"
        exit 1
    fi
    
    get_cluster_costs
    estimate_costs
    check_optimization
    setup_cost_alerts
    show_cleanup_commands
    
    echo ""
    echo "🎉 Cost monitoring check complete!"
    echo "💡 Run this script regularly to keep track of your cluster costs."
    echo "📅 Consider setting up a cron job to run this weekly."
}

# Run the script
main "$@"