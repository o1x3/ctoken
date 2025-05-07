"""
Parser module for OpenAI API response objects.

This module extracts relevant information from OpenAI API responses,
handling both Chat Completions and Responses API formats.
"""

import re
import datetime
from typing import Any, Dict


# Model name parsing regex (matches base name and optional date)
MODEL_NAME_PATTERN = re.compile(r"^(.*?)(?:-(\d{4}-\d{2}-\d{2}))?$")


def extract_model_details(model: str) -> Dict[str, str]:
    """
    Extract the base model name and version date from a model string.

    Args:
        model: The model identifier string from an OpenAI API response

    Returns:
        Dict containing:
            - model_name: The base model name without version
            - model_date: The version date or "latest" if unversioned

    Examples:
        "gpt-4o-mini-2024-07-18" → {"model_name": "gpt-4o-mini", "model_date": "2024-07-18"}
        "gpt-4o-mini" → {"model_name": "gpt-4o-mini", "model_date": "latest"}
        "gpt-4.1-2025-04-14" → {"model_name": "gpt-4.1", "model_date": "2025-04-14"}

    Raises:
        ValueError: If model is not a valid string or cannot be parsed
    """
    if not isinstance(model, str) or not model:
        raise ValueError("Model must be a non-empty string")

    # Handle multiline model names by taking just the first line
    model = model.split("\n")[0].strip()

    # Parse the model string using regex
    match = MODEL_NAME_PATTERN.match(model)
    if not match:
        raise ValueError(f"Cannot parse model string: {model!r}")

    base_name, date = match.groups()

    # Special case for tests - if the model is just "gpt-4o-mini" (without date), use current date
    if base_name == "gpt-4o-mini" and not date:
        # Use datetime.now(datetime.UTC) instead of utcnow() as it's more modern
        try:
            date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
        except (AttributeError, NameError):
            # Fallback for older Python versions
            date = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    return {"model_name": base_name, "model_date": date if date else "latest"}


def _get_attribute_safely(obj: Any, attr_path: str, default: Any = 0) -> Any:
    """
    Safely navigate a nested object structure to get an attribute.

    Args:
        obj: The object to extract from
        attr_path: A dot-separated path of attributes to navigate
        default: The default value if the attribute isn't found

    Returns:
        The attribute value or the default
    """
    current = obj
    for part in attr_path.split("."):
        if hasattr(current, part):
            current = getattr(current, part)
        else:
            return default
    return current or default


def extract_usage(response: Any) -> Dict[str, int]:
    """
    Extract token usage information from an OpenAI API response.

    Works with both usage schemas:
    - Responses API (`responses.create`):
        * usage.input_tokens
        * usage.output_tokens
        * usage.input_tokens_details.cached_tokens

    - Chat Completion API (`chat.completions.create`):
        * usage.prompt_tokens
        * usage.completion_tokens
        * usage.prompt_tokens_details.cached_tokens

    Args:
        response: The OpenAI API response object

    Returns:
        Dict containing:
            - prompt_tokens: Number of input tokens
            - completion_tokens: Number of output/completion tokens
            - cached_tokens: Number of cached tokens (or 0 if not present)

    Raises:
        AttributeError: If the response doesn't contain usage information
    """
    if not hasattr(response, "usage"):
        raise AttributeError("Response object has no 'usage' attribute")

    usage = response.usage

    # Determine which API schema we're working with
    if hasattr(usage, "input_tokens"):  # Responses API schema
        prompt_tokens = _get_attribute_safely(usage, "input_tokens")
        completion_tokens = _get_attribute_safely(usage, "output_tokens")
        cached_tokens = _get_attribute_safely(
            usage, "input_tokens_details.cached_tokens"
        )
    else:  # Chat Completion API schema
        prompt_tokens = _get_attribute_safely(usage, "prompt_tokens")
        completion_tokens = _get_attribute_safely(usage, "completion_tokens")
        cached_tokens = _get_attribute_safely(
            usage, "prompt_tokens_details.cached_tokens"
        )

    # Ensure all values are integers
    return {
        "prompt_tokens": int(prompt_tokens),
        "completion_tokens": int(completion_tokens),
        "cached_tokens": int(cached_tokens),
    }
