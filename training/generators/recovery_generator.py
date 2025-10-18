"""
Recovery and Injury Prevention Generator
Generates recovery protocols, injury prevention, and rehabilitation examples
"""

import json
import random
from typing import Dict, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.categories import INJURY_TOPICS
from config.prompts import get_generation_prompt


class RecoveryGenerator:
    """Generate recovery and injury prevention training examples"""

    def __init__(self, claude_client):
        self.client = claude_client
        self.generated_count = 0

    def create_context_variations(self, num_variations: int = 300) -> List[Dict]:
        """Create diverse recovery and injury context variations"""
        variations = []

        # Specific injury scenarios
        injury_scenarios = [
            {
                "issue": "lower_back_pain",
                "symptoms": "Dull ache after deadlifts, worse when bending forward",
                "training_history": "Intermediate, 18 months training, recently increased deadlift volume",
                "request": "How to address lower back pain from deadlifts and return to training safely"
            },
            {
                "issue": "shoulder_impingement",
                "symptoms": "Pain during overhead press at lockout, clicking sensation",
                "training_history": "Advanced, 3 years training, high pressing volume",
                "request": "Rehab protocol for shoulder impingement while maintaining training"
            },
            {
                "issue": "knee_pain",
                "symptoms": "Pain below kneecap during and after squats",
                "training_history": "Beginner, 4 months training, pain started 2 weeks ago",
                "request": "Address knee pain from squatting and modify training"
            },
            {
                "issue": "elbow_tendinitis",
                "symptoms": "Lateral elbow pain during pulling movements and curls",
                "training_history": "Intermediate, 1 year training, gradual onset over 3 months",
                "request": "Golfer's elbow rehabilitation while continuing training"
            },
            {
                "issue": "hip_flexor_strain",
                "symptoms": "Sharp pain in front of hip during squats and leg raises",
                "training_history": "Intermediate, recent increase in training frequency to 6 days",
                "request": "Recover from hip flexor strain and prevent recurrence"
            },
            {
                "issue": "wrist_pain",
                "symptoms": "Wrist pain during bench press and front squats",
                "training_history": "Beginner, 6 months training, pain in both wrists",
                "request": "Address wrist pain during pressing movements"
            },
            {
                "issue": "overtraining_syndrome",
                "symptoms": "Chronic fatigue, poor sleep, strength decreasing, elevated resting heart rate",
                "training_history": "Advanced, 4 years training, training 6-7 days/week with minimal rest",
                "request": "Recover from overtraining and optimize training schedule"
            },
            {
                "issue": "muscle_strain",
                "symptoms": "Pulled hamstring during deadlifts, can walk but painful",
                "training_history": "Intermediate, happened during heavy deadlift session",
                "request": "Hamstring strain recovery protocol and return to deadlifting"
            }
        ]

        variations.extend(injury_scenarios)

        # Recovery optimization scenarios
        recovery_scenarios = [
            {
                "issue": "poor_recovery",
                "symptoms": "Constantly sore, not recovering between sessions",
                "training_history": "Intermediate, training 5 days/week, sleep 6-7 hours",
                "request": "Optimize recovery to support current training volume"
            },
            {
                "issue": "injury_prevention",
                "symptoms": "No current injury but want to prevent issues",
                "training_history": "Beginner, starting serious training, previous sports injuries",
                "request": "Injury prevention strategies for long-term training sustainability"
            },
            {
                "issue": "mobility_limitations",
                "symptoms": "Poor squat depth due to ankle and hip mobility",
                "training_history": "Beginner, desk job, sedentary lifestyle",
                "request": "Mobility program to improve squat depth and movement quality"
            },
            {
                "issue": "deload_strategy",
                "symptoms": "Feeling run down after 8 weeks of training",
                "training_history": "Intermediate, following structured program",
                "request": "How to properly deload and when to implement deloads"
            }
        ]

        variations.extend(recovery_scenarios)

        # Generate random variations
        pain_locations = [
            "lower back", "shoulder", "knee", "elbow", "wrist",
            "hip", "ankle", "neck", "upper back"
        ]

        pain_types = [
            "sharp pain during movement",
            "dull ache after training",
            "stiffness in the morning",
            "clicking/popping sensation",
            "burning sensation"
        ]

        activities = [
            "squats", "deadlifts", "bench press", "overhead press",
            "rows", "pull-ups", "running", "all pressing movements",
            "all pulling movements"
        ]

        while len(variations) < num_variations:
            location = random.choice(pain_locations)
            pain_type = random.choice(pain_types)
            activity = random.choice(activities)
            duration = random.choice(["just started", "2 weeks", "1 month", "3 months"])

            experience = random.choice(["beginner", "intermediate", "advanced"])
            training_years = random.choice([0.5, 1, 1.5, 2, 3, 4, 5])

            variation = {
                "issue": f"{location.replace(' ', '_')}_pain",
                "symptoms": f"{pain_type.capitalize()} in {location} during {activity}, lasting {duration}",
                "training_history": f"{experience.capitalize()}, {training_years} years training",
                "request": f"Address {location} pain during {activity} and return to training"
            }

            if variation not in variations:
                variations.append(variation)

        return variations[:num_variations]

    def format_context(self, variation: Dict) -> str:
        """Format variation into context string"""
        return f"""
        Issue/Concern: {variation['issue'].replace('_', ' ').title()}
        Symptoms: {variation['symptoms']}
        Training History: {variation['training_history']}
        Request: {variation['request']}
        """

    async def generate_examples(self, num_examples: int = 300) -> List[Dict]:
        """Generate recovery and injury prevention examples"""
        print(f"\n🏥 Generating {num_examples} Recovery & Injury Prevention Examples...")

        variations = self.create_context_variations(num_examples)

        prompts = []
        for variation in variations:
            context = self.format_context(variation)
            prompt = get_generation_prompt("recovery_injury", context)
            prompts.append(prompt)

        results = await self.client.generate_batch(prompts, show_progress=True)

        examples = []
        for i, result in enumerate(results):
            if result["success"]:
                try:
                    text = result["response"]
                    # Handle markdown code blocks
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0]
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0]

                    example = json.loads(text.strip())
                    example["source"] = "claude_generated"
                    example["generator"] = "recovery_injury"
                    example["category"] = "recovery_injury"
                    examples.append(example)
                    self.generated_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to parse example {i+1}: {str(e)[:50]}")
            else:
                print(f"⚠️  Generation failed for example {i+1}")

        print(f"✅ Successfully generated {len(examples)}/{num_examples} examples")
        return examples


# Testing
async def test_generator():
    """Test recovery generator"""
    import sys
    sys.path.append(os.path.dirname(__file__))
    from claude_client import ClaudeClient

    print("🧪 Testing Recovery Generator\n")

    client = ClaudeClient()
    generator = RecoveryGenerator(client)

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

    # Print stats
    client.print_stats()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_generator())
