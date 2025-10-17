"""Form Correction Generator - Generates exercise form correction examples"""
import json, random
from typing import Dict, List
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.categories import MAJOR_EXERCISES
from config.prompts import get_generation_prompt

class FormCorrectionGenerator:
    def __init__(self, claude_client):
        self.client = claude_client
        self.generated_count = 0

    def create_context_variations(self, num_variations: int = 200) -> List[Dict]:
        variations = []
        form_issues = [
            {"exercise": "squat", "issue": "knees caving inward", "pain": "lower back"},
            {"exercise": "deadlift", "issue": "rounding lower back", "pain": "lower back"},
            {"exercise": "bench_press", "issue": "shoulder pain", "pain": "front deltoids"},
            {"exercise": "overhead_press", "issue": "arching lower back excessively", "pain": "lower back"},
            {"exercise": "pull_ups", "issue": "swinging and using momentum", "pain": "none but ineffective"},
        ]

        while len(variations) < num_variations:
            exercise_category = random.choice(list(MAJOR_EXERCISES.keys()))
            exercise = random.choice(MAJOR_EXERCISES[exercise_category])
            issue = random.choice(["pain during movement", "ineffective technique", "mobility limitation"])

            variation = {
                "exercise": exercise,
                "issue": issue,
                "experience": random.choice(["beginner", "intermediate"]),
                "request": f"Fix my {exercise.replace('_', ' ')} form - experiencing {issue}"
            }
            if variation not in variations:
                variations.append(variation)

        return variations[:num_variations]

    def format_context(self, variation: Dict) -> str:
        return f"Exercise: {variation['exercise']}, Issue: {variation['issue']}, Experience: {variation['experience']}, Request: {variation['request']}"

    async def generate_examples(self, num_examples: int = 200) -> List[Dict]:
        print(f"\n🎯 Generating {num_examples} Form Correction Examples...")
        variations = self.create_context_variations(num_examples)
        prompts = [get_generation_prompt("form_corrections", self.format_context(v)) for v in variations]
        results = await self.client.generate_batch(prompts, show_progress=True)

        examples = []
        for i, result in enumerate(results):
            if result["success"]:
                try:
                    text = result["response"]
                    if "```json" in text: text = text.split("```json")[1].split("```")[0]
                    elif "```" in text: text = text.split("```")[1].split("```")[0]
                    example = json.loads(text.strip())
                    example.update({"source": "claude_generated", "generator": "form_corrections", "category": "form_corrections"})
                    examples.append(example)
                    self.generated_count += 1
                except: print(f"⚠️  Failed to parse example {i+1}")

        print(f"✅ Successfully generated {len(examples)}/{num_examples} examples")
        return examples
