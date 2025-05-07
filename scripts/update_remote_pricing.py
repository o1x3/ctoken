"""
Remote pricing data updater script.

This script fetches OpenAI pricing data from GitHub and
updates the local pricing data files in both CSV and Python formats.
"""

import csv
import io
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

import requests
import pandas as pd

# Add the parent directory to the path so we can import ctoken
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Get directories
PACKAGE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = PACKAGE_DIR / "data"
PRICING_CSV_PATH = DATA_DIR / "openai_text_tokens_pricing.csv"
PRICING_PY_PATH = PACKAGE_DIR / "ctoken" / "data" / "pricing_data.py"

# GitHub repo URL for pricing data
GITHUB_URL = "https://raw.githubusercontent.com/o1x3/ctoken/main/data/openai_text_tokens_pricing.csv"


def _parse_price(price_str: str) -> float:
    """
    Parse a price string into a float value.

    Args:
        price_str: String representation of price (e.g., "$0.002" or "-")

    Returns:
        Float value of the price
    """
    if not price_str or price_str.strip() == "-":
        return 0.0

    # Remove $ and any other non-numeric characters except decimal point
    clean_price = "".join(c for c in price_str if c.isdigit() or c == ".")
    try:
        return float(clean_price)
    except ValueError:
        return 0.0


def fetch_github_pricing_data() -> Dict:
    """
    Fetch pricing data from GitHub repository.

    Returns:
        Dictionary containing pricing data
    """
    try:
        response = requests.get(GITHUB_URL, timeout=10)
        response.raise_for_status()

        # Parse CSV data
        df = pd.read_csv(io.StringIO(response.text))

        # Convert the DataFrame to dictionary format
        pricing_data = []
        for _, row in df.iterrows():
            model_data = {
                "model": row["Model"],
                "version": row.get("Version", ""),
                "input_price": _parse_price(row.get("Input", "0")),
                "cached_input_price": _parse_price(row.get("Cached input", "0")),
                "output_price": _parse_price(row.get("Output", "0")),
            }
            pricing_data.append(model_data)

        return {"models": pricing_data}

    except Exception as e:
        print(f"Error: Failed to fetch pricing data from GitHub: {str(e)}")
        return {"models": []}


def update_csv_file(pricing_data: Dict) -> None:
    """
    Update the CSV file with the latest pricing data.

    Args:
        pricing_data: Dictionary containing pricing data
    """
    # Extract models data
    models = pricing_data.get("models", [])

    if not models:
        print("Error: No model data available to update CSV")
        return

    # Prepare data for CSV
    csv_data = []
    for model in models:
        row = {
            "Model": model["model"],
            "Version": model.get("version", ""),
            "Input": f"${model['input_price']:.2f}"
            if model.get("input_price")
            else "-",
            "Cached input": f"${model['cached_input_price']:.3f}"
            if model.get("cached_input_price")
            else "-",
            "Output": f"${model['output_price']:.2f}"
            if model.get("output_price")
            else "-",
        }
        csv_data.append(row)

    # Write to CSV file
    with open(PRICING_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Model", "Version", "Input", "Cached input", "Output"]
        )
        writer.writeheader()
        writer.writerows(csv_data)

    print(f"Updated CSV file at {PRICING_CSV_PATH}")


def update_python_dict(pricing_data: Dict) -> None:
    """
    Update the Python dictionary in pricing_data.py with the latest pricing data.

    Args:
        pricing_data: Dictionary containing pricing data
    """
    models = pricing_data.get("models", [])

    if not models:
        print("Error: No model data available to update Python dictionary")
        return

    # Create Python dictionary entries
    py_entries = []
    for model in models:
        model_name = model["model"]
        version = model.get("version", "") or "latest"

        # Get prices (dollars per 1000 tokens)
        input_price = model.get("input_price", 0)
        cached_input_price = model.get("cached_input_price", 0)
        output_price = model.get("output_price", 0)

        # Format the pricing entry (storing as dollars per 1000 tokens)
        entry = (
            f'    ("{model_name}", "{version}"): {{\n'
            f'        "input_price": {input_price:.2f},\n'
            f'        "cached_input_price": {cached_input_price:.3f},\n'
            f'        "output_price": {output_price:.2f},\n'
            f"    }},"
        )
        py_entries.append(entry)

    # Create the Python file content
    py_content = [
        '"""',
        "Pricing data for OpenAI models.",
        "",
        "This module contains the pricing data for OpenAI models in dictionary format.",
        "This file is auto-generated by update_remote_pricing.py",
        f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        '"""',
        "",
        "# Pricing data in dollars per 1000 tokens (input/cached_input/output)",
        "PRICING_DATA = {",
        '    # Format: (model_name, version): {"input_price": float, "cached_input_price": float, "output_price": float}',
        *py_entries,
        "}",
        "",
    ]

    # Write to Python file
    with open(PRICING_PY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(py_content))

    print(f"Updated Python dictionary at {PRICING_PY_PATH}")


def update_pricing_data() -> None:
    """
    Main function to update pricing data from GitHub.

    Fetches data from GitHub, then updates both CSV and Python dictionary files.
    """
    print("Fetching latest pricing data from GitHub...")
    pricing_data = fetch_github_pricing_data()

    if not pricing_data.get("models"):
        print("Error: No pricing data available from GitHub")
        return

    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(PACKAGE_DIR / "ctoken" / "data", exist_ok=True)

    # Update both file formats
    update_csv_file(pricing_data)
    update_python_dict(pricing_data)

    print("Pricing data successfully updated!")


if __name__ == "__main__":
    update_pricing_data()
