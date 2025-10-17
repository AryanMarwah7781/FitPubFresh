# Training Data Generation System

AI-powered training data generation using Claude API for fitness coaching model finetuning.

## Overview

This system generates high-quality, diverse training examples for finetuning Mistral-7B into a fitness specialist model.

### Features

- ✅ **Claude API Integration** - Uses Claude Sonnet 4 with prompt caching (90% cost savings)
- ✅ **Multi-Category Generation** - Workout programming, nutrition, form corrections, FAQs
- ✅ **Cost Optimized** - ~$18 for 1500 examples vs $25-30 with GPT-4
- ✅ **Quality Validation** - Automatic JSON parsing and validation
- ✅ **Batch Processing** - Efficient batch generation with progress tracking

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit `.env` file:

```bash
# Add your Claude API key
ANTHROPIC_API_KEY=your_key_here

# Add your HuggingFace token (for dataset upload)
HUGGINGFACE_TOKEN=your_token_here
```

## Usage

### Quick Start - Generate 200 Examples (Day 1)

```bash
python3 generate_dataset.py
```

This generates:
- 80 workout programming examples
- 50 nutrition advice examples
- 30 form correction examples
- 40 FAQ examples

**Cost:** ~$2-3
**Time:** ~15-20 minutes

### Full Dataset - Generate 1500 Examples (Day 2)

Edit `generate_dataset.py` and change counts:

```python
all_examples, client = await generate_all_data(
    num_workout=400,
    num_nutrition=300,
    num_form=200,
    num_faq=300,
    num_recovery=300  # To be implemented
)
```

**Cost:** ~$18-20
**Time:** ~90-120 minutes

## Project Structure

```
training/
├── config/
│   ├── claude_config.py      # Claude API configuration
│   ├── categories.py          # Data categories and distributions
│   └── prompts.py             # System prompts for generation
├── generators/
│   ├── claude_client.py       # Claude API wrapper
│   ├── workout_generator.py   # Workout programming examples
│   ├── nutrition_generator.py # Nutrition advice examples
│   ├── form_generator.py      # Form correction examples
│   └── faq_generator.py       # FAQ examples
├── data/                      # Generated datasets (gitignored)
├── generate_dataset.py        # Main generation script
└── requirements.txt
```

## Generated Data Format

Each example follows this structure:

```json
{
  "instruction": "Create a 4-day upper/lower split for muscle building",
  "input": "Experience: Intermediate (1.5 years), Goal: Hypertrophy, Equipment: Full gym, Limitations: None",
  "output": "Here's an optimized 4-day upper/lower split...",
  "category": "workout_programming",
  "difficulty": "intermediate",
  "tags": ["hypertrophy", "upper_lower", "intermediate"],
  "source": "claude_generated",
  "generator": "workout_programming"
}
```

## Cost Tracking

The system automatically tracks:
- Input/output tokens
- Cached tokens (90% cheaper)
- Total cost
- Cost per example
- Cache hit rate

Example output:

```
📊 Claude API Usage Statistics
==========================================
Total Requests: 200
Total Tokens: 320,000
  - Input: 150,000
  - Output: 140,000
  - Cached: 30,000

💰 Cost Breakdown:
  - Input Cost: $0.45
  - Cached Cost: $0.09
  - Output Cost: $2.10
  - Total Cost: $2.64
  - Avg per Request: $0.0132

⚡ Cache Performance: 20.0%
==========================================
```

## Next Steps

1. **Review Generated Data** - Check `data/` directory for quality
2. **Generate Full Dataset** - Run full generation for 1500 examples
3. **Upload to HuggingFace** - Use `datasets` library to upload
4. **Finetune Model** - Use dataset for QLoRA finetuning (Day 3-4)

## Troubleshooting

### API Key Issues

```bash
# Verify API key is set
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('ANTHROPIC_API_KEY')[:20] + '...')"
```

### JSON Parsing Errors

The system automatically handles:
- JSON wrapped in markdown code blocks
- Missing fields (uses defaults)
- Malformed responses (logs and skips)

### Rate Limiting

- Default: 50 requests/minute
- Automatic rate limiting built-in
- Adjust in `config/claude_config.py` if needed

## Development

### Testing Individual Generators

```bash
# Test workout generator
cd generators
python3 workout_generator.py

# Test Claude client
python3 claude_client.py
```

### Adding New Generators

1. Create new generator in `generators/`
2. Inherit from base pattern
3. Implement `create_context_variations()` and `generate_examples()`
4. Add to `generate_dataset.py`

## License

Part of FitPubFresh AI Fitness Assistant project.
