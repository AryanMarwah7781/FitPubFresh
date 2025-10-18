"""
HuggingFace Dataset Upload Script
Upload generated training data to HuggingFace Hub
"""

import json
import os
from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi, login
from dotenv import load_dotenv

load_dotenv()


def upload_dataset_to_hf(
    dataset_path: str,
    repo_name: str = "aryanmarwah/fitness-training-data",
    private: bool = False
):
    """
    Upload dataset to HuggingFace Hub

    Args:
        dataset_path: Path to the JSON dataset file
        repo_name: HuggingFace repo name (username/dataset-name)
        private: Whether to make the dataset private
    """
    print(f"\n🚀 Uploading Dataset to HuggingFace Hub\n")
    print("="*60)

    # 1. Check HuggingFace token
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    if not hf_token:
        print("❌ HUGGINGFACE_TOKEN not found in .env file")
        print("\n📝 To get your token:")
        print("1. Visit: https://huggingface.co/settings/tokens")
        print("2. Create a new token with 'write' access")
        print("3. Add to .env file: HUGGINGFACE_TOKEN=your_token_here")
        return

    # 2. Login to HuggingFace
    try:
        login(token=hf_token)
        print("✅ Logged in to HuggingFace")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return

    # 3. Load dataset
    print(f"\n📂 Loading dataset from: {dataset_path}")
    try:
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} examples")
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        return

    # 4. Convert to HuggingFace Dataset format
    print("\n🔄 Converting to HuggingFace Dataset format...")

    # Separate data by category for splits
    categories = {}
    for example in data:
        cat = example.get("category", "unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(example)

    # Create train/validation split (90/10)
    train_data = []
    val_data = []

    for cat, examples in categories.items():
        split_idx = int(len(examples) * 0.9)
        train_data.extend(examples[:split_idx])
        val_data.extend(examples[split_idx:])

    print(f"  Train: {len(train_data)} examples")
    print(f"  Validation: {len(val_data)} examples")

    # Create HuggingFace datasets
    train_dataset = Dataset.from_list(train_data)
    val_dataset = Dataset.from_list(val_data)

    dataset_dict = DatasetDict({
        "train": train_dataset,
        "validation": val_dataset
    })

    # 5. Add dataset metadata
    print("\n📝 Adding dataset metadata...")

    dataset_card = f"""
# Fitness Training Data

AI-powered fitness coaching training dataset for finetuning language models.

## Dataset Description

This dataset contains high-quality, diverse training examples for fitness coaching across multiple categories:

- **Workout Programming**: {sum(1 for d in data if d.get('category') == 'workout_programming')} examples
- **Nutrition Advice**: {sum(1 for d in data if d.get('category') == 'nutrition_advice')} examples
- **Form Corrections**: {sum(1 for d in data if d.get('category') == 'form_corrections')} examples
- **Recovery & Injury**: {sum(1 for d in data if d.get('category') == 'recovery_injury')} examples
- **FAQ**: {sum(1 for d in data if d.get('category') == 'faq')} examples

**Total Examples**: {len(data)}

## Dataset Format

Each example contains:
- `instruction`: The user's question or request
- `input`: Relevant context (experience level, goals, limitations, stats, etc.)
- `output`: Detailed expert response (300-800 words)
- `category`: Category of the example
- `difficulty`: beginner | intermediate | advanced
- `tags`: Relevant topic tags
- `source`: claude_generated
- `generator`: Specific generator used

## Example

```json
{{
  "instruction": "Create a 4-day upper/lower split for muscle building",
  "input": "Experience: Intermediate (1.5 years), Goal: Hypertrophy, Equipment: Full gym",
  "output": "Here's an optimized 4-day upper/lower hypertrophy split...\\n\\n**Upper Day 1:**\\n...",
  "category": "workout_programming",
  "difficulty": "intermediate",
  "tags": ["hypertrophy", "upper_lower", "intermediate"]
}}
```

## Usage

### Load with datasets library

```python
from datasets import load_dataset

dataset = load_dataset("{repo_name}")

# Access train split
train_data = dataset["train"]

# Access validation split
val_data = dataset["validation"]
```

### Finetuning Example

```python
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from trl import SFTTrainer

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")

# Load dataset
dataset = load_dataset("{repo_name}")

# Format for training
def format_instruction(example):
    return f"<s>[INST] {{example['instruction']}}\\n{{example['input']}} [/INST]\\n{{example['output']}}</s>"

# Train
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    dataset_text_field="text",  # After formatting
    max_seq_length=2048,
)
```

## Dataset Statistics

- **Average Output Length**: ~500 words
- **Categories**: 5
- **Difficulty Levels**: Beginner, Intermediate, Advanced
- **Training Split**: 90%
- **Validation Split**: 10%

## Data Generation

Generated using Claude Sonnet 4 with carefully crafted system prompts to ensure:
- Evidence-based fitness information
- Specific, actionable recommendations
- Proper safety disclaimers
- Diverse context variations
- Natural language instructions

## License

MIT License - Free to use for research and commercial applications

## Citation

```bibtex
@dataset{{fitness_training_data_2025,
  title={{Fitness Training Data}},
  author={{Aryan Marwah}},
  year={{2025}},
  publisher={{HuggingFace}},
  url={{https://huggingface.co/datasets/{repo_name}}}
}}
```

## Contact

For questions or issues, please open an issue on the [GitHub repository](https://github.com/AryanMarwah7781/FitPubFresh).
"""

    # 6. Upload to HuggingFace Hub
    print(f"\n⬆️  Uploading to HuggingFace Hub: {repo_name}")
    print(f"  Privacy: {'Private' if private else 'Public'}")

    try:
        dataset_dict.push_to_hub(
            repo_name,
            private=private,
            token=hf_token
        )
        print(f"\n✅ Successfully uploaded dataset!")
        print(f"\n🔗 View your dataset at:")
        print(f"   https://huggingface.co/datasets/{repo_name}")

        # Upload dataset card
        api = HfApi()
        api.upload_file(
            path_or_fileobj=dataset_card.encode(),
            path_in_repo="README.md",
            repo_id=repo_name,
            repo_type="dataset",
            token=hf_token
        )
        print(f"\n📝 Dataset card uploaded")

    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        print("\n💡 Common issues:")
        print("  - Repository name already exists (use different name)")
        print("  - Token doesn't have write permissions")
        print("  - Network connectivity issues")
        return

    print("\n" + "="*60)
    print("\n🎉 Dataset Upload Complete!")
    print("\n📋 Next Steps:")
    print("1. View dataset on HuggingFace")
    print("2. Test loading: from datasets import load_dataset; load_dataset('" + repo_name + "')")
    print("3. Use for model finetuning (Day 3-4)")
    print("="*60 + "\n")


def upload_latest_dataset():
    """Upload the most recent generated dataset"""
    data_dir = "data"

    # Find latest dataset file
    if not os.path.exists(data_dir):
        print(f"❌ Data directory '{data_dir}' not found")
        print("💡 Run 'python3 generate_dataset.py' first to generate data")
        return

    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json') and f.startswith('fitness_training_data_')]

    if not json_files:
        print(f"❌ No dataset files found in '{data_dir}'")
        print("💡 Run 'python3 generate_dataset.py' first to generate data")
        return

    # Sort by name (which includes timestamp)
    latest_file = sorted(json_files)[-1]
    file_path = os.path.join(data_dir, latest_file)

    print(f"📂 Found latest dataset: {latest_file}")

    # Ask for confirmation
    repo_name = input("\n🏷️  Enter HuggingFace repo name (default: aryanmarwah/fitness-training-data): ").strip()
    if not repo_name:
        repo_name = "aryanmarwah/fitness-training-data"

    private = input("🔒 Make dataset private? (y/N): ").strip().lower() == 'y'

    # Upload
    upload_dataset_to_hf(file_path, repo_name, private)


if __name__ == "__main__":
    upload_latest_dataset()
