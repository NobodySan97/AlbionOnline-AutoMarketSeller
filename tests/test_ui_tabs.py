import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoSeller import STRINGS, AlbionMarketAutoClickerApp

def test_new_tab_keys_exist_in_all_languages():
    required_keys = [
        "tab_mode_fast",
        "tab_mode_ocr",
        "tab_settings",
        "banner_mode_fast",
        "banner_mode_ocr",
        "mode_switched_fast",
        "mode_switched_ocr",
        "section_timing_fast",
        "section_timing_ocr",
    ]
    for lang in ["en", "it"]:
        for key in required_keys:
            assert key in STRINGS[lang], f"Missing key '{key}' in language '{lang}'"
            assert isinstance(STRINGS[lang][key], str)
            assert len(STRINGS[lang][key]) > 0

def test_app_has_tab_and_preset_methods():
    assert hasattr(AlbionMarketAutoClickerApp, "setup_ui")
    assert hasattr(AlbionMarketAutoClickerApp, "on_tab_changed")
    assert hasattr(AlbionMarketAutoClickerApp, "on_change_mode")
    assert hasattr(AlbionMarketAutoClickerApp, "apply_preset_discount")
