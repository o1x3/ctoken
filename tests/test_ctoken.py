from datetime import datetime
import pytest

import ctoken as occ

from ctoken.calculation import calculate_cost
from ctoken.token_estimator import ctoken, estimate_cost, CostEstimateError
from ctoken.response_parser import extract_model_details, extract_usage


class _Struct:
    """Tiny helper to build ad-hoc objects with attributes."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def _classic_response(prompt_t, completion_t, cached_t, model="gpt-4o-2024-08-06"):
    usage = _Struct(
        prompt_tokens=prompt_t,
        completion_tokens=completion_t,
        prompt_tokens_details=_Struct(cached_tokens=cached_t),
    )
    return _Struct(model=model, usage=usage)


def _new_response(input_t, output_t, cached_t, model="gpt-4o-2024-08-06"):
    usage = _Struct(
        input_tokens=input_t,
        output_tokens=output_t,
        input_tokens_details=_Struct(cached_tokens=cached_t),
    )
    return _Struct(model=model, usage=usage)


# Test pricing data used in tests
_TEST_PRICING = {
    ("gpt-4.5-preview", "2025-02-27"): {
        "input_price": 5.00,
        "cached_input_price": 2.50,
        "output_price": 15.00,
    },
    ("gpt-4o", None): {
        "input_price": 3.00,
        "cached_input_price": 1.50,
        "output_price": 6.00,
    },
    ("gpt-4o", "2024-11-20"): {
        "input_price": 3.00,
        "cached_input_price": 1.50,
        "output_price": 6.00,
    },
    ("gpt-4o", "2024-08-06"): {
        "input_price": 3.00,
        "cached_input_price": 1.50,
        "output_price": 6.00,
    },
    ("gpt-4o", "2024-05-13"): {
        "input_price": 3.00,
        "cached_input_price": 1.50,
        "output_price": 6.00,
    },
}


@pytest.fixture(autouse=True)
def monkeypatch_pricing(monkeypatch):
    """Force `load_pricing()` to return our test pricing dict."""
    monkeypatch.setattr(occ.pricing_data, "load_pricing", lambda: _TEST_PRICING)

    # Also mock get_model_pricing for the special test case
    original_get_model_pricing = occ.pricing_data.get_model_pricing

    def mocked_get_model_pricing(model_name):
        # Special case for tests
        if model_name == "gpt-4-0125-preview":
            return {
                "model": "gpt-4-turbo",
                "version": "0125",
                "input_cost_per_1k": 0.01,
                "output_cost_per_1k": 0.03,
            }
        return original_get_model_pricing(model_name)

    monkeypatch.setattr(occ.pricing_data, "get_model_pricing", mocked_get_model_pricing)


# --------------------------------------------------------------------------- #
# Unit tests                                                                  #
# --------------------------------------------------------------------------- #
def test_calculate_cost_basic_rounding():
    usage = {"prompt_tokens": 1_000, "completion_tokens": 2_000, "cached_tokens": 200}
    rates = {"input_price": 1.0, "cached_input_price": 0.5, "output_price": 2.0}
    costs = calculate_cost(usage, rates)

    assert costs == {
        "prompt_cost_uncached": 0.0008,  # 800 / 1M * $1
        "prompt_cost_cached": 0.0001,  # 200 / 1M * $0.5
        "completion_cost": 0.004,  # 2 000 / 1M * $2
        "total_cost": 0.0049,
    }


@pytest.mark.parametrize(
    "model, exp_date",
    [
        ("gpt-4.5-preview-2025-02-27", "2025-02-27"),
        ("gpt-4o-2024-11-20", "2024-11-20"),
        ("gpt-4o-2024-08-06", "2024-08-06"),
        ("gpt-4o-2024-05-13", "2024-05-13"),
        ("gpt-4o", "latest"),
    ],
)
def test_extract_model_details(model, exp_date):
    details = extract_model_details(model)
    if "gpt-4.5" in model:
        assert details == {"model_name": "gpt-4.5-preview", "model_date": exp_date}
    else:
        assert details == {"model_name": "gpt-4o", "model_date": exp_date}


def test_extract_usage_classic_and_new():
    classic = _classic_response(100, 50, 30)
    new = _new_response(100, 50, 30)
    for obj in (classic, new):
        assert extract_usage(obj) == {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "cached_tokens": 30,
        }


# --------------------------------------------------------------------------- #
# Integration tests: ctoken                                                   #
# --------------------------------------------------------------------------- #
def test_estimate_cost_single_response():
    resp = _classic_response(1_000, 500, 100)
    cost = ctoken(resp)
    # Check that all values are numbers
    for key, value in cost.items():
        if key in [
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "cached_tokens",
        ]:
            assert isinstance(value, int), (
                f"Expected {key} to be an int, got {type(value)}"
            )
        else:
            assert isinstance(value, float), (
                f"Expected {key} to be a float, got {type(value)}"
            )

    total = (
        cost["prompt_cost_uncached"]
        + cost["prompt_cost_cached"]
        + cost["completion_cost"]
    )
    assert cost["total_cost"] == pytest.approx(total)


def test_estimate_cost_stream(monkeypatch):
    # two chunks: first w/o usage, last with usage
    dummy_chunks = (
        _Struct(model="ignored", foo="bar"),
        _classic_response(2_000, 0, 0),
    )
    cost = ctoken(iter(dummy_chunks))
    assert float(cost["completion_cost"]) == pytest.approx(0.0)
    assert float(cost["total_cost"]) != pytest.approx(0.0)


def test_missing_pricing_raises(monkeypatch):
    resp = _classic_response(10, 10, 0, model="non-existent-2099-01-01")
    with pytest.raises(CostEstimateError):
        ctoken(resp)
