import unittest
import sys
import os
import random

# Add the parent directory to the path so we can import ctoken
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ctoken.token_estimator import (
    estimate_openai_api_cost,
    estimate_openai_api_cost_from_response,
)
from ctoken.pricing_data import get_all_model_pricings


def get_random_models(count=2):
    """Get random models from available pricing data."""
    all_models = get_all_model_pricings()
    models = [m["model"] for m in all_models if m["model"]]
    return random.sample(models, min(count, len(models)))


class TestAPICostEstimation(unittest.TestCase):
    def test_estimate_openai_api_cost_chat(self):
        # Test cost estimation for a chat completion request
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "The capital of France is Paris."},
        ]

        models = get_random_models(2)

        for model in models:
            cost = estimate_openai_api_cost(
                model=model, messages=messages, max_tokens=100
            )
            self.assertGreaterEqual(cost, 0)

    def test_estimate_openai_api_cost_completion(self):
        # Test cost estimation for a completion request
        prompt = "Translate the following English text to French: 'Hello, how are you?'"

        models = get_random_models(2)

        for model in models:
            cost = estimate_openai_api_cost(
                model=model, prompt=prompt, max_tokens=50
            )
            self.assertGreaterEqual(cost, 0)

    def test_estimate_openai_api_cost_from_response(self):
        # Test with random models from available pricing
        models = get_random_models(2)

        for model in models:
            response = {
                "model": model,
                "usage": {"prompt_tokens": 55, "completion_tokens": 30, "total_tokens": 85},
            }
            cost = estimate_openai_api_cost_from_response(response)
            self.assertGreaterEqual(cost, 0)

    def test_error_handling(self):
        # Test with invalid model
        with self.assertRaises(ValueError):
            estimate_openai_api_cost(
                model="non-existent-model",
                messages=[{"role": "user", "content": "Hello"}],
            )

        # Test with missing messages and prompt
        with self.assertRaises(ValueError):
            model = get_random_models(1)[0]
            estimate_openai_api_cost(model=model)

        # Test with invalid response format
        with self.assertRaises(ValueError):
            estimate_openai_api_cost_from_response({})

        with self.assertRaises(ValueError):
            model = get_random_models(1)[0]
            estimate_openai_api_cost_from_response({"model": model})  # Missing usage


if __name__ == "__main__":
    unittest.main()
