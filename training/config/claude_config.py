"""
Claude API Configuration
Optimized for training data generation with prompt caching
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class ClaudeConfig:
    """Configuration for Claude API"""

    # API Settings
    API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL: str = "claude-sonnet-4-20250514"  # Latest Sonnet model

    # Generation Settings
    MAX_TOKENS: int = 4096  # Claude can generate longer responses
    TEMPERATURE: float = 0.8  # Slightly creative for diverse examples
    TOP_P: float = 0.95

    # Cost Optimization
    USE_PROMPT_CACHING: bool = True  # 90% cost reduction on repeated prompts

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = 50  # Claude's default limit
    BATCH_SIZE: int = 10  # Process in batches

    # Quality Control
    MIN_OUTPUT_LENGTH: int = 200  # Minimum words for training example
    MAX_OUTPUT_LENGTH: int = 2000  # Maximum words

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in environment variables. "
                "Please set it in .env file."
            )
        return True


# Cost Estimation
class CostEstimator:
    """Estimate costs for Claude API usage"""

    # Claude Sonnet 4 pricing (per 1M tokens)
    INPUT_COST = 3.00  # $3 per 1M input tokens
    OUTPUT_COST = 15.00  # $15 per 1M output tokens
    CACHED_INPUT_COST = 0.30  # $0.30 per 1M cached tokens (90% savings)

    @staticmethod
    def estimate_cost(
        num_examples: int,
        avg_prompt_tokens: int = 1000,
        avg_output_tokens: int = 800,
        use_caching: bool = True
    ) -> dict:
        """
        Estimate total cost for generating training data

        Args:
            num_examples: Number of training examples to generate
            avg_prompt_tokens: Average tokens in prompt
            avg_output_tokens: Average tokens in output
            use_caching: Whether to use prompt caching

        Returns:
            Dictionary with cost breakdown
        """
        # First request (no cache)
        first_request_cost = (
            (avg_prompt_tokens / 1_000_000 * CostEstimator.INPUT_COST) +
            (avg_output_tokens / 1_000_000 * CostEstimator.OUTPUT_COST)
        )

        # Subsequent requests (with cache if enabled)
        if use_caching:
            cached_request_cost = (
                (avg_prompt_tokens / 1_000_000 * CostEstimator.CACHED_INPUT_COST) +
                (avg_output_tokens / 1_000_000 * CostEstimator.OUTPUT_COST)
            )
        else:
            cached_request_cost = first_request_cost

        # Total cost
        total_cost = first_request_cost + (cached_request_cost * (num_examples - 1))

        return {
            "num_examples": num_examples,
            "first_request": f"${first_request_cost:.4f}",
            "per_cached_request": f"${cached_request_cost:.4f}",
            "total_cost": f"${total_cost:.2f}",
            "cost_per_example": f"${total_cost / num_examples:.4f}",
            "caching_enabled": use_caching,
            "savings_vs_no_cache": f"${(first_request_cost * num_examples - total_cost):.2f}"
        }


if __name__ == "__main__":
    # Validate configuration
    ClaudeConfig.validate()
    print("✅ Claude configuration is valid!")

    # Estimate costs for 1500 examples
    print("\n💰 Cost Estimation for 1500 Training Examples:")
    estimate = CostEstimator.estimate_cost(num_examples=1500)
    for key, value in estimate.items():
        print(f"  {key}: {value}")

    print("\n📊 Comparison with GPT-4:")
    print("  GPT-4 (1500 examples): ~$25-30")
    print(f"  Claude Sonnet 4 (1500 examples): {estimate['total_cost']}")
    print(f"  Savings: ~${30 - float(estimate['total_cost'].replace('$', '')):.2f}")
