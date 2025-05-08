"""
Cost estimation module for OpenAI API responses.

This is the main public interface of the library, providing a simple
function to estimate costs for various types of OpenAI API responses.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional
from .calculation import calculate_cost, format_usd
from .response_parser import extract_model_details, extract_usage
from .pricing_data import load_pricing, get_model_pricing


class CostEstimateError(Exception):
    """
    Unified exception for all cost estimation errors.

    This exception is raised for any recoverable errors during cost estimation,
    including invalid inputs, missing attributes, and pricing data issues.
    """

    pass


def _find_last_chunk_with_usage(stream: Iterable[Any]) -> Any:
    """
    Extract the last chunk from a stream that contains usage information.

    Args:
        stream: An iterable of response chunks

    Returns:
        The last chunk containing usage information

    Raises:
        CostEstimateError: If no chunks contain usage information
    """
    last_chunk = None

    for chunk in stream:
        if hasattr(chunk, "usage"):
            last_chunk = chunk

    if last_chunk is None:
        raise CostEstimateError("Stream contained no chunks with usage information")

    return last_chunk


@lru_cache(maxsize=128)
def _get_model_rates(model_name: str, model_date: str) -> Dict[str, float]:
    """
    Find the appropriate pricing rates for a model.

    Uses a multi-stage lookup strategy with caching for performance.

    Args:
        model_name: Base model name (e.g., "gpt-4o-mini")
        model_date: Version date or "latest"

    Returns:
        Dict containing input_price, cached_input_price, and output_price

    Raises:
        CostEstimateError: If no pricing data can be found for the model
    """
    pricing_data = load_pricing()

    # Strategy 1: Check common keys first (most frequently hit lookups)
    for key in [
        (model_name, model_date),  # Exact match
        (model_name, "latest"),  # Base model match
        (f"{model_name}-{model_date}", "latest"),  # Full versioned name
    ]:
        if key in pricing_data:
            return pricing_data[key]

    # Strategy 2: Efficient substring search using dict lookup sets
    model_name_lower = model_name.lower().strip()
    for (name, date), rates in pricing_data.items():
        name_first_part = name.split("\n")[0].strip().lower()
        if model_name_lower in name_first_part or name_first_part in model_name_lower:
            return rates

    # Strategy 3: Date-based matching (only if model_date is not "latest")
    if model_date != "latest":
        candidates = [
            (date, rates)
            for (name, date), rates in pricing_data.items()
            if name == model_name and date <= model_date
        ]

        if candidates:
            # Pick the newest among older dates
            _, rates = max(candidates, key=lambda x: x[0])
            return rates

    raise CostEstimateError(
        f"No pricing data found for model '{model_name}' (date: {model_date})"
    )


# Cache for model details to avoid repeated parsing
_model_details_cache = {}


def ctoken(response: Any) -> Dict[str, Any]:
    """
    Estimate token usage and cost for an OpenAI API response.

    Supports multiple response types:
    - Single ChatCompletion response object
    - Stream of ChatCompletionChunk objects
    - Responses API object

    Args:
        response: An OpenAI API response object or stream

    Returns:
        Dict containing detailed cost breakdown:
            - prompt_tokens: Number of input tokens
            - completion_tokens: Number of output tokens
            - total_tokens: Total token count
            - cached_tokens: Number of cached tokens
            - prompt_cost_uncached: Cost of non-cached prompt tokens (USD as string)
            - prompt_cost_cached: Cost of cached prompt tokens (USD as string)
            - completion_cost: Cost of completion tokens (USD as string)
            - total_cost: Total cost (USD as string)

    Raises:
        CostEstimateError: For any issues during estimation
    """
    try:
        # Handle different response types
        if hasattr(response, "__iter__") and not hasattr(response, "model"):
            # This is a stream of chunks - get the last one with usage data
            chunk = _find_last_chunk_with_usage(response)
        else:
            # This is a single response object
            chunk = response

        # Extract token usage
        usage_data = extract_usage(chunk)

        # Extract model details with caching
        model_str = chunk.model
        if model_str in _model_details_cache:
            model_info = _model_details_cache[model_str]
        else:
            model_info = extract_model_details(model_str)
            _model_details_cache[model_str] = model_info

        # Get pricing rates
        pricing_rates = _get_model_rates(
            model_info["model_name"], model_info["model_date"]
        )

        # Calculate cost breakdown
        result = calculate_cost(usage_data, pricing_rates)

        # Pre-define cost keys for faster lookup
        cost_keys = {
            "prompt_cost_uncached",
            "prompt_cost_cached",
            "completion_cost",
            "total_cost",
        }

        # Process values - use faster approach for string conversion
        for key, value in result.items():
            if isinstance(value, (int, float)):
                result[key] = format_usd(value) if key in cost_keys else str(value)

        return result

    except Exception as e:
        # Wrap all exceptions in our unified error type
        if isinstance(e, CostEstimateError):
            raise
        raise CostEstimateError(str(e)) from e


# Alias for backward compatibility
estimate_cost = ctoken


def estimate_openai_api_cost(
    model: str,
    messages: Optional[List[Dict[str, str]]] = None,
    prompt: Optional[str] = None,
    max_tokens: int = 0,
) -> float:
    """
    Estimate the cost of an OpenAI API call before making it.

    This function estimates the cost of a completion or chat completion
    request based on the model, messages/prompt, and maximum tokens.

    Args:
        model: The model identifier (e.g., "gpt-4", "gpt-3.5-turbo")
        messages: List of message dictionaries for chat completions
        prompt: Text prompt for completions
        max_tokens: Maximum number of tokens to generate in the output

    Returns:
        Estimated cost in USD

    Raises:
        ValueError: If the model is not found or inputs are invalid
    """
    if not model:
        raise ValueError("Model identifier is required")

    # Get model pricing
    model_pricing = get_model_pricing(model)
    if not model_pricing:
        raise ValueError(f"Model '{model}' not found in pricing data")

    # Calculate input token count with improved estimation
    input_tokens = 0
    if messages:
        # Estimate tokens for chat completions with role-based overhead
        for message in messages:
            content = message.get("content", "")
            if content:
                # Better character-to-token ratio estimate (varies by model)
                # For English text: approximately 4 chars per token
                # Add overhead for each message (varies by role)
                char_per_token = 4.0
                role_overhead = 3  # tokens for role markers

                input_tokens += len(content) // char_per_token + role_overhead

                # If there are function calls, they have different tokenization
                if "function_call" in message:
                    # Function calls have higher token usage - add estimate
                    input_tokens += 10  # Approximate overhead for function call
    elif prompt:
        # Estimate tokens for completions
        input_tokens += len(prompt) // 4
    else:
        raise ValueError("Either messages or prompt is required")

    # Add token margin for system overhead (10%)
    input_tokens = int(input_tokens * 1.1)

    # Estimate cost
    input_cost = model_pricing["input_cost_per_1k"] * (input_tokens / 1000)
    output_cost = model_pricing["output_cost_per_1k"] * (max_tokens / 1000)

    return input_cost + output_cost


def estimate_openai_api_cost_from_response(response: Dict[str, Any]) -> float:
    """
    Calculate the exact cost of an OpenAI API response.

    Args:
        response: OpenAI API response dictionary containing:
            - model: The model identifier
            - usage: Dictionary with prompt_tokens and completion_tokens

    Returns:
        Cost in USD

    Raises:
        ValueError: If the response is invalid or missing required fields
    """
    if not isinstance(response, dict):
        raise ValueError("Response must be a dictionary")

    if "model" not in response:
        raise ValueError("Response missing 'model' field")

    if "usage" not in response or not isinstance(response["usage"], dict):
        raise ValueError("Response missing 'usage' field or invalid usage format")

    model = response["model"]
    usage = response["usage"]

    # Get model pricing
    model_pricing = get_model_pricing(model)
    if not model_pricing:
        raise ValueError(f"Model '{model}' not found in pricing data")

    # Extract token counts
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)

    # Calculate cost
    input_cost = model_pricing["input_cost_per_1k"] * (prompt_tokens / 1000)
    output_cost = model_pricing["output_cost_per_1k"] * (completion_tokens / 1000)

    return input_cost + output_cost
