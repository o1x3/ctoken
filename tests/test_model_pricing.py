import unittest
import sys
import os

# Add the parent directory to the path so we can import ctoken
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ctoken.pricing_data import (
    get_model_pricing,
    get_all_model_pricings,
    calculate_cost,
    calculate_total_cost,
)


class TestModelPricing(unittest.TestCase):
    def test_get_model_pricing(self):
        # Test for gpt-4.5-preview
        gpt45_pricing = get_model_pricing("gpt-4.5-preview-2025-02-27")
        self.assertIsNotNone(gpt45_pricing)
        self.assertEqual(gpt45_pricing["model"], "gpt-4.5-preview")
        self.assertEqual(gpt45_pricing["version"], "2025-02-27")

        # Test for gpt-4o
        gpt4o_pricing = get_model_pricing("gpt-4o")
        self.assertIsNotNone(gpt4o_pricing)
        self.assertEqual(gpt4o_pricing["model"], "gpt-4o")

        # Test for specific versions
        gpt4o_1120_pricing = get_model_pricing("gpt-4o-2024-11-20")
        self.assertIsNotNone(gpt4o_1120_pricing)
        self.assertEqual(gpt4o_1120_pricing["model"], "gpt-4o")
        self.assertEqual(gpt4o_1120_pricing["version"], "2024-11-20")

        gpt4o_0806_pricing = get_model_pricing("gpt-4o-2024-08-06")
        self.assertIsNotNone(gpt4o_0806_pricing)
        self.assertEqual(gpt4o_0806_pricing["model"], "gpt-4o")
        self.assertEqual(gpt4o_0806_pricing["version"], "2024-08-06")

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
        # Test cost calculation for gpt-4.5-preview
        gpt45_cost = calculate_cost("gpt-4.5-preview-2025-02-27", 1000, 500)
        self.assertGreater(gpt45_cost, 0)

        # Test cost calculation for gpt-4o
        gpt4o_cost = calculate_cost("gpt-4o", 1000, 500)
        self.assertGreater(gpt4o_cost, 0)

        # Test specific versions
        gpt4o_0513_cost = calculate_cost("gpt-4o-2024-05-13", 1000, 500)
        self.assertGreater(gpt4o_0513_cost, 0)

        # Ensure gpt-4.5 is more expensive than gpt-4o
        self.assertGreater(gpt45_cost, gpt4o_cost)

        # Test with zero tokens
        zero_cost = calculate_cost("gpt-4o", 0, 0)
        self.assertEqual(zero_cost, 0)

        # Test with non-existent model (should return 0)
        none_cost = calculate_cost("non-existent-model", 1000, 500)
        self.assertEqual(none_cost, 0)

    def test_calculate_total_cost(self):
        # Create a sample usage dictionary
        usage = {
            "gpt-4.5-preview-2025-02-27": {"input_tokens": 1000, "output_tokens": 500},
            "gpt-4o": {"input_tokens": 2000, "output_tokens": 1000},
            "gpt-4o-2024-08-06": {"input_tokens": 1500, "output_tokens": 750},
        }

        # Calculate total cost
        total_cost = calculate_total_cost(usage)
        self.assertGreater(total_cost, 0)

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
