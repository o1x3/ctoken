"""
Example usage of the ctoken library for estimating OpenAI API costs.

This example demonstrates:
1. Basic cost estimation for Chat Completions API
2. Working with streamed responses
3. Handling the Responses API
4. Error handling
"""

import os
from openai import OpenAI
from ctoken import ctoken, refresh_pricing, CostEstimateError


def basic_example():
    """Basic example using Chat Completions API."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-..."))

    try:
        # Make a simple API call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Explain quantum computing briefly."}
            ],
        )

        # Get cost estimate
        result = ctoken(response)

        # Display the results
        print("\n--- Basic Chat Completion Example ---")
        print(f"Prompt tokens: {result['prompt_tokens']}")
        print(f"Completion tokens: {result['completion_tokens']}")
        print(f"Total tokens: {result['total_tokens']}")
        print(f"Cached tokens: {result['cached_tokens']}")
        print(f"Prompt cost (uncached): ${result['prompt_cost_uncached']}")
        print(f"Prompt cost (cached): ${result['prompt_cost_cached']}")
        print(f"Completion cost: ${result['completion_cost']}")
        print(f"Total cost: ${result['total_cost']}")

    except CostEstimateError as e:
        print(f"Error estimating cost: {e}")


def streaming_example():
    """Example with streaming responses."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "sk-..."))

    try:
        # Make a streaming API call
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Write a short poem about AI."}],
            stream=True,
        )

        # Collect all chunks
        chunks = []
        print("\n--- Streaming Example ---")
        print("Response: ", end="")

        for chunk in stream:
            # Process the chunk as needed
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
            chunks.append(chunk)

        print("\n")

        # Estimate cost after collecting all chunks
        result = ctoken(chunks)
        print(f"Total tokens: {result['total_tokens']}")
        print(f"Total cost: ${result['total_cost']}")

    except CostEstimateError as e:
        print(f"Error estimating streaming cost: {e}")


def error_handling_example():
    """Example showing error handling."""
    try:
        # Try to estimate cost with invalid input
        result = ctoken(None)
    except CostEstimateError as e:
        print("\n--- Error Handling Example ---")
        print(f"Handled error gracefully: {e}")


def refresh_pricing_example():
    """Example showing how to refresh pricing data."""
    print("\n--- Refresh Pricing Example ---")
    try:
        # Force refresh of pricing data
        refresh_pricing()
        print("Successfully refreshed pricing data")
    except Exception as e:
        print(f"Error refreshing pricing data: {e}")


if __name__ == "__main__":
    print("CToken Library Usage Examples")
    print("============================")

    # Run all examples
    basic_example()
    streaming_example()
    error_handling_example()
    refresh_pricing_example()
