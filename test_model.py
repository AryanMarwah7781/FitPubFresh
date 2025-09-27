#!/usr/bin/env python3
"""
Test script for AI Fitness model setup
Tests the Mistral 7B model configuration and basic functionality
"""

import os
import sys
from pathlib import Path

def test_environment_variables():
    """Test if environment variables are set correctly"""
    print("🔍 Testing Environment Variables...")
    
    model_path = os.getenv('MODEL_PATH')
    model_name = os.getenv('MODEL_NAME')
    
    if not model_path:
        print("❌ MODEL_PATH environment variable not set")
        return False
    
    if not model_name:
        print("❌ MODEL_NAME environment variable not set") 
        return False
        
    print(f"✅ MODEL_PATH: {model_path}")
    print(f"✅ MODEL_NAME: {model_name}")
    return True

def test_model_files():
    """Test if model files exist"""
    print("\n🔍 Testing Model Files...")
    
    model_path = os.getenv('MODEL_PATH', './models/mistral-7b-instruct')
    model_dir = Path(model_path)
    
    if not model_dir.exists():
        print(f"❌ Model directory does not exist: {model_dir}")
        return False
    
    print(f"✅ Model directory exists: {model_dir}")
    
    # Check for key model files
    required_files = [
        'config.json',
        'generation_config.json', 
        'tokenizer.json',
        'tokenizer.model'
    ]
    
    missing_files = []
    for file_name in required_files:
        file_path = model_dir / file_name
        if file_path.exists():
            print(f"✅ Found: {file_name}")
        else:
            print(f"❌ Missing: {file_name}")
            missing_files.append(file_name)
    
    # Check for model weights (safetensors files)
    safetensors_files = list(model_dir.glob("*.safetensors"))
    if safetensors_files:
        print(f"✅ Found {len(safetensors_files)} safetensors files")
        for file in safetensors_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"   - {file.name}: {size_mb:.1f} MB")
    else:
        print("❌ No safetensors model files found")
        missing_files.append("*.safetensors")
    
    return len(missing_files) == 0

def main():
    """Run basic tests"""
    print("🚀 AI Fitness Model Setup Test")
    print("=" * 50)
    
    # Load .env file if it exists
    env_file = Path('.env')
    if env_file.exists():
        print("📁 Loading .env file...")
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded")
    else:
        print("⚠️  No .env file found")
    
    # Run tests
    test_environment_variables()
    test_model_files()
    
    print("\n" + "=" * 50)
    print("📊 Test Complete")

if __name__ == "__main__":
    main()
