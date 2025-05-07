"""
Basic usage example for ctoken package
"""

from dataclasses import dataclass


@dataclass
class DummyUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class DummyResponse:
    model: str
    usage: DummyUsage


# Create a dummy OpenAI response
dummy_response = DummyResponse(
    model="gpt-4o-mini-2024-07-18",
    usage=DummyUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500),
)

# Use ctoken to estimate the cost
from ctoken import ctoken

# Estimate token counts and cost with a single button
result = ctoken(dummy_response)

# Print the results
print("OpenAI API Token Count and Cost Estimate:")
print("-" * 40)
print(f"Model: {dummy_response.model}")
print("-" * 40)
print("Token Counts:")
print(f"Prompt tokens: {result['prompt_tokens']}")
print(f"Completion tokens: {result['completion_tokens']}")
print(f"Total tokens: {result['total_tokens']}")
print(f"Cached tokens: {result['cached_tokens']}")
print("-" * 40)
print("Cost Breakdown:")
print(f"Prompt cost (uncached): ${result['prompt_cost_uncached']}")
print(f"Prompt cost (cached): ${result['prompt_cost_cached']}")
print(f"Completion cost: ${result['completion_cost']}")
print(f"Total cost: ${result['total_cost']}")
