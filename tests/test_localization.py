import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoSeller import STRINGS


def test_localization_keys_parity():
    en_keys = set(STRINGS["en"].keys())
    it_keys = set(STRINGS["it"].keys())

    missing_in_it = en_keys - it_keys
    missing_in_en = it_keys - en_keys

    assert not missing_in_it, f"Keys in EN but missing in IT: {missing_in_it}"
    assert not missing_in_en, f"Keys in IT but missing in EN: {missing_in_en}"


def test_region_map_parity():
    en_regions = set(STRINGS["en"]["region_map"].keys())
    it_regions = set(STRINGS["it"]["region_map"].keys())

    assert en_regions == it_regions, f"Region map mismatch: {en_regions ^ it_regions}"


def test_placeholders_match():
    placeholder_pattern = re.compile(r"\{[^{}]*\}")

    for key, en_val in STRINGS["en"].items():
        if isinstance(en_val, str):
            it_val = STRINGS["it"][key]
            en_placeholders = placeholder_pattern.findall(en_val)
            it_placeholders = placeholder_pattern.findall(it_val)

            assert len(en_placeholders) == len(it_placeholders), (
                f"Placeholder count mismatch for key '{key}': "
                f"EN has {en_placeholders} ({len(en_placeholders)}), "
                f"IT has {it_placeholders} ({len(it_placeholders)})"
            )
