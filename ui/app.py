"""
Main CustomTkinter User Interface and Execution Engine for Albion Market Seller.
"""

import csv
import ctypes
import datetime
import json
import math
import os
import random
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

import pyautogui
from pynput import mouse
import pytesseract

try:
    import keyboard
except ImportError:
    keyboard = None

try:
    import customtkinter as ctk
    USE_CUSTOMTKINTER = True
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
except ImportError:
    USE_CUSTOMTKINTER = False

from core.timer import enable_high_res_timer, init_windows_dpi, async_beep
from core.input import human_move_to, human_type, get_gaussian_delay
from core.hotkey import WindowsHotkeyPoller
from core.pricing import calculate_target_price
from core.ocr import OcrReader, detect_tesseract_binary
from core.stats import SessionStats
from core.config import DEFAULT_CONFIG, deep_merge_config
from ui.strings import STRINGS

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Initialize DPI and 1ms timer
init_windows_dpi()
enable_high_res_timer()

class AlbionMarketAutoClickerApp:
    CONFIG_FILE = os.path.join(BASE_DIR, "auto_config.json")

    def __init__(self, root):
        self.root = root
        self.lang = "it"
        self.strings = STRINGS[self.lang]
        self.stats = SessionStats()

        # State flags
        self.is_running = False
        self.worker_thread = None
        self.worker_stop_event = threading.Event()
        self.mouse_listener = None
        self.wizard_step = 0
        self.single_capture_target = None
        self.area_p1 = None
        self.registered_hotkey = None
        self.hotkey_poller = None
        self._prev_bound_key = None
        self._last_hotkey_trigger = 0.0

        # Load Configuration
        self.config = self.load_config()
        self.lang = self.config.get("language", "it")
        self.strings = STRINGS.get(self.lang, STRINGS["it"])

        # Auto-configure Tesseract
        tess_bin = detect_tesseract_binary(self.config.get("tesseract_path", ""))
        if tess_bin:
            try:
                pytesseract.pytesseract.tesseract_cmd = tess_bin
            except Exception:
                pass

        # Setup User Interface
        self.setup_ui()

        # Register Global Hotkey
        self.bind_global_hotkey(self.config.get("toggle_hotkey", "F10"))

        # Log Welcome
        self.log(self.strings["status_ready"], category="System")

    def load_config(self) -> dict:
        default_cfg = {
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
        if os.path.isfile(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_cfg = deep_merge_config(default_cfg, data)
            except Exception:
                pass
        return default_cfg

    def save_config(self):
        try:
            # 3-Point Coordinates
            if hasattr(self, "entry_pos_a_x"):
                self.config["pos_a"] = {"x": int(self.entry_pos_a_x.get()), "y": int(self.entry_pos_a_y.get())}
                self.config["pos_b"] = {"x": int(self.entry_pos_b_x.get()), "y": int(self.entry_pos_b_y.get())}
                self.config["pos_c"] = {"x": int(self.entry_pos_c_x.get()), "y": int(self.entry_pos_c_y.get())}

            # Smart OCR Coordinates
            if hasattr(self, "entry_ocr_sell_x"):
                self.config["ocr_pos_sell"] = {"x": int(self.entry_ocr_sell_x.get()), "y": int(self.entry_ocr_sell_y.get())}
                self.config["ocr_price_box"] = {
                    "x1": int(self.entry_box_x1.get()),
                    "y1": int(self.entry_box_y1.get()),
                    "x2": int(self.entry_box_x2.get()),
                    "y2": int(self.entry_box_y2.get()),
                }
                self.config["ocr_price_input"] = {"x": int(self.entry_ocr_input_x.get()), "y": int(self.entry_ocr_input_y.get())}
                self.config["ocr_create_order"] = {"x": int(self.entry_ocr_create_x.get()), "y": int(self.entry_ocr_create_y.get())}

            # Strategy & Pricing
            if hasattr(self, "entry_discount"):
                try:
                    disc_str = self.entry_discount.get().replace("%", "").strip()
                    self.config["discount_percent"] = float(disc_str) if disc_str else 1.0
                except ValueError:
                    pass
            if hasattr(self, "entry_floor_price"):
                try:
                    self.config["floor_price"] = int(self.entry_floor_price.get().strip() or 0)
                except ValueError:
                    pass

            if hasattr(self, "hotkey_menu"):
                self.config["toggle_hotkey"] = self.hotkey_menu.get()

            # Timings
            if hasattr(self, "entry_delay_ab"):
                self.config["delay_ab_ms"] = int(self.entry_delay_ab.get())
                self.config["delay_bc_ms"] = int(self.entry_delay_bc.get())
                self.config["delay_ca_ms"] = int(self.entry_delay_ca.get())
            if hasattr(self, "entry_delay_ocr"):
                self.config["delay_ocr_ms"] = int(self.entry_delay_ocr.get())

            if hasattr(self, "switch_human_var"):
                self.config["human_mouse"] = self.switch_human_var.get()
            if hasattr(self, "switch_type_var"):
                self.config["human_typing"] = self.switch_type_var.get()
            if hasattr(self, "switch_jitter_var"):
                self.config["jitter"] = self.switch_jitter_var.get()
            if hasattr(self, "entry_max_items"):
                self.config["max_items"] = int(self.entry_max_items.get())

            self.config["language"] = self.lang

            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            self.log("💾 Config saved successfully.", category="Config")
        except Exception as e:
            self.log(f"⚠️ Error saving config: {e}", category="Error")

    def setup_ui(self):
        self.root.title(self.strings["app_title"])
        self.root.geometry("680x820")
        self.root.minsize(640, 750)

        # Header Frame with Title & Language
        header = ctk.CTkFrame(self.root, fg_color="#1a1c23", corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        lbl_header = ctk.CTkLabel(
            header,
            text=self.strings["header_title"],
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color="#f39c12",
        )
        lbl_header.pack(side="left", padx=20)

        self.lang_menu = ctk.CTkOptionMenu(
            header,
            values=["🇮🇹 Italiano", "🇬🇧 English"],
            command=self.on_change_language,
            width=120,
            height=28,
            fg_color="#2c3e50",
            button_color="#34495e",
        )
        self.lang_menu.set("🇮🇹 Italiano" if self.lang == "it" else "🇬🇧 English")
        self.lang_menu.pack(side="right", padx=15)

        # Big START / STOP Button
        self.btn_toggle = ctk.CTkButton(
            self.root,
            text=f"{self.strings['btn_start']} [{self.config.get('toggle_hotkey', 'F10')}]",
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            height=48,
            command=self.toggle_clicking,
        )
        self.btn_toggle.pack(fill="x", padx=15, pady=(10, 6))

        # Main Tabview with 3 Dedicated Tabs
        self.tabview = ctk.CTkTabview(self.root, command=self.on_tab_changed)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 4))

        self.tab_fast = self.tabview.add(self.strings["tab_mode_fast"])
        self.tab_ocr = self.tabview.add(self.strings["tab_mode_ocr"])
        self.tab_settings = self.tabview.add(self.strings["tab_settings"])

        # ================= TAB 1: ⚡ UNDERCUT -1 SILVER (NATIVO) =================
        lbl_fast_info = ctk.CTkLabel(
            self.tab_fast,
            text=self.strings["banner_mode_fast"],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3498db",
            wraplength=600,
        )
        lbl_fast_info.pack(fill="x", padx=10, pady=(4, 6))

        # 3-Point Wizard Button
        self.btn_wizard = ctk.CTkButton(
            self.tab_fast,
            text=self.strings["btn_wizard"],
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8e44ad",
            hover_color="#732d91",
            height=32,
            command=self.start_setup_wizard,
        )
        self.btn_wizard.pack(fill="x", padx=10, pady=(0, 6))

        # Pos A Row
        frame_pos_a = ctk.CTkFrame(self.tab_fast, fg_color="transparent")
        frame_pos_a.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(frame_pos_a, text=f"{self.strings['label_pos_a']} (Sell):", width=95, anchor="w").pack(side="left")
        ctk.CTkLabel(frame_pos_a, text="X:").pack(side="left", padx=(5, 2))
        self.entry_pos_a_x = ctk.CTkEntry(frame_pos_a, width=60)
        self.entry_pos_a_x.insert(0, str(self.config["pos_a"]["x"]))
        self.entry_pos_a_x.pack(side="left")
        ctk.CTkLabel(frame_pos_a, text="Y:").pack(side="left", padx=(6, 2))
        self.entry_pos_a_y = ctk.CTkEntry(frame_pos_a, width=60)
        self.entry_pos_a_y.insert(0, str(self.config["pos_a"]["y"]))
        self.entry_pos_a_y.pack(side="left")
        ctk.CTkButton(
            frame_pos_a, text=self.strings["btn_capture"], width=65, command=lambda: self.start_single_capture("Pos A"), fg_color="#2980b9"
        ).pack(side="right", padx=(5, 0))
        ctk.CTkButton(
            frame_pos_a, text=self.strings["btn_test"], width=55, command=lambda: self.test_click_position("Pos A"), fg_color="#7f8c8d"
        ).pack(side="right")

        # Pos B Row
        frame_pos_b = ctk.CTkFrame(self.tab_fast, fg_color="transparent")
        frame_pos_b.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(frame_pos_b, text=f"{self.strings['label_pos_b']} ([-]):", width=95, anchor="w").pack(side="left")
        ctk.CTkLabel(frame_pos_b, text="X:").pack(side="left", padx=(5, 2))
        self.entry_pos_b_x = ctk.CTkEntry(frame_pos_b, width=60)
        self.entry_pos_b_x.insert(0, str(self.config["pos_b"]["x"]))
        self.entry_pos_b_x.pack(side="left")
        ctk.CTkLabel(frame_pos_b, text="Y:").pack(side="left", padx=(6, 2))
        self.entry_pos_b_y = ctk.CTkEntry(frame_pos_b, width=60)
        self.entry_pos_b_y.insert(0, str(self.config["pos_b"]["y"]))
        self.entry_pos_b_y.pack(side="left")
        ctk.CTkButton(
            frame_pos_b, text=self.strings["btn_capture"], width=65, command=lambda: self.start_single_capture("Pos B"), fg_color="#2980b9"
        ).pack(side="right", padx=(5, 0))
        ctk.CTkButton(
            frame_pos_b, text=self.strings["btn_test"], width=55, command=lambda: self.test_click_position("Pos B"), fg_color="#7f8c8d"
        ).pack(side="right")

        # Pos C Row
        frame_pos_c = ctk.CTkFrame(self.tab_fast, fg_color="transparent")
        frame_pos_c.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(frame_pos_c, text=f"{self.strings['label_pos_c']} (Create):", width=95, anchor="w").pack(side="left")
        ctk.CTkLabel(frame_pos_c, text="X:").pack(side="left", padx=(5, 2))
        self.entry_pos_c_x = ctk.CTkEntry(frame_pos_c, width=60)
        self.entry_pos_c_x.insert(0, str(self.config["pos_c"]["x"]))
        self.entry_pos_c_x.pack(side="left")
        ctk.CTkLabel(frame_pos_c, text="Y:").pack(side="left", padx=(6, 2))
        self.entry_pos_c_y = ctk.CTkEntry(frame_pos_c, width=60)
        self.entry_pos_c_y.insert(0, str(self.config["pos_c"]["y"]))
        self.entry_pos_c_y.pack(side="left")
        ctk.CTkButton(
            frame_pos_c, text=self.strings["btn_capture"], width=65, command=lambda: self.start_single_capture("Pos C"), fg_color="#2980b9"
        ).pack(side="right", padx=(5, 0))
        ctk.CTkButton(
            frame_pos_c, text=self.strings["btn_test"], width=55, command=lambda: self.test_click_position("Pos C"), fg_color="#7f8c8d"
        ).pack(side="right")

        # Delays for Fast Mode
        card_timing_fast = ctk.CTkFrame(self.tab_fast, fg_color="#21252d", corner_radius=6)
        card_timing_fast.pack(fill="x", padx=10, pady=(8, 4))
        lbl_sec_timing_fast = ctk.CTkLabel(
            card_timing_fast,
            text=self.strings["section_timing_fast"],
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        lbl_sec_timing_fast.pack(anchor="w", padx=10, pady=(6, 2))

        # Delay A->B
        frame_dab = ctk.CTkFrame(card_timing_fast, fg_color="transparent")
        frame_dab.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(frame_dab, text=self.strings["label_delay_ab"]).pack(side="left")
        self.entry_delay_ab = ctk.CTkEntry(frame_dab, width=70)
        self.entry_delay_ab.insert(0, str(self.config.get("delay_ab_ms", 300)))
        self.entry_delay_ab.pack(side="right")

        # Delay B->C
        frame_dbc = ctk.CTkFrame(card_timing_fast, fg_color="transparent")
        frame_dbc.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(frame_dbc, text=self.strings["label_delay_bc"]).pack(side="left")
        self.entry_delay_bc = ctk.CTkEntry(frame_dbc, width=70)
        self.entry_delay_bc.insert(0, str(self.config.get("delay_bc_ms", 200)))
        self.entry_delay_bc.pack(side="right")

        # Delay C->A
        frame_dca = ctk.CTkFrame(card_timing_fast, fg_color="transparent")
        frame_dca.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(frame_dca, text=self.strings["label_delay_ca"]).pack(side="left")
        self.entry_delay_ca = ctk.CTkEntry(frame_dca, width=70)
        self.entry_delay_ca.insert(0, str(self.config.get("delay_ca_ms", 400)))
        self.entry_delay_ca.pack(side="right")


        # ================= TAB 2: 🧠 SCONTO % (SMART OCR) =================
        lbl_ocr_info = ctk.CTkLabel(
            self.tab_ocr,
            text=self.strings["banner_mode_ocr"],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#1abc9c",
            wraplength=600,
        )
        lbl_ocr_info.pack(fill="x", padx=10, pady=(4, 6))

        # OCR Wizard Button
        self.btn_wizard_ocr = ctk.CTkButton(
            self.tab_ocr,
            text=self.strings["btn_wizard_ocr"],
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8e44ad",
            hover_color="#732d91",
            height=32,
            command=self.start_ocr_wizard,
        )
        self.btn_wizard_ocr.pack(fill="x", padx=10, pady=(0, 6))

        # Pos Sell (Item)
        f_ocr_sell = ctk.CTkFrame(self.tab_ocr, fg_color="transparent")
        f_ocr_sell.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(f_ocr_sell, text=f"{self.strings['label_pos_sell']}:", width=110, anchor="w").pack(side="left")
        ctk.CTkLabel(f_ocr_sell, text="X:").pack(side="left", padx=(4, 1))
        self.entry_ocr_sell_x = ctk.CTkEntry(f_ocr_sell, width=55)
        self.entry_ocr_sell_x.insert(0, str(self.config["ocr_pos_sell"]["x"]))
        self.entry_ocr_sell_x.pack(side="left")
        ctk.CTkLabel(f_ocr_sell, text="Y:").pack(side="left", padx=(4, 1))
        self.entry_ocr_sell_y = ctk.CTkEntry(f_ocr_sell, width=55)
        self.entry_ocr_sell_y.insert(0, str(self.config["ocr_pos_sell"]["y"]))
        self.entry_ocr_sell_y.pack(side="left")
        ctk.CTkButton(f_ocr_sell, text=self.strings["btn_capture"], width=60, command=lambda: self.start_single_capture("OCR Sell"), fg_color="#2980b9").pack(side="right", padx=(4, 0))
        ctk.CTkButton(f_ocr_sell, text=self.strings["btn_test"], width=50, command=lambda: self.test_click_position("OCR Sell"), fg_color="#7f8c8d").pack(side="right")

        # Area Prezzo (OCR Box)
        f_ocr_box = ctk.CTkFrame(self.tab_ocr, fg_color="transparent")
        f_ocr_box.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(f_ocr_box, text=f"{self.strings['label_price_box']}:", width=110, anchor="w").pack(side="left")
        ctk.CTkLabel(f_ocr_box, text="X1:").pack(side="left", padx=(2, 1))
        self.entry_box_x1 = ctk.CTkEntry(f_ocr_box, width=42)
        self.entry_box_x1.insert(0, str(self.config["ocr_price_box"]["x1"]))
        self.entry_box_x1.pack(side="left")
        ctk.CTkLabel(f_ocr_box, text="Y1:").pack(side="left", padx=(2, 1))
        self.entry_box_y1 = ctk.CTkEntry(f_ocr_box, width=42)
        self.entry_box_y1.insert(0, str(self.config["ocr_price_box"]["y1"]))
        self.entry_box_y1.pack(side="left")
        ctk.CTkLabel(f_ocr_box, text="X2:").pack(side="left", padx=(2, 1))
        self.entry_box_x2 = ctk.CTkEntry(f_ocr_box, width=42)
        self.entry_box_x2.insert(0, str(self.config["ocr_price_box"]["x2"]))
        self.entry_box_x2.pack(side="left")
        ctk.CTkLabel(f_ocr_box, text="Y2:").pack(side="left", padx=(2, 1))
        self.entry_box_y2 = ctk.CTkEntry(f_ocr_box, width=42)
        self.entry_box_y2.insert(0, str(self.config["ocr_price_box"]["y2"]))
        self.entry_box_y2.pack(side="left")

        ctk.CTkButton(f_ocr_box, text=self.strings["btn_capture_area"], width=80, command=self.start_area_capture, fg_color="#2980b9").pack(side="right", padx=(4, 0))
        ctk.CTkButton(f_ocr_box, text=self.strings["btn_test_ocr"], width=75, command=self.test_ocr_recognition, fg_color="#16a085").pack(side="right")

        # Pos Input Field
        f_ocr_inp = ctk.CTkFrame(self.tab_ocr, fg_color="transparent")
        f_ocr_inp.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(f_ocr_inp, text=f"{self.strings['label_price_input']}:", width=110, anchor="w").pack(side="left")
        ctk.CTkLabel(f_ocr_inp, text="X:").pack(side="left", padx=(4, 1))
        self.entry_ocr_input_x = ctk.CTkEntry(f_ocr_inp, width=55)
        self.entry_ocr_input_x.insert(0, str(self.config["ocr_price_input"]["x"]))
        self.entry_ocr_input_x.pack(side="left")
        ctk.CTkLabel(f_ocr_inp, text="Y:").pack(side="left", padx=(4, 1))
        self.entry_ocr_input_y = ctk.CTkEntry(f_ocr_inp, width=55)
        self.entry_ocr_input_y.insert(0, str(self.config["ocr_price_input"]["y"]))
        self.entry_ocr_input_y.pack(side="left")
        ctk.CTkButton(f_ocr_inp, text=self.strings["btn_capture"], width=60, command=lambda: self.start_single_capture("OCR Input"), fg_color="#2980b9").pack(side="right", padx=(4, 0))
        ctk.CTkButton(f_ocr_inp, text=self.strings["btn_test"], width=50, command=lambda: self.test_click_position("OCR Input"), fg_color="#7f8c8d").pack(side="right")

        # Pos Create Order Button
        f_ocr_crt = ctk.CTkFrame(self.tab_ocr, fg_color="transparent")
        f_ocr_crt.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(f_ocr_crt, text=f"{self.strings['label_create_order']}:", width=110, anchor="w").pack(side="left")
        ctk.CTkLabel(f_ocr_crt, text="X:").pack(side="left", padx=(4, 1))
        self.entry_ocr_create_x = ctk.CTkEntry(f_ocr_crt, width=55)
        self.entry_ocr_create_x.insert(0, str(self.config["ocr_create_order"]["x"]))
        self.entry_ocr_create_x.pack(side="left")
        ctk.CTkLabel(f_ocr_crt, text="Y:").pack(side="left", padx=(4, 1))
        self.entry_ocr_create_y = ctk.CTkEntry(f_ocr_crt, width=55)
        self.entry_ocr_create_y.insert(0, str(self.config["ocr_create_order"]["y"]))
        self.entry_ocr_create_y.pack(side="left")
        ctk.CTkButton(f_ocr_crt, text=self.strings["btn_capture"], width=60, command=lambda: self.start_single_capture("OCR Create"), fg_color="#2980b9").pack(side="right", padx=(4, 0))
        ctk.CTkButton(f_ocr_crt, text=self.strings["btn_test"], width=50, command=lambda: self.test_click_position("OCR Create"), fg_color="#7f8c8d").pack(side="right")

        # Pricing & Discount Section Card
        card_pricing = ctk.CTkFrame(self.tab_ocr, fg_color="#21252d", corner_radius=6)
        card_pricing.pack(fill="x", pady=(6, 4), padx=10)

        f_disc = ctk.CTkFrame(card_pricing, fg_color="transparent")
        f_disc.pack(fill="x", padx=8, pady=(6, 2))
        ctk.CTkLabel(f_disc, text=self.strings["label_discount_percent"], font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.entry_discount = ctk.CTkEntry(f_disc, width=60)
        self.entry_discount.insert(0, f"{self.config.get('discount_percent', 1.0):.1f}")
        self.entry_discount.pack(side="right")

        # Discount Slider
        self.slider_discount = ctk.CTkSlider(
            card_pricing,
            from_=0.5,
            to=20.0,
            number_of_steps=195,
            command=self.on_slider_discount,
        )
        self.slider_discount.set(self.config.get("discount_percent", 1.0))
        self.slider_discount.pack(fill="x", padx=8, pady=(2, 4))

        # Quick Preset Buttons (Pure % Discounts)
        f_presets = ctk.CTkFrame(card_pricing, fg_color="transparent")
        f_presets.pack(fill="x", padx=8, pady=(2, 4))
        for p_val in [1.0, 2.0, 5.0, 10.0]:
            ctk.CTkButton(
                f_presets,
                text=f"{p_val:.0f}%",
                width=50,
                height=24,
                fg_color="#34495e",
                command=lambda v=p_val: self.apply_preset_discount(v),
            ).pack(side="left", padx=3)

        # Floor Price
        f_floor = ctk.CTkFrame(card_pricing, fg_color="transparent")
        f_floor.pack(fill="x", padx=8, pady=(2, 6))
        ctk.CTkLabel(f_floor, text=self.strings["label_floor_price"]).pack(side="left")
        self.entry_floor_price = ctk.CTkEntry(f_floor, width=90)
        self.entry_floor_price.insert(0, str(self.config.get("floor_price", 0)))
        self.entry_floor_price.pack(side="right")

        # Delay OCR Card
        card_timing_ocr = ctk.CTkFrame(self.tab_ocr, fg_color="#21252d", corner_radius=6)
        card_timing_ocr.pack(fill="x", padx=10, pady=(4, 4))
        f_docr = ctk.CTkFrame(card_timing_ocr, fg_color="transparent")
        f_docr.pack(fill="x", padx=8, pady=4)
        ctk.CTkLabel(f_docr, text=self.strings["label_delay_ocr"]).pack(side="left")
        self.entry_delay_ocr = ctk.CTkEntry(f_docr, width=70)
        self.entry_delay_ocr.insert(0, str(self.config.get("delay_ocr_ms", 250)))
        self.entry_delay_ocr.pack(side="right")


        # ================= TAB 3: ⚙️ IMPOSTAZIONI GLOBALI =================
        # Hotkey Row
        frame_hotkey = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame_hotkey.pack(fill="x", padx=15, pady=(10, 4))
        ctk.CTkLabel(frame_hotkey, text=self.strings["label_hotkey"], font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.hotkey_menu = ctk.CTkOptionMenu(
            frame_hotkey,
            values=["F10", "F4", "F6", "F8", "F9", "F11", "F12", "PAUSE", "INSERT"],
            command=self.on_change_hotkey,
            width=100,
        )
        self.hotkey_menu.set(self.config.get("toggle_hotkey", "F10"))
        self.hotkey_menu.pack(side="right")

        # Anti-Detection
        lbl_sec_anti = ctk.CTkLabel(
            self.tab_settings,
            text=self.strings["section_antidetect"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_sec_anti.pack(anchor="w", padx=15, pady=(12, 4))

        self.switch_human_var = ctk.BooleanVar(value=self.config.get("human_mouse", True))
        self.switch_human = ctk.CTkSwitch(
            self.tab_settings,
            text=self.strings["switch_human_mouse"],
            variable=self.switch_human_var,
        )
        self.switch_human.pack(anchor="w", padx=15, pady=4)

        self.switch_type_var = ctk.BooleanVar(value=self.config.get("human_typing", True))
        self.switch_type = ctk.CTkSwitch(
            self.tab_settings,
            text=self.strings["switch_human_type"],
            variable=self.switch_type_var,
        )
        self.switch_type.pack(anchor="w", padx=15, pady=4)

        self.switch_jitter_var = ctk.BooleanVar(value=self.config.get("jitter", True))
        self.switch_jitter = ctk.CTkSwitch(
            self.tab_settings,
            text=self.strings["switch_jitter"],
            variable=self.switch_jitter_var,
        )
        self.switch_jitter.pack(anchor="w", padx=15, pady=4)

        # Max Items Limit
        frame_limit = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame_limit.pack(fill="x", padx=15, pady=(8, 4))
        ctk.CTkLabel(frame_limit, text=self.strings["label_max_items"]).pack(side="left")
        self.entry_max_items = ctk.CTkEntry(frame_limit, width=80)
        self.entry_max_items.insert(0, str(self.config.get("max_items", 0)))
        self.entry_max_items.pack(side="right")

        # Tesseract Config
        lbl_sec_tess = ctk.CTkLabel(
            self.tab_settings,
            text=self.strings["label_tesseract"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_sec_tess.pack(anchor="w", padx=15, pady=(12, 4))

        frame_tess = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame_tess.pack(fill="x", padx=15, pady=2)
        self.entry_tesseract = ctk.CTkEntry(frame_tess)
        self.entry_tesseract.insert(0, self.config.get("tesseract_path", ""))
        self.entry_tesseract.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(frame_tess, text=self.strings["btn_browse_tesseract"], width=80, command=self.browse_tesseract).pack(side="left", padx=(0, 4))
        ctk.CTkButton(frame_tess, text=self.strings["btn_detect_tesseract"], width=95, command=self.auto_detect_tesseract, fg_color="#16a085").pack(side="left")

        # Save Button in Settings
        ctk.CTkButton(
            self.tab_settings,
            text=self.strings["btn_save_settings"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.save_config,
            height=36,
        ).pack(fill="x", padx=15, pady=(16, 8))

        # ================= DOCKED BOTTOM LOG (ALWAYS VISIBLE) =================
        frame_log = ctk.CTkFrame(self.root, fg_color="transparent")
        frame_log.pack(fill="x", padx=15, pady=(0, 10))

        lbl_sec_log = ctk.CTkLabel(
            frame_log,
            text=self.strings["section_log"],
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        lbl_sec_log.pack(anchor="w", pady=(0, 2))

        self.txt_log = ctk.CTkTextbox(frame_log, height=135, font=("Consolas", 10), wrap="word")
        self.txt_log.pack(fill="x", expand=False)

        # Set initial tab according to config
        init_mode = self.config.get("mode", "3point")
        try:
            if init_mode == "ocr":
                self.tabview.set(self.strings["tab_mode_ocr"])
            else:
                self.tabview.set(self.strings["tab_mode_fast"])
        except Exception:
            pass

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    MAX_LOG_LINES = 400  # Prevent Tkinter text widget buffer inflation & UI freezes

    def log(self, message: str, category: str = "Log"):
        t_str = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{t_str}] [{category}] {message}\n"

        def _append_log():
            if not hasattr(self, "txt_log") or not self.txt_log.winfo_exists():
                return
            try:
                self.txt_log.insert("end", entry)
                text_widget = getattr(self.txt_log, "_textbox", self.txt_log)
                line_count = int(text_widget.index("end-1c").split(".")[0])
                if line_count > self.MAX_LOG_LINES:
                    # Prune excess lines from top in bulk to keep layout lightning fast
                    excess = line_count - self.MAX_LOG_LINES + 50
                    text_widget.delete("1.0", f"{excess}.0")
                self.txt_log.see("end")
            except Exception:
                pass

        if threading.current_thread() is threading.main_thread():
            _append_log()
        else:
            try:
                self.root.after(0, _append_log)
            except Exception:
                pass

    # --- TAB & MODE SWITCHING ---
    def on_tab_changed(self):
        selected = self.tabview.get()
        if selected == self.strings["tab_mode_fast"]:
            self.config["mode"] = "3point"
            self.log(self.strings["mode_switched_fast"], category="Mode")
            self.save_config()
        elif selected == self.strings["tab_mode_ocr"]:
            self.config["mode"] = "ocr"
            self.log(self.strings["mode_switched_ocr"], category="Mode")
            self.save_config()

    def on_change_mode(self, chosen_value: str):
        if "3-Point" in chosen_value or "Fast" in chosen_value or "Veloce" in chosen_value or "-1" in chosen_value:
            self.config["mode"] = "3point"
            try:
                self.tabview.set(self.strings["tab_mode_fast"])
            except Exception:
                pass
        else:
            self.config["mode"] = "ocr"
            try:
                self.tabview.set(self.strings["tab_mode_ocr"])
            except Exception:
                pass
        self.save_config()

    def on_slider_discount(self, val: float):
        if hasattr(self, "entry_discount"):
            self.entry_discount.delete(0, "end")
            self.entry_discount.insert(0, f"{val:.1f}")
        self.config["strategy"] = "percentage"
        self.config["discount_percent"] = round(val, 1)

    def apply_preset_discount(self, val):
        if val == "undercut_1":
            self.config["strategy"] = "undercut_1"
            if hasattr(self, "entry_discount"):
                self.entry_discount.delete(0, "end")
                self.entry_discount.insert(0, "-1 Silver")
            self.log("Strategia: Sconto 1 Silver (Undercut-1)", category="Pricing")
        else:
            self.config["strategy"] = "percentage"
            self.config["discount_percent"] = float(val)
            if hasattr(self, "slider_discount"):
                self.slider_discount.set(float(val))
            if hasattr(self, "entry_discount"):
                self.entry_discount.delete(0, "end")
                self.entry_discount.insert(0, f"{float(val):.1f}")
            self.log(f"Sconto percentuale impostato su: {float(val):.1f}%", category="Pricing")
        self.save_config()

    # --- HOTKEY & SOUND FEEDBACK ---
    def handle_hotkey_press(self):
        """Called when toggle hotkey is triggered. Debounced and dispatched to Tkinter main thread."""
        now = time.time()
        if now - self._last_hotkey_trigger < 0.4:
            return
        self._last_hotkey_trigger = now

        # Asynchronous non-blocking audio feedback
        if not self.is_running:
            async_beep(1200, 80)
        else:
            async_beep(600, 100)

        self.root.after(0, self.toggle_clicking)

    def bind_global_hotkey(self, key_name: str):
        # 1. Hardware/Kernel polling (Primary: lock-free GetAsyncKeyState, <0.001% CPU, 0ms input lag)
        if hasattr(self, "hotkey_poller") and self.hotkey_poller is not None:
            self.hotkey_poller.set_key(key_name)
        else:
            self.hotkey_poller = WindowsHotkeyPoller(self.handle_hotkey_press, default_key=key_name)

        # 2. Secondary layer: only on non-Windows platforms (avoids redundant WH_KEYBOARD_LL hook on Windows)
        if sys.platform != "win32":
            try:
                if self.registered_hotkey:
                    keyboard.remove_hotkey(self.registered_hotkey)
            except Exception:
                pass
            try:
                self.registered_hotkey = keyboard.add_hotkey(key_name, self.handle_hotkey_press)
            except Exception:
                self.registered_hotkey = None

        # 3. Tertiary layer: Tkinter local window binding (clean previous unbind)
        if hasattr(self, "_prev_bound_key") and self._prev_bound_key:
            try:
                self.root.unbind_all(f"<{self._prev_bound_key}>")
            except Exception:
                pass
        try:
            self.root.bind_all(f"<{key_name}>", lambda e: self.handle_hotkey_press())
            self._prev_bound_key = key_name
        except Exception:
            pass

        self.update_toggle_button_text()
        self.log(f"Hotkey {key_name} attivo (Kernel Polling)", category="Hotkey")

    def update_toggle_button_text(self):
        hk = self.config.get("toggle_hotkey", "F10")
        if self.is_running:
            self.btn_toggle.configure(
                text=f"{self.strings['btn_stop']} [{hk}]",
                fg_color="#e74c3c",
                hover_color="#c0392b",
            )
        else:
            self.btn_toggle.configure(
                text=f"{self.strings['btn_start']} [{hk}]",
                fg_color="#2ecc71",
                hover_color="#27ae60",
            )

    def on_change_hotkey(self, chosen_key: str):
        self.bind_global_hotkey(chosen_key)
        self.config["toggle_hotkey"] = chosen_key
        self.save_config()

    def on_change_language(self, chosen: str):
        new_lang = "it" if "Italiano" in chosen else "en"
        if new_lang != self.lang:
            self.lang = new_lang
            self.strings = STRINGS[self.lang]
            self.save_config()
            messagebox.showinfo(
                "Language Changed",
                "Lingua aggiornata! Riavvia l'applicazione per visualizzare i testi aggiornati.\nLanguage updated! Restart the app to reflect changes.",
            )

    def browse_tesseract(self):
        filename = filedialog.askopenfilename(
            title="Select tesseract.exe",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")],
        )
        if filename:
            self.entry_tesseract.delete(0, "end")
            self.entry_tesseract.insert(0, filename)
            self.config["tesseract_path"] = filename
            pytesseract.pytesseract.tesseract_cmd = filename
            self.log(self.strings["tesseract_found"].format(filename), category="OCR")
            self.save_config()

    def auto_detect_tesseract(self):
        p = detect_tesseract_binary(self.entry_tesseract.get())
        if p:
            self.entry_tesseract.delete(0, "end")
            self.entry_tesseract.insert(0, p)
            self.config["tesseract_path"] = p
            pytesseract.pytesseract.tesseract_cmd = p
            self.log(self.strings["tesseract_found"].format(p), category="OCR")
            self.save_config()
        else:
            self.log(self.strings["tesseract_not_found"], category="OCR")

    # --- SETUP WIZARD & MOUSE CAPTURE ---
    def _stop_mouse_listener(self):
        """Helper to cleanly stop and join any active mouse listener to release WH_MOUSE_LL hook."""
        if self.mouse_listener is not None and self.mouse_listener.is_alive():
            try:
                self.mouse_listener.stop()
                self.mouse_listener.join(timeout=0.25)
            except Exception:
                pass
        self.mouse_listener = None

    def start_setup_wizard(self):
        if self.is_running:
            self.stop_clicking()
        self.wizard_step = 1
        self.single_capture_target = None
        self.btn_wizard.configure(text=f"Wizard: Step 1/3 (Click 'Sell')", fg_color="#e67e22")
        self.log(self.strings["wizard_step_1"], category="Wizard")

        self._stop_mouse_listener()
        self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        self.mouse_listener.start()

    def start_ocr_wizard(self):
        if self.is_running:
            self.stop_clicking()
        self.wizard_step = 11  # Step 11: Sell, 12: Box Top-Left, 13: Box Bottom-Right, 14: Input, 15: Create
        self.single_capture_target = None
        self.btn_wizard_ocr.configure(text="Wizard OCR: 1/4 Click 'Sell'", fg_color="#e67e22")
        self.log("[Wizard OCR] Passo 1/4: Fai click sul tasto 'Sell' dell'oggetto in inventario", category="Wizard")

        self._stop_mouse_listener()
        self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        self.mouse_listener.start()

    def start_single_capture(self, target_name: str):
        if self.is_running:
            self.stop_clicking()
        self.wizard_step = 0
        self.single_capture_target = target_name
        self.log(self.strings["capture_single"].format(target_name), category="Capture")

        self._stop_mouse_listener()
        self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        self.mouse_listener.start()

    def start_area_capture(self):
        if self.is_running:
            self.stop_clicking()
        self.wizard_step = 101  # Top-Left point
        self.area_p1 = None
        self.log("[Cattura Area] Fai click nell'angolo in ALTO A SINISTRA dell'area prezzo...", category="Capture")

        self._stop_mouse_listener()
        self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        self.mouse_listener.start()

    def _on_mouse_click(self, x, y, button, pressed):
        if not pressed or button != mouse.Button.left:
            return

        # Handle Area Capture
        if self.wizard_step == 101:
            self.area_p1 = (int(x), int(y))
            self.wizard_step = 102
            self.root.after(0, lambda: self.log(f"[Cattura Area] Punto 1: ({int(x)}, {int(y)}). Ora fai click in BASSO A DESTRA...", category="Capture"))
            return
        elif self.wizard_step == 102:
            p1 = self.area_p1
            p2 = (int(x), int(y))
            self.wizard_step = 0
            self.root.after(0, lambda: self._apply_area_capture(p1, p2))
            return False

        # Handle Single Point Capture
        if self.single_capture_target:
            target = self.single_capture_target
            self.single_capture_target = None
            self.root.after(0, lambda: self._apply_single_capture(target, int(x), int(y)))
            return False

        # Handle 3-Point Wizard
        if self.wizard_step == 1:
            self.root.after(0, lambda: self._apply_wizard_step_1(int(x), int(y)))
        elif self.wizard_step == 2:
            self.root.after(0, lambda: self._apply_wizard_step_2(int(x), int(y)))
        elif self.wizard_step == 3:
            self.root.after(0, lambda: self._apply_wizard_step_3(int(x), int(y)))
            return False

        # Handle OCR Wizard
        elif self.wizard_step == 11:
            self.root.after(0, lambda: self._apply_ocr_step_1(int(x), int(y)))
        elif self.wizard_step == 12:
            self.area_p1 = (int(x), int(y))
            self.wizard_step = 13
            self.root.after(0, lambda: self.log("[Wizard OCR] Area P1 impostato. Ora click in BASSO A DESTRA dell'area prezzo...", category="Wizard"))
        elif self.wizard_step == 13:
            p1 = self.area_p1
            p2 = (int(x), int(y))
            self.root.after(0, lambda: self._apply_area_capture(p1, p2))
            self.wizard_step = 14
            self.btn_wizard_ocr.configure(text="Wizard OCR: 3/4 Click 'Input Prezzo'", fg_color="#e67e22")
            self.root.after(0, lambda: self.log("[Wizard OCR] Passo 3/4: Fai click sul campo input del prezzo...", category="Wizard"))
        elif self.wizard_step == 14:
            self.root.after(0, lambda: self._apply_ocr_step_input(int(x), int(y)))
        elif self.wizard_step == 15:
            self.root.after(0, lambda: self._apply_ocr_step_create(int(x), int(y)))
            return False

    def _apply_area_capture(self, p1, p2):
        x1, x2 = min(p1[0], p2[0]), max(p1[0], p2[0])
        y1, y2 = min(p1[1], p2[1]), max(p1[1], p2[1])
        self.entry_box_x1.delete(0, "end")
        self.entry_box_x1.insert(0, str(x1))
        self.entry_box_y1.delete(0, "end")
        self.entry_box_y1.insert(0, str(y1))
        self.entry_box_x2.delete(0, "end")
        self.entry_box_x2.insert(0, str(x2))
        self.entry_box_y2.delete(0, "end")
        self.entry_box_y2.insert(0, str(y2))
        self.log(f"[Area Prezzo] Impostata: ({x1}, {y1}) -> ({x2}, {y2})", category="Capture")
        self.save_config()

    def _apply_single_capture(self, target: str, x: int, y: int):
        if target == "Pos A":
            self.entry_pos_a_x.delete(0, "end")
            self.entry_pos_a_x.insert(0, str(x))
            self.entry_pos_a_y.delete(0, "end")
            self.entry_pos_a_y.insert(0, str(y))
        elif target == "Pos B":
            self.entry_pos_b_x.delete(0, "end")
            self.entry_pos_b_x.insert(0, str(x))
            self.entry_pos_b_y.delete(0, "end")
            self.entry_pos_b_y.insert(0, str(y))
        elif target == "Pos C":
            self.entry_pos_c_x.delete(0, "end")
            self.entry_pos_c_x.insert(0, str(x))
            self.entry_pos_c_y.delete(0, "end")
            self.entry_pos_c_y.insert(0, str(y))
        elif target == "OCR Sell":
            self.entry_ocr_sell_x.delete(0, "end")
            self.entry_ocr_sell_x.insert(0, str(x))
            self.entry_ocr_sell_y.delete(0, "end")
            self.entry_ocr_sell_y.insert(0, str(y))
        elif target == "OCR Input":
            self.entry_ocr_input_x.delete(0, "end")
            self.entry_ocr_input_x.insert(0, str(x))
            self.entry_ocr_input_y.delete(0, "end")
            self.entry_ocr_input_y.insert(0, str(y))
        elif target == "OCR Create":
            self.entry_ocr_create_x.delete(0, "end")
            self.entry_ocr_create_x.insert(0, str(x))
            self.entry_ocr_create_y.delete(0, "end")
            self.entry_ocr_create_y.insert(0, str(y))

        self.log(self.strings["capture_done"].format(target, x, y), category="Capture")
        self.save_config()

    def _apply_wizard_step_1(self, x: int, y: int):
        self.entry_pos_a_x.delete(0, "end")
        self.entry_pos_a_x.insert(0, str(x))
        self.entry_pos_a_y.delete(0, "end")
        self.entry_pos_a_y.insert(0, str(y))
        self.log(self.strings["capture_done"].format("Position A", x, y), category="Capture")
        self.wizard_step = 2
        self.btn_wizard.configure(text="Wizard: Step 2/3 (Click '[-]')", fg_color="#e67e22")
        self.log(self.strings["wizard_step_2"], category="Wizard")

    def _apply_wizard_step_2(self, x: int, y: int):
        self.entry_pos_b_x.delete(0, "end")
        self.entry_pos_b_x.insert(0, str(x))
        self.entry_pos_b_y.delete(0, "end")
        self.entry_pos_b_y.insert(0, str(y))
        self.log(self.strings["capture_done"].format("Position B", x, y), category="Capture")
        self.wizard_step = 3
        self.btn_wizard.configure(text="Wizard: Step 3/3 (Click 'Create')", fg_color="#e67e22")
        self.log(self.strings["wizard_step_3"], category="Wizard")

    def _apply_wizard_step_3(self, x: int, y: int):
        self.entry_pos_c_x.delete(0, "end")
        self.entry_pos_c_x.insert(0, str(x))
        self.entry_pos_c_y.delete(0, "end")
        self.entry_pos_c_y.insert(0, str(y))
        self.log(self.strings["capture_done"].format("Position C", x, y), category="Capture")
        self.wizard_step = 0
        self.btn_wizard.configure(text=self.strings["btn_wizard"], fg_color="#8e44ad")
        self.log(self.strings["wizard_complete"], category="Wizard")
        self.save_config()

    def _apply_ocr_step_1(self, x: int, y: int):
        self.entry_ocr_sell_x.delete(0, "end")
        self.entry_ocr_sell_x.insert(0, str(x))
        self.entry_ocr_sell_y.delete(0, "end")
        self.entry_ocr_sell_y.insert(0, str(y))
        self.wizard_step = 12
        self.btn_wizard_ocr.configure(text="Wizard OCR: 2/4 Click Area Prezzo", fg_color="#e67e22")
        self.log("[Wizard OCR] Passo 2/4: Fai click in ALTO A SINISTRA dell'area prezzo...", category="Wizard")

    def _apply_ocr_step_input(self, x: int, y: int):
        self.entry_ocr_input_x.delete(0, "end")
        self.entry_ocr_input_x.insert(0, str(x))
        self.entry_ocr_input_y.delete(0, "end")
        self.entry_ocr_input_y.insert(0, str(y))
        self.wizard_step = 15
        self.btn_wizard_ocr.configure(text="Wizard OCR: 4/4 Click 'Create'", fg_color="#e67e22")
        self.log("[Wizard OCR] Passo 4/4: Fai click sul pulsante 'Create' per confermare l'ordine...", category="Wizard")

    def _apply_ocr_step_create(self, x: int, y: int):
        self.entry_ocr_create_x.delete(0, "end")
        self.entry_ocr_create_x.insert(0, str(x))
        self.entry_ocr_create_y.delete(0, "end")
        self.entry_ocr_create_y.insert(0, str(y))
        self.wizard_step = 0
        self.btn_wizard_ocr.configure(text=self.strings["btn_wizard_ocr"], fg_color="#8e44ad")
        self.log("✅ [Wizard OCR] Calibrazione completata con successo! Pronto per l'avvio.", category="Wizard")
        self.save_config()

    def test_click_position(self, target: str):
        try:
            if target == "Pos A":
                x = int(self.entry_pos_a_x.get())
                y = int(self.entry_pos_a_y.get())
            elif target == "Pos B":
                x = int(self.entry_pos_b_x.get())
                y = int(self.entry_pos_b_y.get())
            elif target == "Pos C":
                x = int(self.entry_pos_c_x.get())
                y = int(self.entry_pos_c_y.get())
            elif target == "OCR Sell":
                x = int(self.entry_ocr_sell_x.get())
                y = int(self.entry_ocr_sell_y.get())
            elif target == "OCR Input":
                x = int(self.entry_ocr_input_x.get())
                y = int(self.entry_ocr_input_y.get())
            else:
                x = int(self.entry_ocr_create_x.get())
                y = int(self.entry_ocr_create_y.get())

            self.log(f"Testing {target} at ({x}, {y}). Moving mouse...", category="Test")
            human_move_to(x, y, enabled=False)
            pyautogui.click()
            self.log(f"✅ Click performed at {target} ({x}, {y})", category="Test")
        except Exception as e:
            self.log(f"⚠️ Error testing {target}: {e}", category="Error")

    def test_ocr_recognition(self):
        try:
            x1 = int(self.entry_box_x1.get())
            y1 = int(self.entry_box_y1.get())
            x2 = int(self.entry_box_x2.get())
            y2 = int(self.entry_box_y2.get())
            bbox = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))

            self.log(f"Test OCR su area {bbox}...", category="OCR")
            val = OcrReader.read_number_from_bbox(bbox)
            if val is not None and val > 0:
                raw_disc = self.entry_discount.get().replace("%", "").strip()
                try:
                    disc = float(raw_disc) if raw_disc else 1.0
                except ValueError:
                    disc = 1.0
                strat = self.config.get("strategy", "percentage")
                floor_p = int(self.entry_floor_price.get().strip() or 0)
                target, reason = calculate_target_price(val, disc, floor_p, strat)
                self.log(self.strings["ocr_test_result"].format(val, target, reason), category="OCR")
            else:
                self.log(self.strings["ocr_read_fail"], category="OCR")
        except Exception as e:
            self.log(f"⚠️ Errore test OCR: {e}", category="Error")

    # --- CLICKING WORKER LOOP ---
    def toggle_clicking(self):
        # Cancel wizard or capture if in progress
        if getattr(self, "wizard_step", 0) > 0 or getattr(self, "single_capture_target", None):
            self.wizard_step = 0
            self.single_capture_target = None
            self._stop_mouse_listener()
            self.btn_wizard.configure(text=self.strings["btn_wizard"], fg_color="#8e44ad")
            self.btn_wizard_ocr.configure(text=self.strings["btn_wizard_ocr"], fg_color="#8e44ad")
            self.log("Wizard / Cattura annullata.", category="Wizard")
            return

        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        # Guard against overlapping zombie worker threads
        if self.worker_thread is not None and self.worker_thread.is_alive():
            self.worker_stop_event.set()
            self.is_running = False
            self.worker_thread.join(timeout=0.5)
            if self.worker_thread.is_alive():
                self.log("⚠️ Attesa completamento ciclo precedente...", category="Warning")
                return

        mode = self.config.get("mode", "3point")
        if mode == "3point":
            try:
                _ = (int(self.entry_pos_a_x.get()), int(self.entry_pos_a_y.get()))
                _ = (int(self.entry_pos_b_x.get()), int(self.entry_pos_b_y.get()))
                _ = (int(self.entry_pos_c_x.get()), int(self.entry_pos_c_y.get()))
            except ValueError:
                messagebox.showerror("Error", "Please set valid integer coordinates for Pos A, B, and C.")
                return
        else:
            try:
                _ = (int(self.entry_ocr_sell_x.get()), int(self.entry_ocr_sell_y.get()))
                _ = (int(self.entry_box_x1.get()), int(self.entry_box_y1.get()))
                _ = (int(self.entry_ocr_input_x.get()), int(self.entry_ocr_input_y.get()))
                _ = (int(self.entry_ocr_create_x.get()), int(self.entry_ocr_create_y.get()))
            except ValueError:
                messagebox.showerror("Error", "Please set valid coordinates for Smart OCR mode.")
                return

        self._stop_mouse_listener()
        self.worker_stop_event.clear()
        self.is_running = True
        self.update_toggle_button_text()
        self.log(f"{self.strings['loop_started']} [Mode: {mode.upper()}]", category="Control")

        self.worker_thread = threading.Thread(
            target=self._clicking_worker_loop,
            daemon=True,
        )
        self.worker_thread.start()

    def stop_clicking(self):
        self.is_running = False
        self.worker_stop_event.set()
        self.update_toggle_button_text()
        self.log(self.strings["loop_stopped"].format(self.stats.total_orders), category="Control")

    def _clicking_worker_loop(self):
        mode = self.config.get("mode", "3point")
        humanize = self.switch_human_var.get()
        jitter = self.switch_jitter_var.get()
        human_type_enabled = self.switch_type_var.get() if hasattr(self, "switch_type_var") else True
        max_items = max(0, int(self.entry_max_items.get()))

        delay_ab = max(50, int(self.entry_delay_ab.get())) / 1000.0
        delay_bc = max(50, int(self.entry_delay_bc.get())) / 1000.0
        delay_ca = max(100, int(self.entry_delay_ca.get())) / 1000.0
        delay_ocr = max(50, int(self.entry_delay_ocr.get())) / 1000.0 if hasattr(self, "entry_delay_ocr") else 0.25

        if mode == "3point":
            pos_a = (int(self.entry_pos_a_x.get()), int(self.entry_pos_a_y.get()))
            pos_b = (int(self.entry_pos_b_x.get()), int(self.entry_pos_b_y.get()))
            pos_c = (int(self.entry_pos_c_x.get()), int(self.entry_pos_c_y.get()))
        else:
            pos_sell = (int(self.entry_ocr_sell_x.get()), int(self.entry_ocr_sell_y.get()))
            bx1, by1 = int(self.entry_box_x1.get()), int(self.entry_box_y1.get())
            bx2, by2 = int(self.entry_box_x2.get()), int(self.entry_box_y2.get())
            price_box = (min(bx1, bx2), min(by1, by2), max(bx1, bx2), max(by1, by2))
            pos_input = (int(self.entry_ocr_input_x.get()), int(self.entry_ocr_input_y.get()))
            pos_create = (int(self.entry_ocr_create_x.get()), int(self.entry_ocr_create_y.get()))
            try:
                raw_disc = self.entry_discount.get().replace("%", "").strip()
                discount_percent = float(raw_disc) if raw_disc else 1.0
            except ValueError:
                discount_percent = 1.0
            try:
                floor_price = int(self.entry_floor_price.get().strip() or 0)
            except ValueError:
                floor_price = 0
            strategy_type = self.config.get("strategy", "percentage")

        cycle_count = 0
        while self.is_running and not self.worker_stop_event.is_set():
            try:
                if mode == "3point":
                    # 1. Click Position A (Top Item 'Sell' Button)
                    human_move_to(pos_a[0], pos_a[1], enabled=humanize)
                    if not self.is_running or self.worker_stop_event.is_set():
                        break
                    pyautogui.click()

                    # Responsive interruptible delay
                    d_ab = get_gaussian_delay(delay_ab * 0.85, delay_ab * 1.15) if jitter else delay_ab
                    if self.worker_stop_event.wait(d_ab):
                        break

                    # 2. Click Position B ([-] Undercut 1 Silver Button)
                    human_move_to(pos_b[0], pos_b[1], enabled=humanize)
                    if not self.is_running or self.worker_stop_event.is_set():
                        break
                    pyautogui.click()

                    d_bc = get_gaussian_delay(delay_bc * 0.85, delay_bc * 1.15) if jitter else delay_bc
                    if self.worker_stop_event.wait(d_bc):
                        break

                    # 3. Click Position C ('Create' Sell Order Button)
                    human_move_to(pos_c[0], pos_c[1], enabled=humanize)
                    if not self.is_running or self.worker_stop_event.is_set():
                        break
                    pyautogui.click()

                    cycle_count += 1
                    self.stats.record_sale(price=0, strategy="3point_clicker")
                    self.root.after(0, lambda c=cycle_count: self.log(self.strings["cycle_sold"].format(c), category="Cycle"))

                else:
                    # SMART OCR MODE
                    # 1. Click Sell on top item
                    human_move_to(pos_sell[0], pos_sell[1], enabled=humanize)
                    if not self.is_running or self.worker_stop_event.is_set():
                        break
                    pyautogui.click()

                    d_ab = get_gaussian_delay(delay_ab * 0.85, delay_ab * 1.15) if jitter else delay_ab
                    if self.worker_stop_event.wait(d_ab):
                        break

                    # 2. OCR Read Price
                    if self.worker_stop_event.wait(delay_ocr):
                        break
                    detected = None
                    for attempt in range(3):
                        if not self.is_running or self.worker_stop_event.is_set():
                            break
                        detected = OcrReader.read_number_from_bbox(price_box)
                        if detected is not None and detected > 0:
                            break
                        if self.worker_stop_event.wait(0.04):
                            break

                    if not self.is_running or self.worker_stop_event.is_set():
                        break

                    if detected is None or detected <= 0:
                        self.root.after(0, lambda: self.log(self.strings["ocr_read_fail"], category="OCR"))
                        if self.worker_stop_event.wait(0.5):
                            break
                        continue

                    # 3. Calculate target price with % discount & floor price
                    target_price, reason = calculate_target_price(
                        detected_price=detected,
                        discount_percent=discount_percent,
                        floor_price=floor_price,
                        strategy=strategy_type,
                    )

                    if reason == "below_floor_safety_stop":
                        self.root.after(0, lambda dp=detected, fp=floor_price: self.log(
                            self.strings["ocr_below_floor"].format(dp, fp), category="Security"
                        ))
                        if self.worker_stop_event.wait(0.5):
                            break
                        continue

                    # 4. Click Price Input Field -> Clear -> Type Target Price
                    human_move_to(pos_input[0], pos_input[1], enabled=humanize)
                    if not self.is_running or self.worker_stop_event.is_set():
                        break
                    pyautogui.click()
                    if self.worker_stop_event.wait(0.04):
                        break

                    pyautogui.hotkey("ctrl", "a")
                    pyautogui.press("backspace")
                    if self.worker_stop_event.wait(0.02):
                        break

                    human_type(str(target_price), enabled=human_type_enabled)
                    if not self.is_running or self.worker_stop_event.is_set():
                        break

                    d_bc = get_gaussian_delay(delay_bc * 0.85, delay_bc * 1.15) if jitter else delay_bc
                    if self.worker_stop_event.wait(d_bc):
                        break

                    # 5. Click Create Order Button
                    human_move_to(pos_create[0], pos_create[1], enabled=humanize)
                    if not self.is_running or self.worker_stop_event.is_set():
                        break
                    pyautogui.click()

                    cycle_count += 1
                    self.stats.record_sale(price=target_price, strategy="smart_ocr", reason=reason)
                    self.root.after(0, lambda c=cycle_count, dp=detected, tp=target_price, r=reason: self.log(
                        self.strings["ocr_sold"].format(c, dp, tp, r), category="Cycle"
                    ))

                if max_items > 0 and cycle_count >= max_items:
                    self.root.after(0, self.stop_clicking)
                    break

                # Inter-cycle delay (interruptible)
                d_ca = get_gaussian_delay(delay_ca * 0.85, delay_ca * 1.15) if jitter else delay_ca
                if self.worker_stop_event.wait(d_ca):
                    break

            except pyautogui.FailSafeException:
                self.root.after(0, self.stop_clicking)
                self.root.after(0, lambda: self.log("⚠️ PyAutoGUI FailSafe triggered!", category="Failsafe"))
                break
            except Exception as e:
                self.root.after(0, lambda err=e: self.log(f"⚠️ Worker error: {err}", category="Error"))
                if self.worker_stop_event.wait(0.5):
                    break

    def on_closing(self):
        self.is_running = False
        if hasattr(self, "worker_stop_event"):
            self.worker_stop_event.set()

        # Join worker thread before destroying UI to prevent calls on dead widgets
        if self.worker_thread is not None and self.worker_thread.is_alive():
            try:
                self.worker_thread.join(timeout=0.8)
            except Exception:
                pass

        if hasattr(self, "hotkey_poller") and self.hotkey_poller:
            self.hotkey_poller.stop()

        self._stop_mouse_listener()

        if sys.platform != "win32":
            try:
                if self.registered_hotkey:
                    keyboard.remove_hotkey(self.registered_hotkey)
            except Exception:
                pass

        if sys.platform == "win32":
            try:
                ctypes.windll.winmm.timeEndPeriod(1)
            except Exception:
                pass

        self.root.destroy()


# Compatibility alias
AutoSellerApp = AlbionMarketAutoClickerApp


def main():
    root = ctk.CTk() if USE_CUSTOMTKINTER else tk.Tk()
    app = AlbionMarketAutoClickerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
