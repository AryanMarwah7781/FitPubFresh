"""
Nutrition Advice Generator
Generates diverse nutrition and diet planning examples using Claude
"""

import json
import random
from typing import Dict, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.categories import NUTRITION_VARIATIONS
from config.prompts import get_generation_prompt


class NutritionGenerator:
    """Generate nutrition advice training examples"""

    def __init__(self, claude_client):
        self.client = claude_client
        self.generated_count = 0

    def create_context_variations(self, num_variations: int = 300) -> List[Dict]:
        """Create diverse nutrition context variations"""
        variations = []

        # Define specific scenarios
        scenarios = [
            {
                "goal": "cutting",
                "stats": "Male, 185lbs, 5'10\", 18% body fat",
                "activity": "4 strength sessions + 2 cardio sessions per week",
                "dietary_pref": "standard",
                "request": "Calculate macros for fat loss while preserving muscle"
            },
            {
                "goal": "bulking",
                "stats": "Male, 165lbs, 5'11\", 12% body fat",
                "activity": "5 strength sessions per week, minimal cardio",
                "dietary_pref": "standard",
                "request": "Calculate macros for lean bulk (muscle gain with minimal fat)"
            },
            {
                "goal": "cutting",
                "stats": "Female, 150lbs, 5'6\", 25% body fat",
                "activity": "3 strength sessions + 3 cardio sessions per week",
                "dietary_pref": "vegetarian",
                "request": "Create a vegetarian macro plan for fat loss"
            },
            {
                "goal": "bulking",
                "stats": "Male, 175lbs, 6'1\", 14% body fat",
                "activity": "4 strength sessions per week",
                "dietary_pref": "vegan",
                "request": "Design a vegan nutrition plan for muscle gain"
            },
            {
                "goal": "maintenance",
                "stats": "Female, 140lbs, 5'5\", 22% body fat",
                "activity": "4 strength sessions per week",
                "dietary_pref": "intermittent_fasting",
                "request": "Create a macro plan for maintenance with 16:8 IF protocol"
            },
            {
                "goal": "recomposition",
                "stats": "Male, 180lbs, 5'9\", 20% body fat",
                "activity": "4 strength sessions + 2 cardio sessions per week",
                "dietary_pref": "standard",
                "request": "Design nutrition plan for body recomp (lose fat + gain muscle)"
            }
        ]

        variations.extend(scenarios)

        # Generate random variations
        heights = ["5'6\"", "5'7\"", "5'8\"", "5'9\"", "5'10\"", "5'11\"", "6'0\"", "6'1\"", "6'2\""]
        weights = list(range(140, 220, 5))
        body_fats = list(range(12, 28, 2))
        genders = ["Male", "Female"]

        while len(variations) < num_variations:
            goal = random.choice(NUTRITION_VARIATIONS["goals"])
            dietary_pref = random.choice(NUTRITION_VARIATIONS["dietary_preferences"])
            activity = random.choice(NUTRITION_VARIATIONS["activity_levels"])
            gender = random.choice(genders)
            height = random.choice(heights)
            weight = random.choice(weights)
            bf = random.choice(body_fats)

            variation = {
                "goal": goal,
                "stats": f"{gender}, {weight}lbs, {height}, {bf}% body fat",
                "activity": activity,
                "dietary_pref": dietary_pref,
                "request": f"Calculate macros for {goal} with {dietary_pref} diet"
            }

            if variation not in variations:
                variations.append(variation)

        return variations[:num_variations]

    def format_context(self, variation: Dict) -> str:
        """Format variation into context string"""
        return f"""
        Request: {variation['request']}
        Stats: {variation['stats']}
        Goal: {variation['goal']}
        Activity Level: {variation['activity']}
        Dietary Preference: {variation['dietary_pref']}
        """

    async def generate_examples(self, num_examples: int = 300) -> List[Dict]:
        """Generate nutrition advice examples"""
        print(f"\n🥗 Generating {num_examples} Nutrition Advice Examples...")

        variations = self.create_context_variations(num_examples)

        prompts = []
        for variation in variations:
            context = self.format_context(variation)
            prompt = get_generation_prompt("nutrition_advice", context)
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
                    example["generator"] = "nutrition_advice"
                    example["category"] = "nutrition_advice"
                    examples.append(example)
                    self.generated_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to parse example {i+1}: {str(e)}")
            else:
                print(f"⚠️  Generation failed for example {i+1}")

        print(f"✅ Successfully generated {len(examples)}/{num_examples} examples")
        return examples
