"""
Albion Online Auto-Inventory Sequential Loop Trader & Net Profit Engine
"""

from typing import List, Tuple
import sys


def calculate_net_profit(total_silver: int, is_premium: bool = True) -> int:
    """
    Calculates estimated net silver after Albion Online marketplace taxes.
    Premium: 2.5% setup fee + 4% sales tax = 6.5% total tax (net = 93.5%).
    Non-Premium: 2.5% setup fee + 8% sales tax = 10.5% total tax (net = 89.5%).
    """
    if total_silver <= 0:
        return 0

    tax_rate = 0.065 if is_premium else 0.105
    net_silver = int(total_silver * (1.0 - tax_rate))
    return max(0, net_silver)


def generate_inventory_slot_coordinates(
    first_slot_x: int,
    first_slot_y: int,
    slot_width: int = 55,
    slot_height: int = 55,
    spacing_x: int = 6,
    spacing_y: int = 6,
    cols: int = 4,
    rows: int = 12,
    max_slots: int = 48,
) -> List[Tuple[int, int]]:
    """
    Computes screen center coordinates (x, y) for each slot in the Albion inventory grid.
    """
    coords = []
    for r in range(rows):
        for c in range(cols):
            if len(coords) >= max_slots:
                break
            cx = first_slot_x + c * (slot_width + spacing_x)
            cy = first_slot_y + r * (slot_height + spacing_y)
            coords.append((cx, cy))
    return coords


def play_sound_cue(sound_type: str = "success") -> None:
    """Emits Windows audio feedback for events."""
    if sys.platform != "win32":
        return

    try:
        import winsound

        if sound_type == "success":
            winsound.Beep(1200, 100)
        elif sound_type == "skip":
            winsound.Beep(700, 80)
        elif sound_type == "complete":
            winsound.Beep(1000, 120)
            winsound.Beep(1500, 200)
        elif sound_type == "alert":
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception:
        pass
