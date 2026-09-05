"""
Configuration management and defaults.
"""

DEFAULT_CONFIG = {
    "language": "it",
    "mode": "3point",  # "3point" or "ocr"
    "pos_a": {"x": 2119, "y": 571},
    "pos_b": {"x": 1194, "y": 841},
    "pos_c": {"x": 1612, "y": 972},
    "ocr_pos_sell": {"x": 2119, "y": 571},
    "ocr_price_box": {"x1": 1150, "y1": 420, "x2": 1300, "y2": 455},
    "ocr_price_input": {"x": 1250, "y": 841},
    "ocr_create_order": {"x": 1612, "y": 972},
    "toggle_hotkey": "F10",
    "discount_percent": 1.0,
    "strategy": "percentage",
    "floor_price": 0,
    "delay_ab_ms": 300,
    "delay_bc_ms": 200,
    "delay_ca_ms": 400,
    "delay_ocr_ms": 250,
    "human_mouse": True,
    "human_typing": True,
    "jitter": True,
    "max_items": 0,
    "tesseract_path": "",
    "auto_template": False,
    "logic": {"fallback_ratio": 0.90, "max_difference_percent": 30},
}


def deep_merge_config(default: dict, override: dict) -> dict:
    """Recursively merges user configuration dictionary into default dictionary."""
    result = dict(default)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge_config(result[k], v)
        else:
            result[k] = v
    return result
