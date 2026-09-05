"""
Pricing engine: percentage discounts, undercut-1, and safety floor limits.
"""

def calculate_target_price(
    detected_price: int | None,
    discount_percent: float = 1.0,
    floor_price: int = 0,
    strategy: str = "percentage",
) -> tuple[int, str]:
    """Calculates target sell price based on percentage discount and safety floor.

    strategy:
      - "percentage": applies discount_percent to detected_price
      - "undercut_1": subtracts 1 Silver from detected_price
    Returns:
      (target_price, reason_string)
    """
    if detected_price is None or detected_price <= 0:
        return 0, "invalid_detected_price"

    if floor_price > 0 and detected_price < floor_price:
        return floor_price, "below_floor_safety_stop"

    if strategy == "undercut_1":
        target = max(1, detected_price - 1)
        reason = "undercut_1"
    else:
        disc = max(0.0, min(99.0, discount_percent))
        multiplier = (100.0 - disc) / 100.0
        target = max(1, int(round(detected_price * multiplier)))
        reason = f"discount_{disc:.1f}%"

    if floor_price > 0 and target < floor_price:
        return floor_price, "floor_price_clamped"

    return target, reason


def calculate_sell_price(
    number1: int | None,
    number2: int | None,
    fallback_ratio: float = 0.90,
    max_diff_percent: float = 30.0,
    strategy: str = "percentage",
    floor_price: int = 0,
) -> tuple[int, str, float]:
    """Intelligent pricing logic supporting Undercut-1, Percentage, and Tiered pricing."""
    if number1 is None and number2 is None:
        return (0, "none", 0.0)

    if number1 is None and number2 is not None:
        raw_price = int(round(number2 * fallback_ratio))
        price = max(1, raw_price, floor_price)
        reason = "floor_protected" if floor_price > raw_price else "fallback_avg"
        return (price, reason, 0.0)

    if number2 is None and number1 is not None:
        if strategy == "undercut_1":
            raw_price = number1 - 1 if number1 > 1 else 1
        else:
            raw_price = int(round(number1 * fallback_ratio))
        price = max(1, raw_price, floor_price)
        reason = "floor_protected" if floor_price > raw_price else "fallback_num1"
        return (price, reason, 0.0)

    diff_percent = abs(number1 - number2) / max(1, number2) * 100.0

    if diff_percent > max_diff_percent and number1 < number2 * (1.0 - max_diff_percent / 100.0):
        raw_price = int(round(number2 * fallback_ratio))
        price = max(1, raw_price, floor_price)
        return (price, "diff_protected", diff_percent)

    if strategy == "undercut_1":
        raw_price = number1 - 1 if number1 > 1 else 1
        reason = "undercut_1"
    elif strategy == "tiered":
        if number1 >= 1_000_000:
            raw_price = number1 - 1
        elif number1 >= 100_000:
            raw_price = int(round(number1 * 0.95))
        else:
            raw_price = int(round(number1 * fallback_ratio))
        reason = "tiered"
    else:  # percentage
        raw_price = int(round(number1 * fallback_ratio))
        reason = "percentage"

    if floor_price > 0 and raw_price < floor_price:
        price = floor_price
        reason = f"{reason}_floor_clamped"
    else:
        price = max(1, raw_price)

    return (price, reason, diff_percent)
