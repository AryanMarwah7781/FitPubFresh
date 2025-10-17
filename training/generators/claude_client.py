"""
Claude API Client for Training Data Generation
Optimized with prompt caching and rate limiting
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.claude_config import ClaudeConfig

load_dotenv()


class ClaudeClient:
    """
    Wrapper for Claude API with:
    - Prompt caching for cost optimization
    - Rate limiting
    - Error handling and retries
    - Token tracking
    """

    def __init__(self):
        ClaudeConfig.validate()
        self.client = Anthropic(api_key=ClaudeConfig.API_KEY)
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cached_tokens = 0
        self.request_count = 0
        self.last_request_time = 0

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        use_caching: bool = True
    ) -> Dict:
        """
        Generate response from Claude with caching

        Args:
            system_prompt: System prompt (will be cached if use_caching=True)
            user_prompt: User prompt
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            use_caching: Whether to use prompt caching

        Returns:
            Dictionary with response and metadata
        """
        # Rate limiting
        await self._rate_limit()

        # Use config defaults if not specified
        temperature = temperature or ClaudeConfig.TEMPERATURE
        max_tokens = max_tokens or ClaudeConfig.MAX_TOKENS

        try:
            # Build messages
            messages = [{"role": "user", "content": user_prompt}]

            # Build system with caching if enabled
            if use_caching and ClaudeConfig.USE_PROMPT_CACHING:
                system = [
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"}  # Cache this
                    }
                ]
            else:
                system = system_prompt

            # Make API call
            response = self.client.messages.create(
                model=ClaudeConfig.MODEL,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=messages
            )

            # Track tokens
            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens

            # Track cached tokens if available
            if hasattr(response.usage, 'cache_read_input_tokens'):
                cached = response.usage.cache_read_input_tokens
                self.total_cached_tokens += cached
            else:
                cached = 0

            self.request_count += 1

            # Extract response text
            response_text = response.content[0].text

            return {
                "success": True,
                "response": response_text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cached_tokens": cached
                },
                "model": response.model,
                "stop_reason": response.stop_reason
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None
            }

    async def generate_batch(
        self,
        prompts: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        show_progress: bool = True
    ) -> List[Dict]:
        """
        Generate multiple responses in batch

        Args:
            prompts: List of {"system": "...", "user": "..."} prompts
            temperature: Generation temperature
            max_tokens: Max tokens per response
            show_progress: Show progress bar

        Returns:
            List of responses
        """
        results = []

        if show_progress:
            try:
                from tqdm import tqdm
                prompts_iter = tqdm(prompts, desc="Generating", unit="example")
            except ImportError:
                prompts_iter = prompts
                print(f"Generating {len(prompts)} examples...")
        else:
            prompts_iter = prompts

        for i, prompt in enumerate(prompts_iter):
            result = await self.generate(
                system_prompt=prompt["system"],
                user_prompt=prompt["user"],
                temperature=temperature,
                max_tokens=max_tokens,
                use_caching=True  # Always cache for batch
            )

            results.append(result)

            # Small delay between requests
            if i < len(prompts) - 1:
                await asyncio.sleep(0.1)

        return results

    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        # Ensure minimum time between requests (to stay under rate limit)
        min_interval = 60.0 / ClaudeConfig.MAX_REQUESTS_PER_MINUTE
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)

        self.last_request_time = time.time()

    def get_stats(self) -> Dict:
        """Get usage statistics"""
        total_tokens = self.total_input_tokens + self.total_output_tokens

        # Calculate cost
        input_cost = (self.total_input_tokens / 1_000_000) * 3.0
        cached_cost = (self.total_cached_tokens / 1_000_000) * 0.30
        output_cost = (self.total_output_tokens / 1_000_000) * 15.0
        total_cost = input_cost + cached_cost + output_cost

        return {
            "requests": self.request_count,
            "total_tokens": total_tokens,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "cached_tokens": self.total_cached_tokens,
            "total_cost": f"${total_cost:.2f}",
            "cost_breakdown": {
                "input": f"${input_cost:.2f}",
                "cached": f"${cached_cost:.2f}",
                "output": f"${output_cost:.2f}"
            },
            "avg_cost_per_request": f"${total_cost / max(1, self.request_count):.4f}",
            "cache_hit_rate": f"{(self.total_cached_tokens / max(1, self.total_input_tokens) * 100):.1f}%"
        }

    def print_stats(self):
        """Print usage statistics"""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("📊 Claude API Usage Statistics")
        print("="*60)
        print(f"Total Requests: {stats['requests']}")
        print(f"Total Tokens: {stats['total_tokens']:,}")
        print(f"  - Input: {stats['input_tokens']:,}")
        print(f"  - Output: {stats['output_tokens']:,}")
        print(f"  - Cached: {stats['cached_tokens']:,}")
        print(f"\n💰 Cost Breakdown:")
        print(f"  - Input Cost: {stats['cost_breakdown']['input']}")
        print(f"  - Cached Cost: {stats['cost_breakdown']['cached']}")
        print(f"  - Output Cost: {stats['cost_breakdown']['output']}")
        print(f"  - Total Cost: {stats['total_cost']}")
        print(f"  - Avg per Request: {stats['avg_cost_per_request']}")
        print(f"\n⚡ Cache Performance: {stats['cache_hit_rate']}")
        print("="*60)


# Test the client
async def test_client():
    """Test Claude client"""
    print("🧪 Testing Claude Client\n")

    client = ClaudeClient()

    # Test single generation
    result = await client.generate(
        system_prompt="You are a helpful fitness coach.",
        user_prompt="Explain progressive overload in one paragraph.",
        max_tokens=200
    )

    if result["success"]:
        print("✅ Generation successful!")
        print(f"\nResponse preview:\n{result['response'][:200]}...")
        print(f"\nTokens used: {result['usage']}")
    else:
        print(f"❌ Generation failed: {result['error']}")

    # Print stats
    client.print_stats()


if __name__ == "__main__":
    asyncio.run(test_client())
