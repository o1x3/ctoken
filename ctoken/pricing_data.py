"""
Pricing data management module.

This module loads and provides access to the bundled pricing data dictionary.
It is updated by external scripts as needed.
"""

from typing import Dict, Tuple, Optional, List, Any
import re

# Import the static pricing data
from ctoken.data.pricing_data import PRICING_DATA

# Cache configuration
_pricing_cache: Optional[Dict[Tuple[str, str], Dict[str, float]]] = None


def load_pricing() -> Dict[Tuple[str, str], Dict[str, float]]:
    """
    Load pricing data from the bundled dictionary.

    Returns:
        Dictionary mapping (model_name, date) to pricing information
    """
    global _pricing_cache

    if _pricing_cache is None:
        _pricing_cache = PRICING_DATA

    return _pricing_cache


def refresh_pricing() -> None:
    """
    Force a refresh of the pricing data from the bundled dictionary.

    This function is exposed for API consistency but simply reloads from the
    bundled data since external updates will modify the source file directly.
    """
    global _pricing_cache
    _pricing_cache = PRICING_DATA


def get_model_pricing(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Get pricing information for a specific model.

    Args:
        model_name: The name of the model to get pricing for

    Returns:
        Dictionary with pricing information or None if model not found
    """
    # Normalize model name
    if not isinstance(model_name, str):
        model_name = str(model_name)

    model_name = model_name.lower().strip()
    base_model_name = model_name
    version = None

    # Handle versioned models (e.g., gpt-4.5-preview-2025-02-27)
    date_pattern = r"-(\d{4}-\d{2}-\d{2})$"
    date_match = re.search(date_pattern, model_name)
    if date_match:
        version = date_match.group(1)
        base_model_name = re.sub(date_pattern, "", model_name)

    # Get all pricing data
    pricing_data = get_all_model_pricings()

    # Direct match with base model name
    for pricing in pricing_data:
        if pricing["model"].lower() == base_model_name:
            # For test compatibility, set the model to base model name
            result = pricing.copy()
            result["model"] = base_model_name
            if version:
                result["version"] = version
            return result

    # Handle versioned models (like gpt-4-0125-preview)
    if "-" in model_name and not version:
        parts = model_name.split("-")
        if len(parts) >= 3:
            base_model = "-".join(parts[:2])  # e.g., "gpt-4"
            version = parts[2]  # e.g., "0125"

            # Check for base model matches
            for pricing in pricing_data:
                if pricing["model"].lower() == base_model:
                    # Clone the pricing and add version
                    versioned_pricing = pricing.copy()
                    versioned_pricing["version"] = version
                    return versioned_pricing

    # No match found
    return None


def get_all_model_pricings() -> List[Dict[str, Any]]:
    """
    Get pricing information for all available models.

    Returns:
        List of dictionaries with pricing information for each model
    """
    pricing_data = load_pricing()
    result = []

    # Convert internal pricing data to the expected format
    for (model_name, _), rates in pricing_data.items():
        # Skip duplicate entries (dates/versions)
        if any(p["model"] == model_name for p in result):
            continue

        model_pricing = {
            "model": model_name,
            "input_cost_per_1k": rates.get("input_price", 0)
            / 1000,  # Convert to cost per 1K
            "output_cost_per_1k": rates.get("output_price", 0) / 1000,
        }

        result.append(model_pricing)

    return result


def calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate the cost of a completion for a specific model.

    Args:
        model_name: The name of the model to calculate cost for
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        The cost in USD as a float
    """
    model_pricing = get_model_pricing(model_name)
    if not model_pricing:
        return 0.0

    input_cost = model_pricing["input_cost_per_1k"] * (input_tokens / 1000)
    output_cost = model_pricing["output_cost_per_1k"] * (output_tokens / 1000)

    return input_cost + output_cost


def calculate_total_cost(usage: Dict[str, Dict[str, int]]) -> float:
    """
    Calculate the total cost of a series of completions.

    Args:
        usage: Dictionary mapping model names to token counts
              Format: {"model_name": {"input_tokens": count, "output_tokens": count}}

    Returns:
        The total cost in USD as a float
    """
    total_cost = 0.0

    for model_name, tokens in usage.items():
        input_tokens = tokens.get("input_tokens", 0)
        output_tokens = tokens.get("output_tokens", 0)

        model_cost = calculate_cost(model_name, input_tokens, output_tokens)
        total_cost += model_cost

    return total_cost
