"""
Dataset Validation Script
Validates generated training data for quality and consistency
"""

import json
import os
from typing import List, Dict
from collections import Counter


class DatasetValidator:
    """Validate training dataset quality"""

    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.data = self.load_dataset()
        self.validation_results = {}

    def load_dataset(self) -> List[Dict]:
        """Load dataset from JSON file"""
        with open(self.dataset_path, 'r') as f:
            return json.load(f)

    def validate_all(self) -> Dict:
        """Run all validation checks"""
        print(f"\n🔍 Validating Dataset: {os.path.basename(self.dataset_path)}\n")
        print("="*60)

        self.validation_results = {
            "total_examples": len(self.data),
            "schema_validation": self.validate_schema(),
            "content_quality": self.validate_content_quality(),
            "category_distribution": self.validate_category_distribution(),
            "duplicates": self.check_duplicates(),
            "length_statistics": self.analyze_lengths(),
        }

        self.print_validation_report()
        return self.validation_results

    def validate_schema(self) -> Dict:
        """Validate that all examples have required fields"""
        required_fields = ["instruction", "input", "output", "category"]
        optional_fields = ["difficulty", "tags", "source", "generator"]

        valid_count = 0
        missing_fields = []

        for i, example in enumerate(self.data):
            is_valid = True
            for field in required_fields:
                if field not in example or not example[field]:
                    missing_fields.append(f"Example {i}: missing '{field}'")
                    is_valid = False

            if is_valid:
                valid_count += 1

        return {
            "valid": valid_count,
            "invalid": len(self.data) - valid_count,
            "missing_fields": missing_fields[:10],  # Show first 10
            "pass_rate": f"{valid_count / len(self.data) * 100:.1f}%"
        }

    def validate_content_quality(self) -> Dict:
        """Validate content quality metrics"""
        too_short = []
        too_long = []
        empty_inputs = []

        min_output_words = 100  # Minimum words in output
        max_output_words = 1500  # Maximum words in output

        for i, example in enumerate(self.data):
            # Check output length
            output_words = len(example.get("output", "").split())

            if output_words < min_output_words:
                too_short.append(f"Example {i}: {output_words} words")

            if output_words > max_output_words:
                too_long.append(f"Example {i}: {output_words} words")

            # Check for empty inputs
            if not example.get("input", "").strip():
                empty_inputs.append(f"Example {i}")

        return {
            "too_short": len(too_short),
            "too_long": len(too_long),
            "empty_inputs": len(empty_inputs),
            "too_short_examples": too_short[:5],
            "too_long_examples": too_long[:5],
            "quality_pass_rate": f"{(len(self.data) - len(too_short) - len(empty_inputs)) / len(self.data) * 100:.1f}%"
        }

    def validate_category_distribution(self) -> Dict:
        """Analyze category distribution"""
        categories = Counter()
        difficulties = Counter()
        generators = Counter()

        for example in self.data:
            categories[example.get("category", "unknown")] += 1
            difficulties[example.get("difficulty", "unknown")] += 1
            generators[example.get("generator", "unknown")] += 1

        return {
            "categories": dict(categories),
            "difficulties": dict(difficulties),
            "generators": dict(generators)
        }

    def check_duplicates(self) -> Dict:
        """Check for duplicate examples"""
        seen_instructions = {}
        duplicates = []

        for i, example in enumerate(self.data):
            instruction = example.get("instruction", "")
            if instruction in seen_instructions:
                duplicates.append(f"Example {i} duplicates {seen_instructions[instruction]}")
            else:
                seen_instructions[instruction] = i

        return {
            "duplicate_count": len(duplicates),
            "duplicate_examples": duplicates[:10],
            "uniqueness_rate": f"{(len(self.data) - len(duplicates)) / len(self.data) * 100:.1f}%"
        }

    def analyze_lengths(self) -> Dict:
        """Analyze text lengths"""
        instruction_lengths = [len(ex.get("instruction", "")) for ex in self.data]
        input_lengths = [len(ex.get("input", "")) for ex in self.data]
        output_lengths = [len(ex.get("output", "").split()) for ex in self.data]

        return {
            "avg_instruction_chars": sum(instruction_lengths) / len(instruction_lengths),
            "avg_input_chars": sum(input_lengths) / len(input_lengths),
            "avg_output_words": sum(output_lengths) / len(output_lengths),
            "min_output_words": min(output_lengths),
            "max_output_words": max(output_lengths)
        }

    def print_validation_report(self):
        """Print validation report"""
        results = self.validation_results

        print("\n📊 VALIDATION REPORT")
        print("="*60)

        print(f"\n📈 Dataset Size: {results['total_examples']} examples")

        # Schema validation
        schema = results['schema_validation']
        print(f"\n✅ Schema Validation:")
        print(f"  Valid: {schema['valid']}/{results['total_examples']} ({schema['pass_rate']})")
        if schema['invalid'] > 0:
            print(f"  ⚠️  Invalid: {schema['invalid']}")
            for missing in schema['missing_fields']:
                print(f"    - {missing}")

        # Content quality
        quality = results['content_quality']
        print(f"\n📝 Content Quality:")
        print(f"  Too short (<100 words): {quality['too_short']}")
        print(f"  Too long (>1500 words): {quality['too_long']}")
        print(f"  Empty inputs: {quality['empty_inputs']}")
        print(f"  Quality pass rate: {quality['quality_pass_rate']}")

        # Category distribution
        categories = results['category_distribution']
        print(f"\n📁 Category Distribution:")
        for cat, count in categories['categories'].items():
            percentage = count / results['total_examples'] * 100
            print(f"  {cat}: {count} ({percentage:.1f}%)")

        # Difficulty distribution
        if categories['difficulties']:
            print(f"\n🎯 Difficulty Distribution:")
            for diff, count in categories['difficulties'].items():
                percentage = count / results['total_examples'] * 100
                print(f"  {diff}: {count} ({percentage:.1f}%)")

        # Duplicates
        duplicates = results['duplicates']
        print(f"\n🔄 Duplicates:")
        print(f"  Duplicate count: {duplicates['duplicate_count']}")
        print(f"  Uniqueness rate: {duplicates['uniqueness_rate']}")

        # Length statistics
        lengths = results['length_statistics']
        print(f"\n📏 Length Statistics:")
        print(f"  Avg instruction: {lengths['avg_instruction_chars']:.0f} chars")
        print(f"  Avg input: {lengths['avg_input_chars']:.0f} chars")
        print(f"  Avg output: {lengths['avg_output_words']:.0f} words")
        print(f"  Output range: {lengths['min_output_words']} - {lengths['max_output_words']} words")

        print("\n" + "="*60)

        # Overall assessment
        schema_pass = schema['valid'] / results['total_examples'] > 0.95
        quality_pass = (results['total_examples'] - quality['too_short'] - quality['empty_inputs']) / results['total_examples'] > 0.90
        uniqueness_pass = duplicates['duplicate_count'] / results['total_examples'] < 0.05

        if schema_pass and quality_pass and uniqueness_pass:
            print("\n✅ VALIDATION PASSED - Dataset is ready for use!")
        else:
            print("\n⚠️  VALIDATION WARNINGS - Review issues above")
            if not schema_pass:
                print("  - Schema validation below 95%")
            if not quality_pass:
                print("  - Content quality below 90%")
            if not uniqueness_pass:
                print("  - Duplicates above 5%")

        print("="*60 + "\n")


def validate_latest_dataset():
    """Validate the most recent dataset"""
    data_dir = "data"

    # Find latest dataset file
    if not os.path.exists(data_dir):
        print(f"❌ Data directory '{data_dir}' not found")
        return

    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json') and f.startswith('fitness_training_data_')]

    if not json_files:
        print(f"❌ No dataset files found in '{data_dir}'")
        return

    # Sort by name (which includes timestamp)
    latest_file = sorted(json_files)[-1]
    file_path = os.path.join(data_dir, latest_file)

    print(f"📂 Found dataset: {latest_file}")

    validator = DatasetValidator(file_path)
    validator.validate_all()


if __name__ == "__main__":
    validate_latest_dataset()
