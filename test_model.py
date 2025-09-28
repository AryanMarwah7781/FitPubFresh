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

def test_python_environment():
    """Test Python environment and potential dependencies"""
    print("\n🔍 Testing Python Environment...")
    
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Python executable: {sys.executable}")
    
    # Try to import common ML libraries
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.device_count()} device(s)")
        else:
            print("ℹ️  CUDA not available (CPU mode)")
    except ImportError:
        print("⚠️  PyTorch not installed")
    
    try:
        import transformers
        print(f"✅ Transformers version: {transformers.__version__}")
    except ImportError:
        print("⚠️  Transformers not installed")
    
    try:
        import safetensors
        print(f"✅ SafeTensors available")
    except ImportError:
        print("⚠️  SafeTensors not installed")

def test_basic_model_loading():
    """Test basic model loading capabilities"""
    print("\n🔍 Testing Basic Model Loading...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        model_name = os.getenv('MODEL_NAME', 'mistralai/Mistral-7B-Instruct-v0.3')
        model_path = os.getenv('MODEL_PATH', './models/mistral-7b-instruct')
        
        print(f"Attempting to load tokenizer from: {model_path}")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print("✅ Tokenizer loaded successfully")
        
        # Test tokenization
        test_text = "Hello, this is a test for AI fitness application"
        tokens = tokenizer.encode(test_text)
        print(f"✅ Tokenization test passed: {len(tokens)} tokens")
        
        # Try to load model (this might take time and memory)
        print("⚠️  Note: Model loading test skipped to save time and memory")
        print("   To test model loading, uncomment the lines below")
        
        # Uncomment these lines to test actual model loading
        # print(f"Attempting to load model from: {model_path}")
        # model = AutoModelForCausalLM.from_pretrained(model_path)
        # print("✅ Model loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading test failed: {str(e)}")
        return False

def generate_test_requirements():
    """Generate a requirements.txt file for the project"""
    print("\n🔧 Generating requirements.txt...")
    
    requirements = [
        "torch>=2.0.0",
        "transformers>=4.30.0", 
        "safetensors>=0.3.0",
        "accelerate>=0.20.0",
        "scipy>=1.10.0",
        "numpy>=1.24.0",
        "tokenizers>=0.13.0"
    ]
    
    with open('requirements.txt', 'w') as f:
        for req in requirements:
            f.write(f"{req}\n")
    
    print("✅ requirements.txt generated")
    print("To install dependencies, run: pip install -r requirements.txt")

def main():
    """Run all tests"""
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
    tests = [
        test_environment_variables,
        test_model_files,
        test_python_environment,
        test_basic_model_loading
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append(False)
    
    # Generate requirements if needed
    if not Path('requirements.txt').exists():
        generate_test_requirements()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed!")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("❌ Some tests failed - check the output above")
    
    print("\n🔧 Next Steps:")
    if not Path('requirements.txt').exists():
        print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Set up proper Python virtual environment")
    print("3. Test model inference with sample fitness queries")
    print("4. Integrate with fitness application logic")

if __name__ == "__main__":
    main()