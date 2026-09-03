"""
Albion Online AI Vision & Item Analyzer
Provides real-time enchantment detection, slot state inspection, and localization mapping.
"""

from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image


def detect_enchantment_level(icon_crop: np.ndarray) -> int:
    """
    Detects the item's enchantment level (.0, .1, .2, .3, .4)
    by analyzing the border hue and color distribution in HSV space.
    """
    if icon_crop is None or icon_crop.size == 0:
        return 0

    if len(icon_crop.shape) == 2:
        return 0

    hsv = cv2.cvtColor(icon_crop, cv2.COLOR_BGR2HSV if icon_crop.shape[2] == 3 else cv2.COLOR_BGRA2BGR)
    h, s, v = cv2.split(hsv)

    # Focus on border / corner regions where enchantment glow is concentrated
    h_len, w_len = icon_crop.shape[:2]
    border_mask = np.zeros((h_len, w_len), dtype=np.uint8)
    border_mask[:8, :] = 255
    border_mask[-8:, :] = 255
    border_mask[:, :8] = 255
    border_mask[:, -8:] = 255

    # Filter out dark background / low saturation pixels
    active_pixels = (s > 60) & (v > 60) & (border_mask > 0)
    if not np.any(active_pixels):
        return 0

    border_hues = h[active_pixels]
    if len(border_hues) < 15:
        return 0

    median_hue = float(np.median(border_hues))

    # Enchantment hue ranges (OpenCV HSV H: 0-180):
    # .1 (Green): ~35 to 80
    if 35 <= median_hue <= 80:
        return 1
    # .2 (Blue): ~85 to 130
    elif 85 <= median_hue <= 130:
        return 2
    # .3 (Purple): ~135 to 165
    elif 135 <= median_hue <= 165:
        return 3
    # .4 (Gold/Cyan/Special glow): High saturation special hue
    elif median_hue < 25 or median_hue > 165:
        return 4

    return 0


def detect_item_tier_from_unique_name(unique_name: str) -> Optional[int]:
    """Extracts integer tier from UniqueName (e.g. 'T8_MAIN_SWORD' -> 8)."""
    if not unique_name or not unique_name.startswith("T"):
        return None
    try:
        parts = unique_name.split("_")
        if parts[0][1:].isdigit():
            return int(parts[0][1:])
    except Exception:
        pass
    return None


def get_localized_item_name(
    unique_name: str,
    items_db: List[Dict],
    lang: str = "it",
) -> str:
    """Returns localized item name (e.g. 'Spada Larga (T8)') from UniqueName."""
    base_name = unique_name.split("@")[0]
    lang_key = "IT-IT" if lang.lower() == "it" else "EN-US"

    for item in items_db:
        if item.get("UniqueName") == base_name:
            localized = item.get("LocalizedNames", {})
            if lang_key in localized and localized[lang_key]:
                name = localized[lang_key]
                tier = detect_item_tier_from_unique_name(base_name)
                if tier:
                    return f"{name} (T{tier})"
                return name

    return unique_name


def is_inventory_slot_occupied(slot_crop: np.ndarray, std_threshold: float = 12.0) -> bool:
    """
    Determines if an inventory slot contains an item
    or is an empty recessed dark slot by checking standard deviation of luminance.
    """
    if slot_crop is None or slot_crop.size == 0:
        return False

    if len(slot_crop.shape) == 3:
        gray = cv2.cvtColor(slot_crop, cv2.COLOR_BGR2GRAY)
    else:
        gray = slot_crop

    # Empty slots in Albion have low variance (<10 std dev)
    std_dev = float(np.std(gray))
    return std_dev > std_threshold
