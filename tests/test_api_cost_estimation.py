import unittest
import sys
import os

# Add the parent directory to the path so we can import ctoken
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ctoken.token_estimator import (
    estimate_openai_api_cost,
    estimate_openai_api_cost_from_response,
)


class TestAPICostEstimation(unittest.TestCase):
    def test_estimate_openai_api_cost_chat(self):
        # Test cost estimation for a chat completion request
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."},
        ]

        cost = estimate_openai_api_cost(
            model="gpt-4o", messages=messages, max_tokens=100
        )

        self.assertGreater(cost, 0)
        self.assertLess(cost, 0.01)  # Should be a small cost for this request

        # Test with a dated model version
        cost_dated = estimate_openai_api_cost(
            model="gpt-4o-2024-05-13", messages=messages, max_tokens=100
        )

        self.assertGreater(cost_dated, 0)

    def test_estimate_openai_api_cost_completion(self):
        # Test cost estimation for a completion request
        prompt = "Translate the following English text to French: 'Hello, how are you?'"

        cost = estimate_openai_api_cost(
            model="gpt-4.5-preview-2025-02-27", prompt=prompt, max_tokens=50
        )

        self.assertGreater(cost, 0)

        # Test with another model version
        cost_dated = estimate_openai_api_cost(
            model="gpt-4o-2024-11-20", prompt=prompt, max_tokens=50
        )

        self.assertGreater(cost_dated, 0)
        # Higher tier model should cost more
        self.assertGreater(cost, cost_dated)

    def test_estimate_openai_api_cost_from_response(self):
        # Mock OpenAI API response with usage information
        response = {
            "model": "gpt-4o-2024-08-06",
            "usage": {"prompt_tokens": 55, "completion_tokens": 30, "total_tokens": 85},
        }

        cost = estimate_openai_api_cost_from_response(response)
        self.assertGreater(cost, 0)

        # Test with another model
        response_premium = {
            "model": "gpt-4.5-preview-2025-02-27",
            "usage": {"prompt_tokens": 55, "completion_tokens": 30, "total_tokens": 85},
        }

        cost_premium = estimate_openai_api_cost_from_response(response_premium)
        self.assertGreater(cost_premium, 0)
        # Premium model should cost more
        self.assertGreater(cost_premium, cost)

    def test_error_handling(self):
        # Test with invalid model
        with self.assertRaises(ValueError):
            estimate_openai_api_cost(
                model="non-existent-model",
                messages=[{"role": "user", "content": "Hello"}],
            )

        # Test with missing messages and prompt
        with self.assertRaises(ValueError):
            estimate_openai_api_cost(model="gpt-4o")

        # Test with invalid response format
        with self.assertRaises(ValueError):
            estimate_openai_api_cost_from_response({})

        with self.assertRaises(ValueError):
            estimate_openai_api_cost_from_response({"model": "gpt-4o"})  # Missing usage


if __name__ == "__main__":
    unittest.main()
