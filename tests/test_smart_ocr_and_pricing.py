import os
import sys
import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoSeller import (
    calculate_target_price,
    OcrReader,
    detect_tesseract_binary,
    deep_merge_config,
    VK_KEY_MAP,
    WindowsHotkeyPoller,
)


def test_calculate_target_price_discounts():
    # 1.0% discount on 10,000 -> 9,900
    price, reason = calculate_target_price(10000, discount_percent=1.0)
    assert price == 9900
    assert reason == "discount_1.0%"

    # 2.5% discount on 10,000 -> 9,750
    price, reason = calculate_target_price(10000, discount_percent=2.5)
    assert price == 9750
    assert reason == "discount_2.5%"

    # 5% discount on 20,000 -> 19,000
    price, reason = calculate_target_price(20000, discount_percent=5.0)
    assert price == 19000

    # 10% discount on 50,000 -> 45,000
    price, reason = calculate_target_price(50000, discount_percent=10.0)
    assert price == 45000


def test_calculate_target_price_undercut_1():
    # Undercut 1 Silver
    price, reason = calculate_target_price(15400, strategy="undercut_1")
    assert price == 15399
    assert reason == "undercut_1"

    # Undercut 1 on 1 silver -> minimum is 1
    price, reason = calculate_target_price(1, strategy="undercut_1")
    assert price == 1


def test_calculate_target_price_floor_protection():
    # Detected price is 10,000, 10% discount would be 9,000, but floor is 9,500 -> Clamped to 9,500
    price, reason = calculate_target_price(10000, discount_percent=10.0, floor_price=9500)
    assert price == 9500
    assert reason == "floor_price_clamped"

    # Detected price is 4,000, but safety floor is 5,000 -> Safety stop (do not dump item!)
    price, reason = calculate_target_price(4000, discount_percent=2.0, floor_price=5000)
    assert price == 5000
    assert reason == "below_floor_safety_stop"


def test_calculate_target_price_invalid_inputs():
    assert calculate_target_price(None)[0] == 0
    assert calculate_target_price(0)[0] == 0
    assert calculate_target_price(-500)[0] == 0


def test_ocr_preprocess_image_variants():
    canvas = np.zeros((50, 150), dtype=np.uint8)
    canvas[:] = 20
    canvas[15:35, 20:130] = 230
    pil_img = Image.fromarray(canvas)

    variants = OcrReader.preprocess_image(pil_img)
    assert len(variants) == 4
    for v in variants:
        assert isinstance(v, Image.Image)


def test_dual_mode_config_merge():
    default_cfg = {
        "mode": "3point",
        "pos_a": {"x": 10, "y": 20},
        "ocr_pos_sell": {"x": 100, "y": 200},
        "ocr_price_box": {"x1": 50, "y1": 60, "x2": 150, "y2": 100},
        "discount_percent": 1.0,
        "floor_price": 0,
    }
    user_cfg = {
        "mode": "ocr",
        "discount_percent": 3.5,
        "floor_price": 2500,
        "ocr_price_box": {"x1": 55, "y1": 65, "x2": 160, "y2": 105},
    }
    merged = deep_merge_config(default_cfg, user_cfg)
    assert merged["mode"] == "ocr"
    assert merged["discount_percent"] == 3.5
    assert merged["floor_price"] == 2500
    assert merged["ocr_price_box"]["x1"] == 55
    assert merged["pos_a"]["x"] == 10
