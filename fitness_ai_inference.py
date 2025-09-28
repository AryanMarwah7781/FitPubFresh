#!/usr/bin/env python3
"""
AI Fitness Model Inference Script
Uses Transformers library to run the Mistral 7B model for fitness-related queries
"""

import os
import sys
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_environment():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        print("📁 Loading environment variables...")
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Environment loaded")
    else:
        print("⚠️  No .env file found")
        
    return os.getenv('MODEL_PATH', './models/mistral-7b-instruct')

def check_system_resources():
    """Check available system resources"""
    print("\n🔍 System Resource Check:")
    print(f"Python version: {sys.version}")
    
    # Check PyTorch and device
    print(f"PyTorch version: {torch.__version__}")
    
    if torch.cuda.is_available():
        print(f"✅ CUDA available: {torch.cuda.device_count()} GPU(s)")
        device = "cuda"
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        print("✅ Apple Metal Performance Shaders (MPS) available")
        device = "mps"
    else:
        print("ℹ️  Using CPU (will be slower)")
        device = "cpu"
    
    return device

def load_model(model_path, device="cpu"):
    """Load the Mistral model and tokenizer"""
    print(f"\n🤖 Loading model from: {model_path}")
    
    try:
        # Load tokenizer
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        print("✅ Tokenizer loaded successfully")
        
        # Load model
        print("Loading model... (this may take a few minutes)")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if device != "cpu" else torch.float32,
            device_map="auto" if device != "cpu" else None,
            low_cpu_mem_usage=True
        )
        
        if device == "cpu":
            model = model.to(device)
            
        print("✅ Model loaded successfully")
        
        return model, tokenizer
        
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None, None

def generate_fitness_response(model, tokenizer, prompt, max_length=200):
    """Generate a fitness-related response"""
    try:
        # Format prompt for instruction following
        formatted_prompt = f"[INST] {prompt} [/INST]"
        
        # Tokenize
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        
        # Move to same device as model
        if next(model.parameters()).device != inputs.input_ids.device:
            inputs = {k: v.to(next(model.parameters()).device) for k, v in inputs.items()}
        
        # Generate
        print("🧠 Generating response...")
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_length=len(inputs.input_ids[0]) + max_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                num_return_sequences=1
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated part
        generated_text = response[len(formatted_prompt):].strip()
        
        return generated_text
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return None

def main():
    """Main function to test model inference"""
    print("🏋️ AI Fitness Model Inference Test")
    print("=" * 50)
    
    # Load environment and check resources
    model_path = load_environment()
    device = check_system_resources()
    
    # Verify model files exist
    model_dir = Path(model_path)
    if not model_dir.exists():
        print(f"❌ Model directory not found: {model_path}")
        return
    
    # Load model
    model, tokenizer = load_model(model_path, device)
    if model is None or tokenizer is None:
        print("❌ Failed to load model. Cannot continue.")
        return
    
    # Test fitness-related prompts
    fitness_prompts = [
        "Create a 20-minute HIIT workout plan for beginners",
        "What are the best exercises for building core strength?",
        "Suggest a healthy meal plan for muscle building",
        "How many calories should I eat to lose 1 pound per week?"
    ]
    
    print(f"\n🎯 Testing {len(fitness_prompts)} fitness prompts:")
    print("=" * 50)
    
    for i, prompt in enumerate(fitness_prompts, 1):
        print(f"\n📝 Prompt {i}: {prompt}")
        print("-" * 40)
        
        response = generate_fitness_response(model, tokenizer, prompt)
        
        if response:
            print(f"🤖 Response: {response}")
        else:
            print("❌ No response generated")
        
        print()
    
    print("🎉 Model inference test completed!")
    print("\n💡 Usage tips:")
    print("1. Model responses may take time on CPU")
    print("2. For production, consider GPU acceleration") 
    print("3. Adjust max_length for longer/shorter responses")
    print("4. Fine-tune prompts for better fitness-specific responses")

if __name__ == "__main__":
    main()