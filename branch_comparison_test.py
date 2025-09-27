#!/usr/bin/env python3
"""
Comprehensive test script for FitPubFresh project
Tests both feature branches: model-setup and eks-cluster-setup
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run shell command and return result"""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def test_git_branches():
    """Test git branch structure"""
    print("🔍 Testing Git Branch Structure...")
    
    success, branches, error = run_command("git branch -a")
    if not success:
        print(f"❌ Failed to get git branches: {error}")
        return False
    
    expected_branches = ['main', 'feature/model-setup', 'feature/eks-cluster-setup']
    found_branches = []
    
    for line in branches.split('\n'):
        branch = line.strip().replace('*', '').strip()
        if branch.startswith('remotes/'):
            branch = branch.replace('remotes/origin/', '')
        if branch in expected_branches:
            found_branches.append(branch)
    
    for branch in expected_branches:
        if branch in found_branches:
            print(f"✅ Found branch: {branch}")
        else:
            print(f"❌ Missing branch: {branch}")
    
    return len(found_branches) >= 2

def test_model_setup_branch():
    """Test the model-setup branch"""
    print("\n🔍 Testing Feature: model-setup branch...")
    
    # Check if we're on the right branch
    success, current_branch, _ = run_command("git branch --show-current")
    if 'model-setup' not in current_branch:
        print("⚠️  Not on model-setup branch, checking out...")
        success, _, error = run_command("git checkout feature/model-setup")
        if not success:
            print(f"❌ Failed to checkout model-setup branch: {error}")
            return False
    
    # Test .env file
    if Path('.env').exists():
        print("✅ .env file exists")
        with open('.env') as f:
            content = f.read()
            if 'MODEL_PATH' in content and 'MODEL_NAME' in content:
                print("✅ Environment variables configured")
            else:
                print("❌ Environment variables not properly configured")
    else:
        print("❌ .env file missing")
        return False
    
    # Test model files
    model_path = Path('./models/mistral-7b-instruct')
    if model_path.exists():
        print("✅ Model directory exists")
        
        # Check key files
        key_files = ['config.json', 'tokenizer.json', 'tokenizer.model']
        missing_files = []
        for file_name in key_files:
            if (model_path / file_name).exists():
                print(f"✅ Found: {file_name}")
            else:
                print(f"❌ Missing: {file_name}")
                missing_files.append(file_name)
        
        # Check model weights
        safetensors_files = list(model_path.glob("*.safetensors"))
        if safetensors_files:
            total_size = sum(f.stat().st_size for f in safetensors_files) / (1024**3)
            print(f"✅ Found {len(safetensors_files)} model files ({total_size:.1f} GB)")
        else:
            print("❌ No model weight files found")
            missing_files.append("model weights")
        
        return len(missing_files) == 0
    else:
        print("❌ Model directory does not exist")
        return False

def test_eks_cluster_branch():
    """Test the eks-cluster-setup branch"""
    print("\n🔍 Testing Feature: eks-cluster-setup branch...")
    
    # Checkout EKS branch
    success, _, error = run_command("git checkout feature/eks-cluster-setup")
    if not success:
        print(f"❌ Failed to checkout eks-cluster-setup branch: {error}")
        return False
    
    print("✅ Switched to eks-cluster-setup branch")
    
    # Check key files
    key_files = [
        'cluster-config.yaml',
        'setup.sh', 
        'cleanup.sh',
        'test-deployment.yaml',
        'cost-monitoring.sh'
    ]
    
    missing_files = []
    for file_name in key_files:
        if Path(file_name).exists():
            print(f"✅ Found: {file_name}")
        else:
            print(f"❌ Missing: {file_name}")
            missing_files.append(file_name)
    
    # Check if scripts are executable
    executable_files = ['setup.sh', 'cleanup.sh', 'cost-monitoring.sh']
    for file_name in executable_files:
        file_path = Path(file_name)
        if file_path.exists() and os.access(file_path, os.X_OK):
            print(f"✅ {file_name} is executable")
        elif file_path.exists():
            print(f"⚠️  {file_name} exists but not executable")
        
    return len(missing_files) == 0

def test_aws_connectivity():
    """Test AWS connectivity and EKS cluster"""
    print("\n🔍 Testing AWS Connectivity...")
    
    # Test AWS CLI
    success, output, error = run_command("aws sts get-caller-identity")
    if success:
        try:
            identity = json.loads(output)
            print(f"✅ AWS CLI configured - Account: {identity.get('Account')}")
            print(f"   User: {identity.get('Arn', 'Unknown')}")
        except:
            print("✅ AWS CLI working but couldn't parse identity")
    else:
        print(f"❌ AWS CLI not configured: {error}")
        return False
    
    # Test EKS cluster
    success, output, error = run_command("aws eks list-clusters --region us-east-1")
    if success:
        try:
            clusters = json.loads(output)
            cluster_list = clusters.get('clusters', [])
            if 'ai-fitness-dev' in cluster_list:
                print("✅ EKS cluster 'ai-fitness-dev' exists")
                
                # Check cluster status
                success, status_output, _ = run_command(
                    "aws eks describe-cluster --name ai-fitness-dev --region us-east-1 --query 'cluster.status'"
                )
                if success:
                    status = status_output.strip('"')
                    print(f"✅ Cluster status: {status}")
                    
                    # Check nodes
                    success, _, _ = run_command("kubectl get nodes")
                    if success:
                        print("✅ kubectl can connect to cluster")
                    else:
                        print("⚠️  kubectl connection issues (nodes may still be starting)")
                else:
                    print("⚠️  Could not get cluster status")
            else:
                print("⚠️  EKS cluster 'ai-fitness-dev' not found")
                print(f"   Available clusters: {cluster_list}")
        except:
            print("❌ Could not parse EKS cluster list")
            return False
    else:
        print(f"❌ Could not list EKS clusters: {error}")
        return False
    
    return True

def main():
    """Run comprehensive tests"""
    print("🚀 FitPubFresh Branch Comparison Test")
    print("=" * 60)
    
    tests = [
        ("Git Branch Structure", test_git_branches),
        ("Model Setup Feature", test_model_setup_branch),
        ("EKS Cluster Feature", test_eks_cluster_branch),
        ("AWS Connectivity", test_aws_connectivity)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30} {status}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nOverall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All tests passed! Both features are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the details above.")
    
    print("\n�� Next Steps:")
    print("1. For model-setup: Test actual model inference")
    print("2. For eks-cluster: Wait for nodes to start and deploy test app")
    print("3. Integrate both features for AI model deployment on EKS")

if __name__ == "__main__":
    main()
