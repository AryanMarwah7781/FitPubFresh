"""
Main Training Data Generation Script
Generates complete dataset using all generators
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict

from generators.claude_client import ClaudeClient
from generators.workout_generator import WorkoutGenerator
from generators.nutrition_generator import NutritionGenerator
from generators.form_generator import FormCorrectionGenerator
from generators.faq_generator import FAQGenerator


async def generate_all_data(
    num_workout: int = 400,
    num_nutrition: int = 300,
    num_form: int = 200,
    num_faq: int = 300,
    num_recovery: int = 300
) -> Dict[str, List]:
    """
    Generate all training data

    Args:
        num_workout: Number of workout programming examples
        num_nutrition: Number of nutrition advice examples
        num_form: Number of form correction examples
        num_faq: Number of FAQ examples
        num_recovery: Number of recovery/injury examples

    Returns:
        Dictionary with all generated examples
    """
    print("="*60)
    print("🚀 FitPub Training Data Generation")
    print("="*60)
    print(f"Target: {num_workout + num_nutrition + num_form + num_faq + num_recovery} total examples\n")

    # Initialize client
    client = ClaudeClient()

    # Initialize generators
    workout_gen = WorkoutGenerator(client)
    nutrition_gen = NutritionGenerator(client)
    form_gen = FormCorrectionGenerator(client)
    faq_gen = FAQGenerator(client)

    all_examples = {
        "workout_programming": [],
        "nutrition_advice": [],
        "form_corrections": [],
        "faq": [],
        "recovery_injury": []
    }

    # Generate workout programming examples
    if num_workout > 0:
        all_examples["workout_programming"] = await workout_gen.generate_examples(num_workout)

    # Generate nutrition advice examples
    if num_nutrition > 0:
        all_examples["nutrition_advice"] = await nutrition_gen.generate_examples(num_nutrition)

    # Generate form correction examples
    if num_form > 0:
        all_examples["form_corrections"] = await form_gen.generate_examples(num_form)

    # Generate FAQ examples
    if num_faq > 0:
        all_examples["faq"] = await faq_gen.generate_examples(num_faq)

    # TODO: Recovery/injury generator (similar to form corrections)
    # For now, we'll skip this and adjust totals

    return all_examples, client


async def main():
    """Main execution function"""

    # Start with smaller batch for Day 1
    # Full dataset: 400 workout, 300 nutrition, 200 form, 300 faq, 300 recovery = 1500
    # Day 1 target: 200 examples for testing

    print("\n📅 DAY 1: Initial Generation (200 examples)\n")

    # Generate smaller batch for testing
    all_examples, client = await generate_all_data(
        num_workout=80,  # 40% of total
        num_nutrition=50,  # 25% of total
        num_form=30,  # 15% of total
        num_faq=40,  # 20% of total
        num_recovery=0  # Skip for now
    )

    # Flatten all examples
    all_examples_flat = []
    for category, examples in all_examples.items():
        all_examples_flat.extend(examples)

    # Print summary
    print("\n" + "="*60)
    print("📊 Generation Summary")
    print("="*60)
    for category, examples in all_examples.items():
        print(f"{category.replace('_', ' ').title()}: {len(examples)} examples")

    print(f"\nTotal Generated: {len(all_examples_flat)} examples")

    # Save to file
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_dir}/fitness_training_data_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(all_examples_flat, f, indent=2)

    print(f"\n💾 Saved to: {output_file}")

    # Save by category as well
    for category, examples in all_examples.items():
        if examples:
            category_file = f"{output_dir}/{category}_{timestamp}.json"
            with open(category_file, 'w') as f:
                json.dump(examples, f, indent=2)
            print(f"💾 Saved {category} to: {category_file}")

    # Print cost stats
    client.print_stats()

    print("\n✅ Generation Complete!")
    print("\n📝 Next Steps:")
    print("1. Review generated examples in data/ directory")
    print("2. Run validation: python validate_dataset.py")
    print("3. Generate remaining examples (Day 2)")
    print("4. Upload to HuggingFace Hub")

    return all_examples_flat


if __name__ == "__main__":
    asyncio.run(main())
