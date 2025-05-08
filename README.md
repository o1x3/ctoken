# ctoken

A high-performance Python library for estimating costs of OpenAI API calls. Track your API expenses precisely with support for all OpenAI models and APIs.

[![PyPI version](https://badge.fury.io/py/ctoken.svg?icon=si%3Apython)](https://badge.fury.io/py/ctoken)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/o1x3/ctoken/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Install

```bash
pip install ctoken
```

## Features

- Accurate cost estimation for all OpenAI models
- Compatible with all OpenAI APIs (Chat Completions and Responses)
- Detailed cost breakdown (prompt, completion, cached tokens)
- Works with streaming responses
- External pricing data with no hardcoded values
- Dynamic data refresh from remote sources
- Mock response support for testing
- High-performance token counting with efficient caching
- Smart model detection for accurate pricing
- Robust error handling through unified exception type

## Quick Start

```python
from openai import OpenAI
from ctoken import ctoken

client = OpenAI(api_key="YOUR_API_KEY")

# Make your API call
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)

# Get the cost estimate and token counts
result = ctoken(response)
print(f"Tokens: {result['total_tokens']} | Cost: ${result['total_cost']}")
```

## Real-world Examples

### 1. Chat Completion API

```python
from openai import OpenAI
from ctoken import ctoken

client = OpenAI(api_key="sk-...")
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hi there!"}],
)

# Get token counts and cost breakdown
result = ctoken(resp)
print(f"Token counts: {result['prompt_tokens']} prompt, {result['completion_tokens']} completion")
print(f"Total cost: ${result['total_cost']}")
# Complete result:
# {'prompt_tokens'       : 3,
#  'completion_tokens'   : 12,
#  'total_tokens'        : 15,
#  'cached_tokens'       : 0,
#  'prompt_cost_uncached': 0.00000150,
#  'prompt_cost_cached'  : 0.00000000,
#  'completion_cost'     : 0.00000600,
#  'total_cost'          : 0.00000750}
```

### 2. Responses API

```python
from openai import OpenAI
from ctoken import ctoken

client = OpenAI(api_key="sk-...")
resp = client.responses.create(
    model="gpt-4.1-mini",
    input=[{"role": "user", "content": "Hi there!"}],
)

# Get detailed cost breakdown
print(ctoken(resp))
# {'prompt_cost_uncached': 0.00000120,
#  'prompt_cost_cached'  : 0.00000000,
#  'completion_cost'     : 0.00001920,
#  'total_cost'          : 0.00002040}
```

### 3. Streaming Responses

```python
from openai import OpenAI
from ctoken import ctoken

client = OpenAI(api_key="sk-...")
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a poem about AI"}],
    stream=True
)

# Collect the stream and use it
response_chunks = []
for chunk in stream:
    response_chunks.append(chunk)
    # Use the chunk for whatever you need
    # ...

# Get cost at the end of the stream
cost = ctoken(response_chunks)
print(f"Streaming API call cost: ${cost['total_cost']}")
```

### 4. Batch Estimation

```python
from openai import OpenAI
from ctoken import ctoken
import pandas as pd

client = OpenAI(api_key="sk-...")
responses = []
total_cost = 0

# Collect multiple responses
questions = ["What is AI?", "How does quantum computing work?", "Explain neural networks"]
for question in questions:
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": question}],
    )
    responses.append(resp)
    
    # Accumulate costs
    cost_estimate = ctoken(resp)
    total_cost += cost_estimate['total_cost']

# Create a report
df = pd.DataFrame([{
    'prompt': responses[i].choices[0].message.content[:50] + "...",
    'tokens': responses[i].usage.total_tokens,
    'cost': ctoken(responses[i])['total_cost']
} for i in range(len(responses))])

print(f"Total batch cost: ${total_cost:.8f}")
print(df)
```

### 5. Refresh Pricing Data

```python
from ctoken import refresh_pricing

# Force-reload the current pricing data (cache TTL is 24h)
refresh_pricing()
```

### 6. Pricing Data Sources

The library contains pricing data in a bundled Python dictionary format. It also supports fetching pricing from:

1. Local file: `data/gpt_pricing_data.csv` if available
2. Remote source: Official GitHub repository
3. Bundled fallback data: A default dataset included with the package

This approach ensures pricing data remains up-to-date without requiring library updates but also provides fast access through the bundled dictionary.

### 7. Error Handling

```python
from ctoken import ctoken, CostEstimateError

try:
    cost = ctoken(response)
    print(f"Cost: ${cost['total_cost']}")
except CostEstimateError as e:
    print(f"Error estimating cost: {e}")
    # Handle gracefully
```

## API Reference

```python
from ctoken import ctoken, estimate_cost, refresh_pricing, CostEstimateError

# Main function for cost estimation
ctoken(response) → dict[str, Any]
    """
    Accepts a ChatCompletion, streamed chunks, or Response object.
    Returns a dict with:
        prompt_tokens        : int   # Number of prompt tokens
        completion_tokens    : int   # Number of completion tokens
        total_tokens         : int   # Total tokens used
        cached_tokens        : int   # Number of cached tokens
        prompt_cost_uncached : float # Cost of non-cached prompt tokens
        prompt_cost_cached  : float # Cost of cached prompt tokens (often reduced rate)
        completion_cost      : float # Cost of model-generated tokens
        total_cost           : float # Total cost of the API call
    """

# Alias for backward compatibility
estimate_cost = ctoken

# Force reload pricing data
refresh_pricing() → None
    """Force-reload the remote pricing CSV (cache TTL is 24h)."""

# Exception for errors
CostEstimateError
    """Unified exception for recoverable input, parsing, or pricing errors."""
```

## Production Usage Tips

### Cost Monitoring in Flask Application

```python
from flask import Flask, request, jsonify
from openai import OpenAI
from ctoken import ctoken
import logging

app = Flask(__name__)
client = OpenAI(api_key="sk-...")

# Configure cost logging
cost_logger = logging.getLogger("api_costs")
handler = logging.FileHandler("api_costs.log")
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
cost_logger.addHandler(handler)
cost_logger.setLevel(logging.INFO)

@app.route("/ask", methods=["POST"])
def ask_ai():
    user_query = request.json.get("query", "")
    user_id = request.json.get("user_id", "anonymous")
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_query}]
    )
    
    # Log the cost with user ID
    result = ctoken(response)
    cost_logger.info(
        f"User: {user_id} | Query: {user_query[:30]}... | "
        f"Tokens: {result['total_tokens']} | Cost: ${result['total_cost']}"
    )
    
    return jsonify({
        "answer": response.choices[0].message.content,
        "tokens": {
            "prompt": result['prompt_tokens'],
            "completion": result['completion_tokens'],
            "total": result['total_tokens']
        },
        "cost": result['total_cost']
    })

if __name__ == "__main__":
    app.run(debug=True)
```

### Budget Management

```python
from openai import OpenAI
from ctoken import ctoken
import os
from datetime import datetime

client = OpenAI(api_key="sk-...")
DAILY_BUDGET = 1.0  # $1 per day

# Track daily spending
today = datetime.now().strftime("%Y-%m-%d")
spent_today = 0.0

def make_api_call(query):
    global spent_today
    
    # Check budget before making the call
    if spent_today >= DAILY_BUDGET:
        return {"error": "Daily budget exceeded"}
    
    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )
    
    # Calculate and add to spending
    cost = ctoken(response)
    spent_today += cost['total_cost']
    
    return {
        "response": response.choices[0].message.content,
        "cost": cost['total_cost'],
        "remaining_budget": DAILY_BUDGET - spent_today
    }
```

## Performance Improvements

This library has been optimized for performance with:

- Efficient caching of pricing data
- Improved error handling with detailed messages
- Smart model name parsing for versioned models
- Optimized token calculations using Python's Decimal for financial accuracy
- Reduced memory usage with streamlined data structures
- Enhanced attribute access for safe navigation of nested objects

## License

MIT

## Links

- [GitHub Repository](https://github.com/o1x3/ctoken)
- [PyPI Package](https://pypi.org/project/ctoken/)
- [OpenAI Pricing Page](https://platform.openai.com/pricing)

## Project Structure

The project is organized as follows:

```
ctoken/
├── ctoken/                # Main package
│   ├── __init__.py        # Package initialization
│   ├── core.py            # Core functionality
│   ├── estimate.py        # Cost estimation
│   ├── parser.py          # Token parsing
│   ├── pricing.py         # Pricing data handling
│   └── data/              # Package data files
│       └── gpt_pricing_data.csv   # Pricing data
├── data/                  # External data files
│   └── openai_text_tokens_pricing.csv  # Latest scraped pricing
├── examples/              # Example code
│   ├── basic_usage.py     # Basic token counting
│   ├── cost_estimation.py # Cost estimation examples
│   ├── demo_ctoken_usage.py  # Complete usage demo
│   └── demo_cost_estimation.py  # Detailed cost estimations
├── scripts/               # Utility scripts
│   ├── openai_pricing_scraper.py  # Scraper for OpenAI pricing
│   └── verify_pricing_data.py     # Verify pricing data
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_api_cost_estimation.py
│   ├── test_ctoken.py
│   └── test_model_pricing.py
├── .gitignore
├── MANIFEST.in
├── pyproject.toml
├── pytest.ini
├── README.md
├── requirements-dev.txt
└── setup.py
```

### Directory Overview

- **ctoken/**: Main package source code
- **data/**: External data files including scraped pricing information
- **examples/**: Example code showing how to use the package
- **scripts/**: Utility scripts for maintenance tasks
- **tests/**: Test suite for the package 