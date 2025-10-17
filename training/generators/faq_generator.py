"""FAQ Generator - Generates common fitness question/answer examples"""
import json, random
from typing import Dict, List
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.categories import FAQ_CATEGORIES
from config.prompts import get_generation_prompt

class FAQGenerator:
    def __init__(self, claude_client):
        self.client = claude_client
        self.generated_count = 0

    def create_context_variations(self, num_variations: int = 300) -> List[Dict]:
        variations = []
        common_questions = [
            "Should I do cardio before or after weights?",
            "How often should I train each muscle group?",
            "Is muscle soreness necessary for growth?",
            "How much protein do I really need?",
            "Can I build muscle and lose fat at the same time?",
            "What's the best time to workout?",
            "Do I need to take supplements?",
            "How long should my workouts be?",
            "Should I train to failure?",
            "How do I break through a plateau?",
        ]

        for question in common_questions:
            variations.append({"question": question, "context": "general fitness goals"})

        while len(variations) < num_variations:
            category = random.choice(list(FAQ_CATEGORIES.keys()))
            topic = random.choice(FAQ_CATEGORIES[category])
            context = random.choice(["muscle building", "fat loss", "general fitness", "strength training"])
            question = f"Question about {topic.replace('_', ' ')} for {context}"
            variation = {"question": question, "context": context}
            if variation not in variations:
                variations.append(variation)

        return variations[:num_variations]

    def format_context(self, variation: Dict) -> str:
        return f"Question: {variation['question']}, Context: {variation['context']}"

    async def generate_examples(self, num_examples: int = 300) -> List[Dict]:
        print(f"\n❓ Generating {num_examples} FAQ Examples...")
        variations = self.create_context_variations(num_examples)
        prompts = [get_generation_prompt("faq", self.format_context(v)) for v in variations]
        results = await self.client.generate_batch(prompts, show_progress=True)

        examples = []
        for i, result in enumerate(results):
            if result["success"]:
                try:
                    text = result["response"]
                    if "```json" in text: text = text.split("```json")[1].split("```")[0]
                    elif "```" in text: text = text.split("```")[1].split("```")[0]
                    example = json.loads(text.strip())
                    example.update({"source": "claude_generated", "generator": "faq", "category": "faq"})
                    examples.append(example)
                    self.generated_count += 1
                except: print(f"⚠️  Failed to parse example {i+1}")

        print(f"✅ Successfully generated {len(examples)}/{num_examples} examples")
        return examples
