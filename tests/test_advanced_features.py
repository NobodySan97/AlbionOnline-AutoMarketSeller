import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoSeller import (
    calculate_sell_price,
    generate_bezier_curve,
    get_gaussian_delay,
    SessionStats,
)


def test_pricing_percentage_strategy():
    # 1000 current, 1050 avg, 10% discount -> 900
    price, reason, diff = calculate_sell_price(
        number1=1000,
        number2=1050,
        strategy="percentage",
        fallback_ratio=0.90,
        max_diff_percent=30.0,
        floor_price=0,
    )
    assert price == 900
    assert reason == "percentage"


def test_pricing_undercut_1_strategy():
    # 1000 current -> 999
    price, reason, diff = calculate_sell_price(
        number1=1000,
        number2=1050,
        strategy="undercut_1",
        fallback_ratio=0.90,
        max_diff_percent=30.0,
        floor_price=0,
    )
    assert price == 999
    assert reason == "undercut_1"


def test_pricing_undercut_1_with_undercut_trap():
    # Current is 10 (troll price), Avg is 100,000 -> Diff > 30% -> Fallback to 90% of avg: 90,000
    price, reason, diff = calculate_sell_price(
        number1=10,
        number2=100000,
        strategy="undercut_1",
        fallback_ratio=0.90,
        max_diff_percent=30.0,
        floor_price=0,
    )
    assert price == 90000
    assert reason == "diff_protected"


def test_pricing_tiered_strategy():
    # High tier > 1,000,000 -> undercut by 1
    price_high, _, _ = calculate_sell_price(
        number1=2000000,
        number2=2050000,
        strategy="tiered",
        fallback_ratio=0.90,
        max_diff_percent=30.0,
        floor_price=0,
    )
    assert price_high == 1999999

    # Mid tier (100k - 1M) -> 5% off
    price_mid, _, _ = calculate_sell_price(
        number1=500000,
        number2=520000,
        strategy="tiered",
        fallback_ratio=0.90,
        max_diff_percent=30.0,
        floor_price=0,
    )
    assert price_mid == 475000

    # Low tier (< 100k) -> fallback ratio (10% off) -> 45,000
    price_low, _, _ = calculate_sell_price(
        number1=50000,
        number2=52000,
        strategy="tiered",
        fallback_ratio=0.90,
        max_diff_percent=30.0,
        floor_price=0,
    )
    assert price_low == 45000


def test_pricing_floor_price_protection():
    # Calculated is 900, but floor_price is 5000 -> clamped to 5000
    price, reason, _ = calculate_sell_price(
        number1=1000,
        number2=1050,
        strategy="percentage",
        fallback_ratio=0.90,
        max_diff_percent=30.0,
        floor_price=5000,
    )
    assert price == 5000
    assert "floor" in reason


def test_bezier_curve_generation():
    points = generate_bezier_curve(start=(100, 100), end=(500, 500), num_points=20, deviation=30)
    assert len(points) == 20
    assert points[0] == (100, 100)
    assert points[-1] == (500, 500)
    for x, y in points:
        assert isinstance(x, int)
        assert isinstance(y, int)


def test_gaussian_delay():
    delay = get_gaussian_delay(min_val=0.04, max_val=0.08)
    assert 0.04 <= delay <= 0.08


def test_session_stats():
    stats = SessionStats()
    stats.record_sale(price=10000, item_name="Item 1")
    stats.record_sale(price=25000, item_name="Item 2")
    assert stats.total_orders == 2
    assert stats.total_silver == 35000
    assert stats.average_price == 17500
    assert len(stats.records) == 2
    assert len(stats.orders) == 2  # Backward-compatible property alias
    assert stats.orders is stats.records  # Zero duplicate memory allocation

    # Test bounded capacity doesn't leak memory on high volume
    stats.MAX_IN_MEMORY_RECORDS = 5
    stats.records = type(stats.records)(maxlen=5)
    for i in range(10):
        stats.record_sale(price=100, item_name=f"Item {i}")
    assert len(stats.records) == 5
    assert stats.total_orders == 12


def test_detect_tesseract_custom_path(tmp_path):
    from AutoSeller import detect_tesseract_binary
    fake_exe = tmp_path / "tesseract.exe"
    fake_exe.write_text("fake binary")
    detected = detect_tesseract_binary(str(fake_exe))
    assert detected == str(fake_exe)

