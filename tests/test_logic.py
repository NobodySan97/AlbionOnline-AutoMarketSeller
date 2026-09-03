import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoSeller import (
    calculate_sell_price,
    deep_merge_config,
    detect_tesseract_binary,
    parse_albion_number,
)


def test_parse_standard_integers():
    assert parse_albion_number("500") == 500
    assert parse_albion_number("12345") == 12345
    assert parse_albion_number("1") == 1


def test_parse_thousands_separators():
    # US format
    assert parse_albion_number("1,500") == 1500
    assert parse_albion_number("1,500,000") == 1500000
    # EU format (dots as thousand separators)
    assert parse_albion_number("1.500") == 1500
    assert parse_albion_number("1.500.000") == 1500000
    assert parse_albion_number("250.000") == 250000


def test_parse_suffixes():
    assert parse_albion_number("500k") == 500000
    assert parse_albion_number("500K") == 500000
    assert parse_albion_number("1.5m") == 1500000
    assert parse_albion_number("1.5M") == 1500000
    assert parse_albion_number("1,5M") == 1500000
    assert parse_albion_number("10.5k") == 10500
    assert parse_albion_number("10,5k") == 10500
    assert parse_albion_number("2T") == 2000


def test_parse_ocr_artifacts():
    assert parse_albion_number(" 1,500. ") == 1500
    assert parse_albion_number(".1.500.000.") == 1500000
    assert parse_albion_number("O500") == 500
    assert parse_albion_number("l500") == 1500
    assert parse_albion_number("S00") == 500
    assert parse_albion_number("") is None
    assert parse_albion_number(None) is None
    assert parse_albion_number("abc???") is None


def test_calculate_sell_price_normal():
    price, reason, diff = calculate_sell_price(1000, 1050, 0.90, 30.0)
    assert price == 900
    assert reason == "percentage"


def test_calculate_sell_price_fallback_avg_only():
    price, reason, diff = calculate_sell_price(None, 10000, 0.90, 30.0)
    assert price == 9000
    assert reason == "fallback_avg"


def test_calculate_sell_price_fallback_num1_only():
    price, reason, diff = calculate_sell_price(5000, None, 0.90, 30.0)
    assert price == 4500
    assert reason == "fallback_num1"


def test_calculate_sell_price_undercut_trap():
    # Current lowest is 10 silver (scam/trap/misread), average is 100,000
    # Diff is ~99.99% > 30% -> Should fallback to average: 100,000 * 0.9 = 90,000
    price, reason, diff = calculate_sell_price(10, 100000, 0.90, 30.0)
    assert price == 90000
    assert reason == "diff_protected"


def test_calculate_sell_price_never_zero_or_negative():
    price, reason, diff = calculate_sell_price(0, 0, 0.90, 30.0)
    assert price == 1  # Minimum market price in Albion is 1 silver
    price, reason, diff = calculate_sell_price(1, 1, 0.90, 30.0)
    assert price == 1


def test_deep_merge_config():
    default = {
        "language": "en",
        "logic": {"fallback_ratio": 0.90, "max_diff": 30, "robust_attempts": 12},
        "sleep": {"between_clicks": {"min": 0.04, "max": 0.06}, "before_input": 0.05}
    }
    user = {
        "language": "it",
        "logic": {"fallback_ratio": 0.85},
        "custom_key": "test"
    }
    merged = deep_merge_config(default, user)
    assert merged["language"] == "it"
    assert merged["logic"]["fallback_ratio"] == 0.85
    assert merged["logic"]["max_diff"] == 30
    assert merged["logic"]["robust_attempts"] == 12
    assert merged["sleep"]["between_clicks"]["min"] == 0.04
    assert merged["custom_key"] == "test"


def test_detect_tesseract_binary():
    # Should return string without crashing
    path = detect_tesseract_binary()
    assert isinstance(path, str)
