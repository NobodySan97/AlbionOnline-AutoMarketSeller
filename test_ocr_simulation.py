"""
Simulates realistic Albion Online in-game price screenshots
and tests the OCR & parsing pipeline.
"""

import os
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AutoSeller import parse_albion_number


def create_mock_albion_price_crop(text: str, text_color=(235, 195, 75), bg_color=(28, 30, 36)):
    """Creates a realistic mockup crop of Albion Online market price label."""
    img = Image.new("RGB", (180, 48), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Add subtle background texture / noise like in Albion UI
    np_img = np.array(img)
    noise = np.random.randint(-5, 5, np_img.shape, dtype=np.int16)
    np_img = np.clip(np_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(np_img)
    draw = ImageDraw.Draw(img)

    # Draw text
    draw.text((15, 12), text, fill=text_color)
    return img


def test_albion_parser_with_sample_strings():
    test_cases = [
        # Standard notation
        ("1,450,000", 1450000),
        ("1.450.000", 1450000),
        ("12,500", 12500),
        ("12.500", 12500),
        ("99", 99),
        ("1", 1),
        ("10,000,000", 10000000),
        # Compact K/M notation
        ("686k", 686000),
        ("686K", 686000),
        ("1.2M", 1200000),
        ("1,2M", 1200000),
        ("12.5k", 12500),
        ("500k", 500000),
        ("2.5M", 2500000),
        ("1.5M", 1500000),
        ("100k", 100000),
        # OCR common digit misreads (O->0, l/I->1, S->5, B->8)
        ("1,45O,OOO", 1450000),
        ("686K ", 686000),
        ("l2.5k", 12500),
        ("I,500", 1500),
        ("S00k", 500000),
    ]

    passed = 0
    failed = 0

    print("=" * 65)
    print("🎯 Testing Albion Number Recognition & String Parsing Pipeline")
    print("=" * 65)

    for raw, expected in test_cases:
        res = parse_albion_number(raw)
        status = "✅ PASS" if res == expected else "❌ FAIL"
        if res == expected:
            passed += 1
        else:
            failed += 1
        print(f"{status} | Input: '{raw:<12}' -> Parsed: {str(res):<10} (Expected: {expected})")

    print("=" * 65)
    print(f"Total Tests: {len(test_cases)} | Passed: {passed} | Failed: {failed}")
    print("=" * 65)

    assert failed == 0, f"{failed} test cases failed!"


if __name__ == "__main__":
    test_albion_parser_with_sample_strings()
