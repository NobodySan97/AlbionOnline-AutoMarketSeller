import json
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoSeller import (
    AlbionMarketAutoClickerApp,
    deep_merge_config,
    get_gaussian_delay,
    generate_bezier_curve,
    STRINGS,
)


def test_deep_merge_config():
    default_cfg = {
        "pos_a": {"x": 100, "y": 200},
        "delay_ab_ms": 300,
        "toggle_hotkey": "F10",
    }
    user_cfg = {
        "pos_a": {"x": 500, "y": 600},
        "delay_ab_ms": 150,
    }
    merged = deep_merge_config(default_cfg, user_cfg)
    assert merged["pos_a"]["x"] == 500
    assert merged["pos_a"]["y"] == 600
    assert merged["delay_ab_ms"] == 150
    assert merged["toggle_hotkey"] == "F10"


def test_gaussian_delay_bounds():
    for _ in range(50):
        d = get_gaussian_delay(0.1, 0.2)
        assert 0.1 <= d <= 0.2


def test_bezier_curve_points():
    pts = generate_bezier_curve((0, 0), (100, 100), num_points=15, deviation=10)
    assert len(pts) == 15
    assert pts[0] == (0, 0)
    assert pts[-1] == (100, 100)


def test_3point_strings_parity():
    en_keys = set(STRINGS["en"].keys())
    it_keys = set(STRINGS["it"].keys())
    assert en_keys == it_keys
    for key in en_keys:
        assert key in STRINGS["it"]
