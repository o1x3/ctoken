import sys
import os
import pandas as pd

# Add the parent directory to the path so we can import ctoken
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ctoken.pricing_data import get_all_model_pricings


def verify_pricing_data():
    """
    Verify the pricing data in the ctoken package against the latest scraped data.
    """
    print("Verifying pricing data...")

    # Get pricing data from ctoken
    ctoken_pricing = get_all_model_pricings()

    # Load latest scraped data
    try:
        scraped_data_path = os.path.join(
            os.path.dirname(__file__), "../data/openai_text_tokens_pricing.csv"
        )
        scraped_pricing = pd.read_csv(scraped_data_path)
    except Exception as e:
        print(f"Error loading scraped data: {str(e)}")
        return

    # Count models in both sources
    print(f"Models in ctoken: {len(ctoken_pricing)}")
    print(f"Models in scraped data: {len(scraped_pricing)}")

    # Compare model names
    ctoken_models = {p["model"] for p in ctoken_pricing}
    scraped_models = set(scraped_pricing["Model"].unique())

    # Check for models in scraped data but not in ctoken
    missing_in_ctoken = scraped_models - ctoken_models
    if missing_in_ctoken:
        print("\nModels in scraped data but not in ctoken:")
        for model in missing_in_ctoken:
            print(f"- {model}")

    # Check for models in ctoken but not in scraped data
    missing_in_scraped = ctoken_models - scraped_models
    if missing_in_scraped:
        print("\nModels in ctoken but not in scraped data:")
        for model in missing_in_scraped:
            print(f"- {model}")

    # Check for price discrepancies
    print("\nChecking for price discrepancies...")

    discrepancies = []
    # Use iloc to get numerical indices of columns for safety
    input_col_idx = scraped_pricing.columns.get_loc("Input")
    output_col_idx = scraped_pricing.columns.get_loc("Output")

    for idx, row in scraped_pricing.iterrows():
        model_name = row["Model"]

        # Find corresponding model in ctoken
        ctoken_model = next(
            (p for p in ctoken_pricing if p["model"] == model_name), None
        )
        if not ctoken_model:
            continue

        # Extract prices from scraped data by column name (handling currency symbols and parsing)
        try:
            input_price_str = row["Input"]
            output_price_str = row["Output"]

            # Clean the price strings
            if isinstance(input_price_str, str):
                input_price = float(input_price_str.replace("$", "").strip())
            else:
                input_price = 0.0

            if isinstance(output_price_str, str):
                output_price = float(output_price_str.replace("$", "").strip())
            else:
                output_price = 0.0

            # Compare with ctoken prices (convert from per-token to per-1000-tokens)
            ctoken_input_price = ctoken_model.get("input_cost_per_1k", 0.0) * 1000
            ctoken_output_price = ctoken_model.get("output_cost_per_1k", 0.0) * 1000

            # Check for significant discrepancies (>1%)
            input_diff_pct = (
                abs(input_price - ctoken_input_price) / max(input_price, 0.0001) * 100
            )
            output_diff_pct = (
                abs(output_price - ctoken_output_price)
                / max(output_price, 0.0001)
                * 100
            )

            if input_diff_pct > 1 or output_diff_pct > 1:
                discrepancies.append(
                    {
                        "model": model_name,
                        "scraped_input": input_price,
                        "ctoken_input": ctoken_input_price,
                        "input_diff_pct": input_diff_pct,
                        "scraped_output": output_price,
                        "ctoken_output": ctoken_output_price,
                        "output_diff_pct": output_diff_pct,
                    }
                )
        except Exception as e:
            print(f"Error processing {model_name}: {str(e)}")

    # Report discrepancies
    if discrepancies:
        print("\nPrice discrepancies found:")
        for d in discrepancies:
            print(f"Model: {d['model']}")
            print(
                f"  Input: ${d['scraped_input']} (scraped) vs ${d['ctoken_input']} (ctoken) - {d['input_diff_pct']:.2f}% diff"
            )
            print(
                f"  Output: ${d['scraped_output']} (scraped) vs ${d['ctoken_output']} (ctoken) - {d['output_diff_pct']:.2f}% diff"
            )
    else:
        print("No significant price discrepancies found!")

    print("\nVerification complete.")


if __name__ == "__main__":
    verify_pricing_data()
