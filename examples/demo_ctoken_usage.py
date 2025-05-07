import sys
import os

# Add the parent directory to the path so we can import ctoken
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import ctoken


def demonstrate_ctoken_usage():
    print("# CToken: API Token Counter Demo")
    print("-" * 50)

    # Example 1: Count tokens in a string
    print("\n## Example 1: Count tokens in a string")
    text = "This is a test string to count tokens. How many tokens will this be?"
    token_count = ctoken.count(text)
    print(f"Text: '{text}'")
    print(f"Token count: {token_count}")

    # Example 2: Count tokens in a chat message
    print("\n## Example 2: Count tokens in a chat message")
    message = {"role": "user", "content": "What's the weather like today?"}
    message_token_count = ctoken.count(message)
    print(f"Message: {message}")
    print(f"Token count: {message_token_count}")

    # Example 3: Count tokens in a full conversation
    print("\n## Example 3: Count tokens in a conversation")
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about Paris."},
        {
            "role": "assistant",
            "content": "Paris is the capital of France and known for landmarks like the Eiffel Tower.",
        },
        {"role": "user", "content": "How tall is the Eiffel Tower?"},
    ]
    conversation_token_count = ctoken.count(conversation)
    print(f"Conversation with {len(conversation)} messages")
    print(f"Token count: {conversation_token_count}")

    # Example 4: Estimate cost
    print("\n## Example 4: Estimate cost for API call")

    # For GPT-3.5 Turbo
    cost_35 = ctoken.ctoken(
        model="gpt-3.5-turbo",
        input_tokens=conversation_token_count,
        output_tokens=100,  # Assuming the response will be around 100 tokens
    )

    # For GPT-4
    cost_4 = ctoken.ctoken(
        model="gpt-4",
        input_tokens=conversation_token_count,
        output_tokens=100,  # Same output token estimate
    )

    print(f"GPT-3.5 Turbo cost: ${cost_35:.6f}")
    print(f"GPT-4 cost: ${cost_4:.6f}")

    print(
        "\nCToken provides a simple way to count tokens and estimate costs for OpenAI API calls."
    )


if __name__ == "__main__":
    demonstrate_ctoken_usage()
