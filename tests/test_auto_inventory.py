"""
Unit tests for Auto-Inventory and Net Profit Calculation Engine
"""

from ai_tools.auto_inventory_seller import (
    calculate_net_profit,
    generate_inventory_slot_coordinates,
    play_sound_cue,
)


def test_net_profit_calculation_premium():
    # 1,000,000 Silver with Premium (6.5% tax) -> 935,000 net
    assert calculate_net_profit(1_000_000, is_premium=True) == 935_000

    # 100,000 Silver with Premium -> 93,500 net
    assert calculate_net_profit(100_000, is_premium=True) == 93_500

    # 0 Silver
    assert calculate_net_profit(0, is_premium=True) == 0


def test_net_profit_calculation_non_premium():
    # 1,000,000 Silver without Premium (10.5% tax) -> 895,000 net
    assert calculate_net_profit(1_000_000, is_premium=False) == 895_000

    # 50,000 Silver without Premium -> 44,750 net
    assert calculate_net_profit(50_000, is_premium=False) == 44_750


def test_inventory_slot_coordinates_generation():
    slots = generate_inventory_slot_coordinates(
        first_slot_x=100,
        first_slot_y=200,
        slot_width=50,
        slot_height=50,
        spacing_x=10,
        spacing_y=10,
        cols=4,
        rows=12,
        max_slots=48,
    )
    assert len(slots) == 48
    # Slot 0 (Row 0, Col 0) -> (100, 200)
    assert slots[0] == (100, 200)
    # Slot 1 (Row 0, Col 1) -> (100 + 60, 200) -> (160, 200)
    assert slots[1] == (160, 200)
    # Slot 4 (Row 1, Col 0) -> (100, 200 + 60) -> (100, 260)
    assert slots[4] == (100, 260)


def test_play_sound_cue():
    # Should execute safely without raising any exceptions
    play_sound_cue("success")
    play_sound_cue("skip")
    play_sound_cue("complete")
    play_sound_cue("alert")
