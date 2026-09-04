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
    VK_KEY_MAP,
    WindowsHotkeyPoller,
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


def test_vk_key_map_and_poller():
    assert VK_KEY_MAP["F10"] == 0x79
    assert VK_KEY_MAP["F4"] == 0x73
    assert VK_KEY_MAP["F9"] == 0x78
    assert VK_KEY_MAP["PAUSE"] == 0x13
    assert VK_KEY_MAP["INSERT"] == 0x2D

    triggered = []
    poller = WindowsHotkeyPoller(lambda: triggered.append(True), default_key="F10")
    assert poller.target_vk == 0x79
    poller.set_key("F4")
    assert poller.target_vk == 0x73
    poller.stop()
