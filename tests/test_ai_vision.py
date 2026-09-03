"""
Unit tests for AI Vision & Synthetic Dataset Builder
"""

import os
import shutil
import numpy as np
import pytest
from PIL import Image

from ai_tools.dataset_builder import AlbionDatasetBuilder
from ai_tools.albion_ai_vision import (
    detect_enchantment_level,
    detect_item_tier_from_unique_name,
    get_localized_item_name,
    is_inventory_slot_occupied,
)


@pytest.fixture
def mock_builder(tmp_path):
    builder = AlbionDatasetBuilder(data_dir=str(tmp_path))
    # Provide sample items
    builder.items = [
        {
            "UniqueName": "T8_MAIN_SWORD",
            "LocalizedNames": {
                "IT-IT": "Spada Larga",
                "EN-US": "Broadsword",
            },
        },
        {
            "UniqueName": "T4_BAG",
            "LocalizedNames": {
                "IT-IT": "Borsa dell'Apprendista",
                "EN-US": "Adept's Bag",
            },
        },
        {
            "UniqueName": "UNIQUE_HIDEOUT",
            "LocalizedNames": {
                "IT-IT": "Kit Nascondiglio",
                "EN-US": "Hideout Kit",
            },
        },
    ]
    return builder


def test_filter_tradeable_items(mock_builder):
    filtered = mock_builder.filter_tradeable_items(tiers=["T8"])
    assert len(filtered) == 1
    assert filtered[0]["UniqueName"] == "T8_MAIN_SWORD"


def test_synthetic_grid_generation(mock_builder, tmp_path):
    # Create a dummy icon render
    dummy_icon_path = str(tmp_path / "dummy_icon.png")
    img = Image.new("RGBA", (64, 64), color=(200, 50, 50, 255))
    img.save(dummy_icon_path)

    canvas, labels = mock_builder.generate_synthetic_inventory_grid(
        render_paths=[dummy_icon_path],
        cols=2,
        rows=2,
        slot_px=32,
    )
    assert canvas.size[0] > 0 and canvas.size[1] > 0
    # Verify YOLO bbox format (cls, cx, cy, w, h) in range [0, 1]
    for cls_id, cx, cy, w, h in labels:
        assert cls_id == 0
        assert 0.0 <= cx <= 1.0
        assert 0.0 <= cy <= 1.0
        assert 0.0 < w <= 1.0
        assert 0.0 < h <= 1.0


def test_enchantment_detection():
    # Green glow (.1) - HSV hue ~60
    green_crop = np.zeros((64, 64, 3), dtype=np.uint8)
    green_crop[:8, :] = [0, 200, 0]  # BGR green
    green_crop[:, :8] = [0, 200, 0]
    assert detect_enchantment_level(green_crop) == 1

    # Blue glow (.2) - HSV hue ~110
    blue_crop = np.zeros((64, 64, 3), dtype=np.uint8)
    blue_crop[:8, :] = [220, 100, 0]  # BGR blue
    blue_crop[:, :8] = [220, 100, 0]
    assert detect_enchantment_level(blue_crop) == 2

    # Purple glow (.3) - HSV hue ~150
    purple_crop = np.zeros((64, 64, 3), dtype=np.uint8)
    purple_crop[:8, :] = [200, 0, 180]  # BGR magenta/purple
    purple_crop[:, :8] = [200, 0, 180]
    assert detect_enchantment_level(purple_crop) == 3

    # Empty / Dark (.0)
    empty_crop = np.full((64, 64, 3), 25, dtype=np.uint8)
    assert detect_enchantment_level(empty_crop) == 0


def test_tier_extraction():
    assert detect_item_tier_from_unique_name("T8_MAIN_SWORD") == 8
    assert detect_item_tier_from_unique_name("T4_BAG") == 4
    assert detect_item_tier_from_unique_name("UNIQUE_HIDEOUT") is None


def test_localization_name_lookup(mock_builder):
    name_it = get_localized_item_name("T8_MAIN_SWORD", mock_builder.items, lang="it")
    assert "Spada Larga" in name_it
    assert "T8" in name_it

    name_en = get_localized_item_name("T4_BAG", mock_builder.items, lang="en")
    assert "Adept's Bag" in name_en
    assert "T4" in name_en


def test_slot_occupancy():
    # Empty uniform dark slot
    empty_slot = np.full((50, 50, 3), 30, dtype=np.uint8)
    assert not is_inventory_slot_occupied(empty_slot)

    # Occupied slot with high variance
    occupied_slot = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
    assert is_inventory_slot_occupied(occupied_slot)
