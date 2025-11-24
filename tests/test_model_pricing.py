import unittest
import sys
import os
import random

# Add the parent directory to the path so we can import ctoken
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ctoken.pricing_data import (
    get_model_pricing,
    get_all_model_pricings,
    calculate_cost,
    calculate_total_cost,
)


def get_random_models(count=2):
    """Get random models from available pricing data."""
    all_models = get_all_model_pricings()
    models = [m["model"] for m in all_models if m["model"]]
    return random.sample(models, min(count, len(models)))


class TestModelPricing(unittest.TestCase):
    def test_get_model_pricing(self):
        # Test with random models from available pricing
        models = get_random_models(3)

        for model in models:
            pricing = get_model_pricing(model)
            self.assertIsNotNone(pricing)
            self.assertEqual(pricing["model"], model)

        # Test for non-existent model
        none_pricing = get_model_pricing("non-existent-model")
        self.assertIsNone(none_pricing)

    def test_get_all_model_pricings(self):
        all_pricings = get_all_model_pricings()
        self.assertIsNotNone(all_pricings)
        self.assertGreater(len(all_pricings), 0)

        # Check that each pricing entry has the required fields
        for pricing in all_pricings:
            self.assertIn("model", pricing)
            self.assertIn("input_cost_per_1k", pricing)
            self.assertIn("output_cost_per_1k", pricing)

    def test_calculate_cost(self):
        # Test cost calculation with random models
        models = get_random_models(3)

        for model in models:
            cost = calculate_cost(model, 1000, 500)
            self.assertGreaterEqual(cost, 0)

        # Test with zero tokens
        model = get_random_models(1)[0]
        zero_cost = calculate_cost(model, 0, 0)
        self.assertEqual(zero_cost, 0)

        # Test with non-existent model (should return 0)
        none_cost = calculate_cost("non-existent-model", 1000, 500)
        self.assertEqual(none_cost, 0)

    def test_calculate_total_cost(self):
        # Create a sample usage dictionary with random models
        models = get_random_models(3)
        usage = {}
        for i, model in enumerate(models):
            usage[model] = {
                "input_tokens": 1000 * (i + 1),
                "output_tokens": 500 * (i + 1),
            }

        # Calculate total cost
        total_cost = calculate_total_cost(usage)
        self.assertGreaterEqual(total_cost, 0)

        # Test with empty usage
        empty_cost = calculate_total_cost({})
        self.assertEqual(empty_cost, 0)

        # Test with invalid model in usage
        invalid_usage = {
            "non-existent-model": {"input_tokens": 1000, "output_tokens": 500}
        }
        invalid_cost = calculate_total_cost(invalid_usage)
        self.assertEqual(invalid_cost, 0)


if __name__ == "__main__":
    unittest.main()
