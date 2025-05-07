import sys
import os

# Add the parent directory to the path so we can import ctoken
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import ctoken
from ctoken.token_estimator import estimate_openai_api_cost


def demonstrate_cost_estimation():
    print("# CToken: OpenAI API Cost Estimation Demo")
    print("-" * 50)

    # Example 1: Simple chat completion
    print("\n## Example 1: Simple Chat Completion")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ]

    # Calculate estimated cost
    cost = estimate_openai_api_cost(
        model="gpt-3.5-turbo", messages=messages, max_tokens=50
    )

    token_count = ctoken.count(messages)

    print(f"Model: gpt-3.5-turbo")
    print(f"Input: {token_count} tokens")
    print(f"Max output: 50 tokens")
    print(f"Estimated cost: ${cost:.6f}")

    # Example 2: More complex conversation
    print("\n## Example 2: Complex Conversation")
    complex_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides detailed information about world capitals.",
        },
        {"role": "user", "content": "Tell me about Paris, France."},
        {
            "role": "assistant",
            "content": "Paris is the capital and most populous city of France. It is located on the Seine River, in the north of the country. Paris is known for its art, culture, fashion, and cuisine. Some famous landmarks include the Eiffel Tower, the Louvre Museum, Notre-Dame Cathedral, and the Arc de Triomphe.",
        },
        {"role": "user", "content": "What about London?"},
        {
            "role": "assistant",
            "content": "London is the capital and largest city of England and the United Kingdom. It stands on the River Thames in southeast England. London is a global city and one of the world's major financial, cultural, and historical centers. Famous landmarks include the Tower of London, Buckingham Palace, the British Museum, and the London Eye.",
        },
        {"role": "user", "content": "And Tokyo?"},
    ]

    # Calculate estimated cost for GPT-4
    cost_gpt4 = estimate_openai_api_cost(
        model="gpt-4", messages=complex_messages, max_tokens=250
    )

    complex_token_count = ctoken.count(complex_messages)

    print(f"Model: gpt-4")
    print(f"Input: {complex_token_count} tokens")
    print(f"Max output: 250 tokens")
    print(f"Estimated cost: ${cost_gpt4:.6f}")

    # Example 3: Completion (not chat)
    print("\n## Example 3: Text Completion")
    prompt = "Write a short poem about artificial intelligence."

    # Calculate estimated cost for completion
    cost_completion = estimate_openai_api_cost(
        model="gpt-3.5-turbo-instruct", prompt=prompt, max_tokens=100
    )

    prompt_token_count = ctoken.count(prompt)

    print(f"Model: gpt-3.5-turbo-instruct")
    print(f"Input: {prompt_token_count} tokens")
    print(f"Max output: 100 tokens")
    print(f"Estimated cost: ${cost_completion:.6f}")

    # Example 4: Different model versions
    print("\n## Example 4: Different GPT-4 Versions")

    test_message = [
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ]

    # Standard GPT-4
    cost_gpt4_std = estimate_openai_api_cost(
        model="gpt-4", messages=test_message, max_tokens=150
    )

    # GPT-4 Turbo
    cost_gpt4_turbo = estimate_openai_api_cost(
        model="gpt-4-turbo", messages=test_message, max_tokens=150
    )

    # GPT-4 Vision
    cost_gpt4_vision = estimate_openai_api_cost(
        model="gpt-4-vision-preview", messages=test_message, max_tokens=150
    )

    test_token_count = ctoken.count(test_message)

    print(f"Input: {test_token_count} tokens")
    print(f"Max output: 150 tokens")
    print(f"GPT-4 Standard cost: ${cost_gpt4_std:.6f}")
    print(f"GPT-4 Turbo cost: ${cost_gpt4_turbo:.6f}")
    print(f"GPT-4 Vision cost: ${cost_gpt4_vision:.6f}")

    print("\n## Pricing Information")
    print("For more information on the pricing data used, see the documentation.")
    print(
        "Prices are based on the official OpenAI pricing at the time of the library's last update."
    )


if __name__ == "__main__":
    demonstrate_cost_estimation()
