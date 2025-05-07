# CToken Scripts

This directory contains utility scripts for maintaining and updating the `ctoken` package.

## Scripts Overview

### `openai_pricing_scraper.py`

This script scrapes the OpenAI pricing page to get the latest pricing information for OpenAI models. It uses Selenium with undetected-chromedriver to navigate the OpenAI website and extract pricing data.

**Requirements:**
- undetected-chromedriver
- selenium
- pandas

**Usage:**
```bash
python scripts/openai_pricing_scraper.py
```

The script will:
1. Open a Chrome browser window
2. Navigate to the OpenAI pricing page
3. Extract pricing data for text token models
4. Save the data to a CSV file in the `data/` directory

**Notes:**
- You may need to solve a CAPTCHA during execution
- The script has hardcoded paths for Chrome and ChromeDriver. Update these paths if needed.

### `verify_pricing_data.py`

This script verifies the pricing data in the `ctoken` package against the latest scraped data. It compares the two data sources and reports any discrepancies.

**Requirements:**
- pandas

**Usage:**
```bash
python scripts/verify_pricing_data.py
```

The script will:
1. Load pricing data from the `ctoken` package
2. Load the latest scraped pricing data
3. Compare the two data sources
4. Report any discrepancies

## Pricing Data Scripts

### `update_remote_pricing.py`

This script fetches OpenAI pricing data from GitHub and updates the local pricing data files in both CSV and Python dictionary formats.

Usage:
```bash
python scripts/update_remote_pricing.py
```

The script will:
1. Fetch pricing data from GitHub repository
2. Update the CSV file at `data/openai_text_tokens_pricing.csv`
3. Update the Python dictionary at `ctoken/data/pricing_data.py`

The GitHub URL used for fetching pricing data can be configured by modifying the `GITHUB_URL` constant in the script.

## Developer Workflow

1. Run `openai_pricing_scraper.py` to get the latest pricing data
2. Run `verify_pricing_data.py` to check for discrepancies
3. Update the pricing data in the `ctoken` package if needed 