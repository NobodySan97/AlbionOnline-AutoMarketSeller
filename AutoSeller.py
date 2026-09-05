"""
Albion Online — Auto Market Seller
Dual-Mode Market Automation:
  Mode 1: 3-Point Fast Clicker (Sell -> [-] Undercut 1 Silver -> Create Order)
  Mode 2: Smart OCR Seller (Sell -> OCR Lowest Order -> Custom % Discount & Floor Protection -> Type Price -> Create Order)

Modular Architecture Entrypoint:
  - core.timer: Windows 1ms high-precision timer, async audio, DPI awareness
  - core.input: Human Bézier mouse curves and typing simulation
  - core.hotkey: Hardware-level polling via Windows GetAsyncKeyState
  - core.pricing: Target price calculation (% discount, undercut-1, floor protection)
  - core.ocr: OpenCV preprocessing, Tesseract OCR, and Albion number parsing
  - core.stats: Session statistics with bounded circular buffer and CSV export
  - core.config: Configuration defaults and recursive deep merge
  - ui.strings: Multilingual localizations (Italian, English)
  - ui.app: CustomTkinter GUI interface and execution worker
"""

import os
import sys

# Ensure local directory is in Python module search path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Re-export core modules for 100% backward compatibility with tests & scripts
from core.timer import (
    init_windows_dpi,
    enable_high_res_timer,
    disable_high_res_timer,
    async_beep,
)
from core.input import (
    generate_bezier_curve,
    get_gaussian_delay,
    human_move_to,
    human_type,
)
from core.hotkey import (
    VK_KEY_MAP,
    is_key_pressed_win32,
    WindowsHotkeyPoller,
)
from core.pricing import (
    calculate_target_price,
    calculate_sell_price,
)
from core.ocr import (
    parse_albion_number,
    detect_tesseract_binary,
    OcrReader,
    TemplateMatcher,
)
from core.stats import (
    SessionStats,
)
from core.config import (
    DEFAULT_CONFIG,
    deep_merge_config,
)
from ui.strings import (
    STRINGS,
)
from ui.app import (
    AlbionMarketAutoClickerApp,
    AutoSellerApp,
    main,
    USE_CUSTOMTKINTER,
)

__all__ = [
    "init_windows_dpi",
    "enable_high_res_timer",
    "disable_high_res_timer",
    "async_beep",
    "generate_bezier_curve",
    "get_gaussian_delay",
    "human_move_to",
    "human_type",
    "VK_KEY_MAP",
    "is_key_pressed_win32",
    "WindowsHotkeyPoller",
    "calculate_target_price",
    "calculate_sell_price",
    "parse_albion_number",
    "detect_tesseract_binary",
    "OcrReader",
    "TemplateMatcher",
    "SessionStats",
    "DEFAULT_CONFIG",
    "deep_merge_config",
    "STRINGS",
    "AlbionMarketAutoClickerApp",
    "AutoSellerApp",
    "main",
    "USE_CUSTOMTKINTER",
]

# Initialize DPI awareness and 1ms timer at module import
init_windows_dpi()
enable_high_res_timer()

if __name__ == "__main__":
    main()
