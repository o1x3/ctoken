# CToken Scripts

## `openai_pricing_scraper.py`

Scrapes OpenAI pricing and updates the package pricing data.

**Requirements:**
- selenium
- pandas
- pyperclip

**Usage:**
```bash
python scripts/openai_pricing_scraper.py
```

**What it does:**
1. Opens Chrome browser
2. Navigates to OpenAI pricing page
3. Clicks "Copy page" button to get markdown
4. Parses the Standard tier Text tokens pricing
5. Updates `data/openai_text_tokens_pricing.csv`
6. Updates `ctoken/data/pricing_data.py`

The package automatically uses the updated pricing data.
