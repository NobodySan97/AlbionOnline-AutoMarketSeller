import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoSeller import (
    DEFAULT_CONFIG,
    deep_merge_config,
    AlbionMarketAutoClickerApp,
)


def test_default_config_has_all_required_keys():
    required_keys = [
        "language", "mode", "pos_a", "pos_b", "pos_c",
        "ocr_pos_sell", "ocr_price_box", "ocr_price_input", "ocr_create_order",
        "toggle_hotkey", "discount_percent", "strategy", "floor_price",
        "delay_ab_ms", "delay_bc_ms", "delay_ca_ms", "delay_ocr_ms",
        "human_mouse", "human_typing", "jitter", "max_items",
        "tesseract_path", "logic"
    ]
    for k in required_keys:
        assert k in DEFAULT_CONFIG, f"Key '{k}' missing from DEFAULT_CONFIG"

    assert isinstance(DEFAULT_CONFIG["pos_a"], dict)
    assert "x" in DEFAULT_CONFIG["pos_a"] and "y" in DEFAULT_CONFIG["pos_a"]
    assert isinstance(DEFAULT_CONFIG["ocr_price_box"], dict)
    assert all(coord in DEFAULT_CONFIG["ocr_price_box"] for coord in ["x1", "y1", "x2", "y2"])


def test_deep_merge_config_behavior():
    base = {
        "a": 1,
        "nested": {"x": 10, "y": 20},
        "list_val": [1, 2],
    }
    override = {
        "nested": {"y": 99, "z": 30},
        "new_key": "hello",
    }
    merged = deep_merge_config(base, override)
    assert merged["a"] == 1
    assert merged["nested"]["x"] == 10
    assert merged["nested"]["y"] == 99
    assert merged["nested"]["z"] == 30
    assert merged["new_key"] == "hello"
    assert merged["list_val"] == [1, 2]


def test_config_load_with_corrupt_file(tmp_path):
    corrupt_file = tmp_path / "corrupt_config.json"
    corrupt_file.write_text("{ this is not valid json !!! }", encoding="utf-8")

    class DummyApp:
        CONFIG_FILE = str(corrupt_file)
        load_config = AlbionMarketAutoClickerApp.load_config

    app = DummyApp()
    loaded = app.load_config()
    assert loaded["language"] == DEFAULT_CONFIG["language"]
    assert loaded["toggle_hotkey"] == DEFAULT_CONFIG["toggle_hotkey"]


def test_config_load_with_non_dict_file(tmp_path):
    list_file = tmp_path / "list_config.json"
    list_file.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    class DummyApp:
        CONFIG_FILE = str(list_file)
        load_config = AlbionMarketAutoClickerApp.load_config

    app = DummyApp()
    loaded = app.load_config()
    assert loaded["mode"] == DEFAULT_CONFIG["mode"]


def test_config_save_atomic_and_load_roundtrip(tmp_path):
    cfg_file = tmp_path / "test_config.json"

    class MockEntry:
        def __init__(self, val):
            self.val = str(val)
        def get(self):
            return self.val

    class MockVar:
        def __init__(self, val):
            self.val = val
        def get(self):
            return self.val

    class MockMenu:
        def __init__(self, val):
            self.val = val
        def get(self):
            return self.val

    class DummyApp:
        CONFIG_FILE = str(cfg_file)
        load_config = AlbionMarketAutoClickerApp.load_config
        save_config = AlbionMarketAutoClickerApp.save_config

        def __init__(self):
            self.config = deep_merge_config(DEFAULT_CONFIG, {})
            self.lang = "en"
            self.logs = []
            # Mock widgets
            self.entry_pos_a_x = MockEntry("100")
            self.entry_pos_a_y = MockEntry("200")
            self.entry_pos_b_x = MockEntry("300")
            self.entry_pos_b_y = MockEntry("400")
            self.entry_pos_c_x = MockEntry("500")
            self.entry_pos_c_y = MockEntry("600")

            self.entry_ocr_sell_x = MockEntry("150")
            self.entry_ocr_sell_y = MockEntry("250")
            self.entry_box_x1 = MockEntry("10")
            self.entry_box_y1 = MockEntry("20")
            self.entry_box_x2 = MockEntry("70")
            self.entry_box_y2 = MockEntry("40")
            self.entry_ocr_input_x = MockEntry("350")
            self.entry_ocr_input_y = MockEntry("450")
            self.entry_ocr_create_x = MockEntry("550")
            self.entry_ocr_create_y = MockEntry("650")

            self.entry_discount = MockEntry("3.5%")
            self.entry_floor_price = MockEntry("50000")
            self.hotkey_menu = MockMenu("F4")

            self.entry_delay_ab = MockEntry("250")
            self.entry_delay_bc = MockEntry("180")
            self.entry_delay_ca = MockEntry("350")
            self.entry_delay_ocr = MockEntry("220")

            self.switch_human_var = MockVar(False)
            self.switch_type_var = MockVar(True)
            self.switch_jitter_var = MockVar(False)
            self.entry_max_items = MockEntry("25")
            self.entry_tesseract = MockEntry(r"C:\Custom\Tesseract\tesseract.exe")

        def log(self, msg, category=""):
            self.logs.append((category, msg))

    app = DummyApp()
    app.save_config()

    assert os.path.exists(cfg_file)
    with open(cfg_file, "r", encoding="utf-8") as f:
        saved_json = json.load(f)

    assert saved_json["pos_a"] == {"x": 100, "y": 200}
    assert saved_json["ocr_price_box"] == {"x1": 10, "y1": 20, "x2": 70, "y2": 40}
    assert saved_json["discount_percent"] == 3.5
    assert saved_json["floor_price"] == 50000
    assert saved_json["toggle_hotkey"] == "F4"
    assert saved_json["delay_ab_ms"] == 250
    assert saved_json["delay_ocr_ms"] == 220
    assert saved_json["human_mouse"] is False
    assert saved_json["jitter"] is False
    assert saved_json["max_items"] == 25
    assert saved_json["tesseract_path"] == r"C:\Custom\Tesseract\tesseract.exe"
    assert saved_json["language"] == "en"

    # Now load it back
    app2 = DummyApp()
    loaded_cfg = app2.load_config()
    assert loaded_cfg["tesseract_path"] == r"C:\Custom\Tesseract\tesseract.exe"
    assert loaded_cfg["discount_percent"] == 3.5
    assert loaded_cfg["max_items"] == 25


def test_config_save_resilience_against_bad_inputs(tmp_path):
    cfg_file = tmp_path / "bad_inputs.json"

    class MockEntry:
        def __init__(self, val):
            self.val = str(val)
        def get(self):
            return self.val

    class DummyApp:
        CONFIG_FILE = str(cfg_file)
        save_config = AlbionMarketAutoClickerApp.save_config

        def __init__(self):
            self.config = deep_merge_config(DEFAULT_CONFIG, {})
            self.lang = "it"
            self.logs = []
            # Corrupted / empty text fields
            self.entry_pos_a_x = MockEntry("not a number")
            self.entry_pos_a_y = MockEntry("")
            self.entry_discount = MockEntry("invalid_float%")
            self.entry_delay_ab = MockEntry("-500")

        def log(self, msg, category=""):
            self.logs.append((category, msg))

    app = DummyApp()
    app.save_config()

    # Verify app didn't crash and saved fallback defaults
    assert os.path.exists(cfg_file)
    with open(cfg_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # pos_a x defaulted to 2119, y defaulted to 571
    assert data["pos_a"]["x"] == 2119
    assert data["pos_a"]["y"] == 571
    # discount_percent stayed 1.0
    assert data["discount_percent"] == 1.0
    # delay_ab clamped to at least min 50ms
    assert data["delay_ab_ms"] >= 50
