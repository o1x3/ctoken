"""
Claude Token Pricing Calculator

A simple utility for calculating and estimating costs
when using OpenAI's API with Claude models.
"""

from datetime import datetime
import re
from typing import Dict, Any, Optional, List, Tuple, Union

from .pricing_data import (
    get_model_pricing,
    get_all_model_pricings,
    load_pricing,
    refresh_pricing,
)
from .response_parser import extract_model_details
from .calculation import calculate_cost
from .token_estimator import estimate_openai_api_cost as estimate_api_cost

__version__ = "1.0.0"

__all__ = [
    "calculate_cost",
    "extract_model_details",
    "estimate_api_cost",
    "get_model_pricing",
    "get_all_model_pricings",
    "load_pricing",
    "refresh_pricing",
]
