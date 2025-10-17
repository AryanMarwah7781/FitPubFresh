"""
Workout Programming Generator
Generates diverse workout program examples using Claude
"""

import json
import random
from typing import Dict, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.categories import (
    WORKOUT_VARIATIONS,
    ExperienceLevel,
    FitnessGoal,
    EquipmentType
)
from config.prompts import get_generation_prompt


class WorkoutGenerator:
    """Generate workout programming training examples"""

    def __init__(self, claude_client):
        """
        Initialize workout generator

        Args:
            claude_client: ClaudeClient instance
        """
        self.client = claude_client
        self.generated_count = 0

    def create_context_variations(self, num_variations: int = 400) -> List[Dict]:
        """
        Create diverse context variations for workout programs

        Args:
            num_variations: Number of unique variations to create

        Returns:
            List of context dictionaries
        """
        variations = []

        # Define specific scenarios for structured diversity
        scenarios = [
            # Beginner scenarios
            {
                "experience": ExperienceLevel.BEGINNER.value,
                "goal": FitnessGoal.GENERAL_FITNESS.value,
                "frequency": 3,
                "equipment": EquipmentType.FULL_GYM.value,
                "limitations": "None",
                "request": "Create a beginner-friendly 3-day full body program"
            },
            {
                "experience": ExperienceLevel.BEGINNER.value,
                "goal": FitnessGoal.WEIGHT_LOSS.value,
                "frequency": 4,
                "equipment": EquipmentType.HOME_GYM.value,
                "limitations": "Knee issues - avoid high impact",
                "request": "Design a 4-day home workout for fat loss with knee-friendly exercises"
            },

            # Intermediate scenarios
            {
                "experience": ExperienceLevel.INTERMEDIATE.value,
                "goal": Fitness Goal.HYPERTROPHY.value,
                "frequency": 4,
                "equipment": EquipmentType.FULL_GYM.value,
                "limitations": "Previous lower back injury (recovered)",
                "request": "Create a 4-day upper/lower split for muscle building"
            },
            {
                "experience": ExperienceLevel.INTERMEDIATE.value,
                "goal": FitnessGoal.STRENGTH.value,
                "frequency": 3,
                "equipment": EquipmentType.FULL_GYM.value,
                "limitations": "None",
                "request": "Design a 3-day full body strength program focusing on main lifts"
            },

            # Advanced scenarios
            {
                "experience": ExperienceLevel.ADVANCED.value,
                "goal": FitnessGoal.STRENGTH.value,
                "frequency": 5,
                "equipment": EquipmentType.FULL_GYM.value,
                "limitations": "None",
                "request": "Create a 5-day powerlifting-style program for advanced lifter"
            },
            {
                "experience": ExperienceLevel.ADVANCED.value,
                "goal": FitnessGoal.HYPERTROPHY.value,
                "frequency": 6,
                "equipment": EquipmentType.FULL_GYM.value,
                "limitations": "None",
                "request": "Design a 6-day push/pull/legs split for advanced bodybuilding"
            },

            # Special equipment scenarios
            {
                "experience": ExperienceLevel.INTERMEDIATE.value,
                "goal": FitnessGoal.HYPERTROPHY.value,
                "frequency": 4,
                "equipment": EquipmentType.BODYWEIGHT.value,
                "limitations": "No equipment access",
                "request": "Create a 4-day bodyweight program for muscle building"
            },
            {
                "experience": ExperienceLevel.BEGINNER.value,
                "goal": FitnessGoal.GENERAL_FITNESS.value,
                "frequency": 3,
                "equipment": EquipmentType.MINIMAL.value,
                "limitations": "Only have dumbbells up to 50lbs",
                "request": "Design a 3-day dumbbell-only full body program"
            },

            # Athletic performance scenarios
            {
                "experience": ExperienceLevel.INTERMEDIATE.value,
                "goal": FitnessGoal.ATHLETIC_PERFORMANCE.value,
                "frequency": 4,
                "equipment": EquipmentType.FULL_GYM.value,
                "limitations": "None",
                "request": "Create a 4-day program for basketball player focusing on explosiveness"
            },

            # Endurance scenarios
            {
                "experience": ExperienceLevel.INTERMEDIATE.value,
                "goal": FitnessGoal.ENDURANCE.value,
                "frequency": 4,
                "equipment": EquipmentType.FULL_GYM.value,
                "limitations": "Marathon runner wanting to add strength work",
                "request": "Design a 3-day strength program for endurance athletes"
            }
        ]

        # Add predefined scenarios
        variations.extend(scenarios)

        # Generate random variations to reach target count
        while len(variations) < num_variations:
            experience = random.choice(list(ExperienceLevel)).value
            goal = random.choice(list(FitnessGoal)).value
            frequency = random.choice(WORKOUT_VARIATIONS["frequencies"])
            equipment = random.choice(list(EquipmentType)).value
            split = random.choice(WORKOUT_VARIATIONS["splits"])

            # Generate random limitations (30% have limitations)
            limitations_pool = [
                "None",
                "None",
                "None",  # More "None" for weighted probability
                "Shoulder mobility issues",
                "Lower back sensitivity",
                "Knee pain from old injury",
                "Limited time (45 min sessions)",
                "Can only train mornings",
                "Wrist discomfort on pressing",
                "Hip flexor tightness"
            ]
            limitation = random.choice(limitations_pool)

            # Create contextual request
            requests = [
                f"Create a {frequency}-day {split.replace('_', ' ')} program for {goal.replace('_', ' ')}",
                f"Design a {frequency}-day workout focusing on {goal.replace('_', ' ')}",
                f"Build me a {split.replace('_', ' ')} program ({frequency} days/week) for {goal.replace('_', ' ')}",
                f"I need a {frequency}-day {split.replace('_', ' ')} routine optimized for {goal.replace('_', ' ')}"
            ]

            variation = {
                "experience": experience,
                "goal": goal,
                "frequency": frequency,
                "equipment": equipment,
                "limitations": limitation,
                "request": random.choice(requests)
            }

            # Avoid exact duplicates
            if variation not in variations:
                variations.append(variation)

        return variations[:num_variations]

    def format_context(self, variation: Dict) -> str:
        """Format variation into context string"""
        return f"""
        Request: {variation['request']}
        Experience Level: {variation['experience']}
        Primary Goal: {variation['goal']}
        Training Frequency: {variation['frequency']} days per week
        Equipment Available: {variation['equipment']}
        Limitations/Notes: {variation['limitations']}
        """

    async def generate_examples(self, num_examples: int = 400) -> List[Dict]:
        """
        Generate workout programming examples

        Args:
            num_examples: Number of examples to generate

        Returns:
            List of training examples
        """
        print(f"\n🏋️ Generating {num_examples} Workout Programming Examples...")

        # Create context variations
        variations = self.create_context_variations(num_examples)

        # Build prompts
        prompts = []
        for variation in variations:
            context = self.format_context(variation)
            prompt = get_generation_prompt("workout_programming", context)
            prompts.append(prompt)

        # Generate with Claude
        results = await self.client.generate_batch(prompts, show_progress=True)

        # Parse and validate results
        examples = []
        for i, result in enumerate(results):
            if result["success"]:
                try:
                    # Parse JSON response
                    example = json.loads(result["response"])

                    # Add metadata
                    example["source"] = "claude_generated"
                    example["generator"] = "workout_programming"
                    example["category"] = "workout_programming"

                    examples.append(example)
                    self.generated_count += 1

                except json.JSONDecodeError:
                    print(f"⚠️  Failed to parse example {i+1} - invalid JSON")
                    # Try to extract and fix JSON
                    try:
                        # Sometimes Claude wraps JSON in markdown code blocks
                        text = result["response"]
                        if "```json" in text:
                            text = text.split("```json")[1].split("```")[0]
                        elif "```" in text:
                            text = text.split("```")[1].split("```")[0]
                        example = json.loads(text.strip())
                        example["source"] = "claude_generated"
                        example["generator"] = "workout_programming"
                        example["category"] = "workout_programming"
                        examples.append(example)
                        self.generated_count += 1
                    except:
                        print(f"   Could not recover example {i+1}")
            else:
                print(f"⚠️  Generation failed for example {i+1}: {result.get('error', 'Unknown error')}")

        print(f"✅ Successfully generated {len(examples)}/{num_examples} examples")
        return examples


# Testing
async def test_generator():
    """Test workout generator"""
    from claude_client import ClaudeClient

    print("🧪 Testing Workout Generator\n")

    client = ClaudeClient()
    generator = WorkoutGenerator(client)

    # Generate 2 test examples
    examples = await generator.generate_examples(num_examples=2)

    print(f"\n📦 Generated {len(examples)} examples")

    if examples:
        print("\n" + "="*60)
        print("Sample Example:")
        print("="*60)
        example = examples[0]
        print(f"Instruction: {example['instruction']}")
        print(f"\nInput: {example['input']}")
        print(f"\nOutput (first 300 chars):\n{example['output'][:300]}...")
        print(f"\nCategory: {example['category']}")
        print(f"Difficulty: {example.get('difficulty', 'N/A')}")

    # Print stats
    client.print_stats()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_generator())
