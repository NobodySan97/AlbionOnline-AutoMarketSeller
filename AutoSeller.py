"""
Albion Online — Market Seller Auto Clicker (3-Point Loop)
Replicates the high-speed 3-Point Market Clicker from the video:
  Position A (Sell Button) -> Position B ([-] Price Undercut) -> Position C (Create Order)
"""

import csv
import ctypes
import datetime
import json
import math
import os
import random
import re
import shutil
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox

import cv2
import keyboard
import numpy as np
import pyautogui
from pynput import mouse

try:
    import customtkinter as ctk
    USE_CUSTOMTKINTER = True
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
except ImportError:
    USE_CUSTOMTKINTER = False

# --- WINDOWS DPI AWARENESS ---
if sys.platform == "win32":
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# MULTILINGUAL STRINGS
STRINGS = {
    "en": {
        "app_title": "Market Seller — Auto Clicker",
        "header_title": "MARKET SELLER AUTO CLICKER",
        "tab_positions": "Positions & Controls",
        "tab_settings": "Settings",
        "section_positions": "Click Positions",
        "btn_wizard": "Setup Wizard",
        "label_pos_a": "Pos A",
        "label_pos_b": "Pos B",
        "label_pos_c": "Pos C",
        "btn_test": "Test",
        "btn_capture": "Capture",
        "section_controls": "Controls",
        "label_hotkey": "Toggle Hotkey:",
        "section_log": "Activity Log",
        "btn_start": "▶ START",
        "btn_stop": "■ STOP",
        "section_timing": "Timing & Delays (Milliseconds)",
        "label_delay_ab": "Delay after Pos A (Open Item):",
        "label_delay_bc": "Delay after Pos B (Undercut [-]):",
        "label_delay_ca": "Delay after Pos C (Create Order):",
        "section_antidetect": "Anti-Detection & Humanization",
        "switch_human_mouse": "Humanized Bézier Mouse Movement",
        "switch_jitter": "Random Timing Jitter (±15%)",
        "label_max_items": "Max Items to Sell (0 = Infinite):",
        "label_language": "Language:",
        "btn_save_settings": "💾 Save Settings",
        "wizard_step_1": "[Wizard] Step 1/3: Position A (first click) -> Click 'Sell' on the top item",
        "wizard_step_2": "[Wizard] Step 2/3: Position B (second click) -> Click '[-]' price decrement button",
        "wizard_step_3": "[Wizard] Step 3/3: Position C (third click) -> Click 'Create' order button",
        "wizard_complete": "[Wizard] All 3 positions set! You're ready to start.",
        "capture_single": "[Capture] Click anywhere to set {}...",
        "capture_done": "[Capture] {} set to ({}, {})",
        "loop_started": "[Control] Clicking started - A -> B -> C loop",
        "loop_stopped": "[Control] Clicking stopped. Total items sold: {}",
        "cycle_sold": "[Cycle #{}] Sold item at Pos A -> B -> C",
        "status_ready": "Ready",
        "status_running": "Running",
        "status_wizard": "Wizard Active...",
        "region_map": {
            "sell_button": "Sell Tab Button",
            "order_button": "Sell Order Button",
            "price_input": "Price Input Field",
            "submit_button": "Create Order Button",
            "price_value": "Current Price Area",
            "average_price": "Average Price Area",
        },
    },
    "it": {
        "app_title": "Market Seller — Auto Clicker",
        "header_title": "MARKET SELLER AUTO CLICKER",
        "tab_positions": "Posizioni & Controlli",
        "tab_settings": "Impostazioni",
        "section_positions": "Posizioni di Click",
        "btn_wizard": "Setup Wizard (3 Click)",
        "label_pos_a": "Pos A",
        "label_pos_b": "Pos B",
        "label_pos_c": "Pos C",
        "btn_test": "Test",
        "btn_capture": "Cattura",
        "section_controls": "Controlli",
        "label_hotkey": "Tasto Rapido Avvio/Stop:",
        "section_log": "Log Attività",
        "btn_start": "▶ AVVIA",
        "btn_stop": "■ FERMA",
        "section_timing": "Tempi & Ritardi (Millisecondi)",
        "label_delay_ab": "Ritardo dopo Pos A (Apertura Oggetto):",
        "label_delay_bc": "Ritardo dopo Pos B (Sconto [-]):",
        "label_delay_ca": "Ritardo dopo Pos C (Crea Ordine):",
        "section_antidetect": "Anti-Rilevamento & Umanizzazione",
        "switch_human_mouse": "Movimento Mouse Naturale (Bézier)",
        "switch_jitter": "Variazione Casuale Ritardi (±15%)",
        "label_max_items": "Max Oggetti da Vendere (0 = Infinito):",
        "label_language": "Lingua:",
        "btn_save_settings": "💾 Salva Impostazioni",
        "wizard_step_1": "[Wizard] Passo 1/3: Posizione A (primo click) -> Fai click su 'Sell' del primo oggetto",
        "wizard_step_2": "[Wizard] Passo 2/3: Posizione B (secondo click) -> Fai click sul tasto '[-]' del prezzo",
        "wizard_step_3": "[Wizard] Passo 3/3: Posizione C (terzo click) -> Fai click sul tasto 'Create' ordine",
        "wizard_complete": "[Wizard] Tutte e 3 le posizioni impostate! Pronto per iniziare.",
        "capture_single": "[Cattura] Fai click ovunque sullo schermo per impostare {}...",
        "capture_done": "[Cattura] {} impostato su ({}, {})",
        "loop_started": "[Controllo] Avviato ciclo di vendita - Loop A -> B -> C",
        "loop_stopped": "[Controllo] Ciclo fermato. Oggetti totali venduti: {}",
        "cycle_sold": "[Ciclo #{}] Venduto oggetto con Pos A -> B -> C",
        "status_ready": "Pronto",
        "status_running": "In Esecuzione",
        "status_wizard": "Wizard Attivo...",
        "region_map": {
            "sell_button": "Sell Tab Button",
            "order_button": "Sell Order Button",
            "price_input": "Price Input Field",
            "submit_button": "Create Order Button",
            "price_value": "Current Price Area",
            "average_price": "Average Price Area",
        },
    },
}


# --- BEZIER & HUMAN INPUT SIMULATION ---
def generate_bezier_curve(
    start: tuple[int, int], end: tuple[int, int], num_points: int = 25, deviation: int = 30
) -> list[tuple[int, int]]:
    """Generates smooth human-like cubic Bézier curve trajectory."""
    x0, y0 = start
    x3, y3 = end

    dx = x3 - x0
    dy = y3 - y0
    dist = math.hypot(dx, dy)

    if dist < 5:
        return [start, end]

    nx = -dy / dist
    ny = dx / dist

    offset1 = random.uniform(-deviation, deviation)
    offset2 = random.uniform(-deviation, deviation)

    x1 = int(x0 + dx * 0.33 + nx * offset1)
    y1 = int(y0 + dy * 0.33 + ny * offset1)
    x2 = int(x0 + dx * 0.66 + nx * offset2)
    y2 = int(y0 + dy * 0.66 + ny * offset2)

    points = []
    for i in range(num_points):
        t_raw = i / max(1, num_points - 1)
        t = 0.5 * (1 - math.cos(math.pi * t_raw))

        bx = (1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t**2 * x2 + t**3 * x3
        by = (1 - t) ** 3 * y0 + 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t**2 * y2 + t**3 * y3
        points.append((int(round(bx)), int(round(by))))
    return points


def get_gaussian_delay(min_val: float, max_val: float) -> float:
    """Returns random delay sampled from bounded Gaussian distribution."""
    mu = (min_val + max_val) / 2.0
    sigma = (max_val - min_val) / 6.0
    val = random.gauss(mu, sigma)
    return max(min_val, min(max_val, val))


def human_move_to(target_x: int, target_y: int, enabled: bool = True):
    """Moves mouse naturally using Bézier curves."""
    if not enabled:
        pyautogui.moveTo(target_x, target_y)
        return

    current_pos = pyautogui.position()
    dist = math.hypot(target_x - current_pos[0], target_y - current_pos[1])
    num_pts = max(10, min(40, int(dist / 20)))
    curve = generate_bezier_curve(current_pos, (target_x, target_y), num_points=num_pts)

    for pt in curve:
        pyautogui.moveTo(pt[0], pt[1])
        time.sleep(random.uniform(0.003, 0.008))


# --- NUMBER PARSER & OCR UTILITIES ---
def parse_albion_number(text: str) -> int | None:
    """Parses raw OCR number string with robust European/American format handling."""
    if not text:
        return None

    text = text.strip()
    text = re.sub(r"[^\w.,]", "", text)

    text = text.replace("O", "0").replace("o", "0")
    text = text.replace("l", "1").replace("I", "1")
    text = text.replace("S", "5").replace("s", "5")
    text = text.replace("B", "8")

    match = re.search(r"([\d.,]+)\s*([KkMmtT])?", text)
    if not match:
        return None

    num_part, suffix = match.groups()
    suffix = suffix.upper() if suffix else None

    num_part = num_part.strip(".,")
    if not num_part:
        return None

    dot_count = num_part.count(".")
    comma_count = num_part.count(",")

    if dot_count > 0 and comma_count > 0:
        last_dot = num_part.rfind(".")
        last_comma = num_part.rfind(",")
        if last_dot > last_comma:
            clean_str = num_part.replace(",", "")
        else:
            clean_str = num_part.replace(".", "").replace(",", ".")
    elif dot_count > 1:
        clean_str = num_part.replace(".", "")
    elif comma_count > 1:
        clean_str = num_part.replace(",", "")
    elif dot_count == 1:
        if suffix:
            clean_str = num_part
        else:
            parts = num_part.split(".")
            if len(parts[1]) == 3:
                clean_str = num_part.replace(".", "")
            else:
                clean_str = num_part
    elif comma_count == 1:
        if suffix:
            clean_str = num_part.replace(",", ".")
        else:
            parts = num_part.split(",")
            if len(parts[1]) == 3:
                clean_str = num_part.replace(",", "")
            else:
                clean_str = num_part.replace(",", ".")
    else:
        clean_str = num_part

    try:
        val = float(clean_str)
        if suffix == "M":
            val *= 1_000_000
        elif suffix in ("K", "T"):
            val *= 1_000
        return max(0, int(round(val)))
    except (ValueError, TypeError):
        return None


def detect_tesseract_binary(custom_config_path: str = "") -> str:
    meipass = getattr(sys, "_MEIPASS", "")
    candidate_paths = [
        os.path.join(meipass, "tesseract", "tesseract.exe") if meipass else "",
        os.path.join(meipass, "tesseract.exe") if meipass else "",
        os.path.join(BASE_DIR, "tesseract", "tesseract.exe"),
        os.path.join(BASE_DIR, "tesseract-portable", "tesseract.exe"),
        os.path.join(BASE_DIR, "tesseract.exe"),
        custom_config_path,
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"%APPDATA%\Tesseract-OCR\tesseract.exe"),
        r"C:\tools\tesseract\tesseract.exe",
        shutil.which("tesseract.exe") or "",
        shutil.which("tesseract") or "",
    ]
    for p in candidate_paths:
        if p and os.path.isfile(p):
            tess_dir = os.path.dirname(p)
            tessdata_path = os.path.join(tess_dir, "tessdata")
            if os.path.isdir(tessdata_path):
                os.environ["TESSDATA_PREFIX"] = tessdata_path
            return p
    return ""


def deep_merge_config(default_cfg: dict, user_cfg: dict) -> dict:
    """Recursively merges user_cfg into default_cfg without dropping keys."""
    merged = default_cfg.copy()
    for k, v in user_cfg.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = deep_merge_config(merged[k], v)
        else:
            merged[k] = v
    return merged


# --- TEMPLATE MATCHER UTILITY (BACKWARD COMPATIBILITY) ---
class TemplateMatcher:
    @staticmethod
    def find_template_in_image(image_bgr: np.ndarray, template_path: str, threshold: float = 0.75):
        if not os.path.isfile(template_path) or image_bgr is None:
            return None, 0.0
        try:
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                return None, 0.0
            h, w = template.shape[:2]
            if image_bgr.shape[0] < h or image_bgr.shape[1] < w:
                return None, 0.0
            res = cv2.matchTemplate(image_bgr, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            if max_val >= threshold:
                return (max_loc[0] + w // 2, max_loc[1] + h // 2), float(max_val)
            return None, float(max_val)
        except Exception:
            return None, 0.0


# --- SESSION STATS ---
class SessionStats:
    def __init__(self):
        self.start_time = time.time()
        self.total_orders = 0
        self.total_silver = 0
        self.records = []
        self.orders = []
        self.lock = threading.Lock()

    def record_sale(
        self, price: int = 0, strategy: str = "normal", reason: str = "ok", diff_percent: float = 0.0, item_name: str = "Item"
    ):
        with self.lock:
            self.total_orders += 1
            self.total_silver += price
            rec = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "item": item_name,
                "price": price,
                "strategy": strategy,
                "reason": reason,
                "diff_percent": round(diff_percent, 2),
            }
            self.records.append(rec)
            self.orders.append(rec)

    def reset(self):
        with self.lock:
            self.total_orders = 0
            self.total_silver = 0
            self.start_time = time.time()
            self.records.clear()
            self.orders.clear()

    @property
    def average_price(self) -> int:
        with self.lock:
            return int(round(self.total_silver / self.total_orders)) if self.total_orders > 0 else 0

    @property
    def elapsed_formatted(self) -> str:
        s = int(time.time() - self.start_time)
        return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"

    def export_csv(self, filepath: str):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "item", "price", "strategy", "reason", "diff_percent"])
            writer.writeheader()
            writer.writerows(self.records)


# --- PRICING CALCULATION (FOR BACKWARD COMPATIBILITY) ---
def calculate_sell_price(
    number1: int | None,
    number2: int | None,
    fallback_ratio: float = 0.90,
    max_diff_percent: float = 30.0,
    strategy: str = "percentage",
    floor_price: int = 0,
) -> tuple[int, str, float]:
    """Intelligent pricing logic supporting Undercut-1, Percentage, and Tiered pricing."""
    if number1 is None and number2 is None:
        return (0, "none", 0.0)

    if number1 is None and number2 is not None:
        raw_price = int(round(number2 * fallback_ratio))
        price = max(1, raw_price, floor_price)
        reason = "floor_protected" if floor_price > raw_price else "fallback_avg"
        return (price, reason, 0.0)

    if number2 is None and number1 is not None:
        if strategy == "undercut_1":
            raw_price = number1 - 1 if number1 > 1 else 1
        else:
            raw_price = int(round(number1 * fallback_ratio))
        price = max(1, raw_price, floor_price)
        reason = "floor_protected" if floor_price > raw_price else "fallback_num1"
        return (price, reason, 0.0)

    diff_percent = abs(number1 - number2) / max(1, number2) * 100.0

    if diff_percent > max_diff_percent and number1 < number2 * (1.0 - max_diff_percent / 100.0):
        raw_price = int(round(number2 * fallback_ratio))
        price = max(1, raw_price, floor_price)
        return (price, "diff_protected", diff_percent)

    if strategy == "undercut_1":
        raw_price = number1 - 1 if number1 > 1 else 1
        reason = "undercut_1"
    elif strategy == "tiered":
        if number1 >= 1_000_000:
            raw_price = number1 - 1
        elif number1 >= 100_000:
            raw_price = int(round(number1 * 0.95))
        else:
            raw_price = int(round(number1 * fallback_ratio))
        reason = "tiered"
    else:  # percentage
        raw_price = int(round(number1 * fallback_ratio))
        reason = "percentage"

    if floor_price > 0 and raw_price < floor_price:
        price = floor_price
        reason = f"{reason}_floor_clamped"
    else:
        price = max(1, raw_price)

    return (price, reason, diff_percent)


# =====================================================================
#                MAIN 3-POINT AUTO CLICKER APPLICATION
# =====================================================================
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
        self.mouse_listener = None
        self.wizard_step = 0
        self.single_capture_target = None
        self.registered_hotkey = None

        # Load Configuration
        self.config = self.load_config()
        self.lang = self.config.get("language", "it")
        self.strings = STRINGS.get(self.lang, STRINGS["it"])

        # Setup User Interface
        self.setup_ui()

        # Register Global Hotkey
        self.bind_global_hotkey(self.config.get("toggle_hotkey", "F10"))

        # Log Welcome
        self.log(self.strings["status_ready"], category="System")

    def load_config(self) -> dict:
        default_cfg = {
            "language": "it",
            "pos_a": {"x": 2119, "y": 571},
            "pos_b": {"x": 1194, "y": 841},
            "pos_c": {"x": 1612, "y": 972},
            "toggle_hotkey": "F10",
            "delay_ab_ms": 300,
            "delay_bc_ms": 200,
            "delay_ca_ms": 400,
            "human_mouse": True,
            "jitter": True,
            "max_items": 0,
            "strategy": "undercut_1",
            "floor_price": 0,
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
            self.config["pos_a"] = {"x": int(self.entry_pos_a_x.get()), "y": int(self.entry_pos_a_y.get())}
            self.config["pos_b"] = {"x": int(self.entry_pos_b_x.get()), "y": int(self.entry_pos_b_y.get())}
            self.config["pos_c"] = {"x": int(self.entry_pos_c_x.get()), "y": int(self.entry_pos_c_y.get())}
            self.config["toggle_hotkey"] = self.hotkey_menu.get()

            self.config["delay_ab_ms"] = int(self.entry_delay_ab.get())
            self.config["delay_bc_ms"] = int(self.entry_delay_bc.get())
            self.config["delay_ca_ms"] = int(self.entry_delay_ca.get())
            self.config["human_mouse"] = self.switch_human_var.get()
            self.config["jitter"] = self.switch_jitter_var.get()
            self.config["max_items"] = int(self.entry_max_items.get())
            self.config["language"] = self.lang

            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            self.log("💾 Config saved successfully.", category="Config")
        except Exception as e:
            self.log(f"⚠️ Error saving config: {e}", category="Error")

    def setup_ui(self):
        self.root.title(self.strings["app_title"])
        self.root.geometry("640x720")
        self.root.minsize(580, 680)

        # Header Frame with Title & Language
        header = ctk.CTkFrame(self.root, fg_color="#1a1c23", corner_radius=0, height=65)
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
            text=self.strings["btn_start"],
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            height=50,
            command=self.toggle_clicking,
        )
        self.btn_toggle.pack(fill="x", padx=15, pady=(12, 8))

        # Main Tabview
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tab_ctrl = self.tabview.add(self.strings["tab_positions"])
        self.tab_settings = self.tabview.add(self.strings["tab_settings"])

        # ================= TAB 1: POSITIONS & CONTROLS =================
        lbl_sec_pos = ctk.CTkLabel(
            self.tab_ctrl,
            text=self.strings["section_positions"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_sec_pos.pack(anchor="w", padx=10, pady=(10, 5))

        # Setup Wizard Button
        self.btn_wizard = ctk.CTkButton(
            self.tab_ctrl,
            text=self.strings["btn_wizard"],
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8e44ad",
            hover_color="#732d91",
            height=34,
            command=self.start_setup_wizard,
        )
        self.btn_wizard.pack(fill="x", padx=10, pady=(0, 10))

        # Pos A Row
        frame_pos_a = ctk.CTkFrame(self.tab_ctrl, fg_color="transparent")
        frame_pos_a.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(frame_pos_a, text=f"{self.strings['label_pos_a']} (Sell):", width=95, anchor="w").pack(side="left")
        ctk.CTkLabel(frame_pos_a, text="X:").pack(side="left", padx=(5, 2))
        self.entry_pos_a_x = ctk.CTkEntry(frame_pos_a, width=65)
        self.entry_pos_a_x.insert(0, str(self.config["pos_a"]["x"]))
        self.entry_pos_a_x.pack(side="left")
        ctk.CTkLabel(frame_pos_a, text="Y:").pack(side="left", padx=(8, 2))
        self.entry_pos_a_y = ctk.CTkEntry(frame_pos_a, width=65)
        self.entry_pos_a_y.insert(0, str(self.config["pos_a"]["y"]))
        self.entry_pos_a_y.pack(side="left")

        ctk.CTkButton(
            frame_pos_a,
            text=self.strings["btn_capture"],
            width=65,
            command=lambda: self.start_single_capture("Pos A"),
            fg_color="#2980b9",
            hover_color="#1f618d",
        ).pack(side="right", padx=(5, 0))
        ctk.CTkButton(
            frame_pos_a,
            text=self.strings["btn_test"],
            width=55,
            command=lambda: self.test_click_position("Pos A"),
            fg_color="#7f8c8d",
            hover_color="#95a5a6",
        ).pack(side="right")

        # Pos B Row
        frame_pos_b = ctk.CTkFrame(self.tab_ctrl, fg_color="transparent")
        frame_pos_b.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(frame_pos_b, text=f"{self.strings['label_pos_b']} ([-]):", width=95, anchor="w").pack(side="left")
        ctk.CTkLabel(frame_pos_b, text="X:").pack(side="left", padx=(5, 2))
        self.entry_pos_b_x = ctk.CTkEntry(frame_pos_b, width=65)
        self.entry_pos_b_x.insert(0, str(self.config["pos_b"]["x"]))
        self.entry_pos_b_x.pack(side="left")
        ctk.CTkLabel(frame_pos_b, text="Y:").pack(side="left", padx=(8, 2))
        self.entry_pos_b_y = ctk.CTkEntry(frame_pos_b, width=65)
        self.entry_pos_b_y.insert(0, str(self.config["pos_b"]["y"]))
        self.entry_pos_b_y.pack(side="left")

        ctk.CTkButton(
            frame_pos_b,
            text=self.strings["btn_capture"],
            width=65,
            command=lambda: self.start_single_capture("Pos B"),
            fg_color="#2980b9",
            hover_color="#1f618d",
        ).pack(side="right", padx=(5, 0))
        ctk.CTkButton(
            frame_pos_b,
            text=self.strings["btn_test"],
            width=55,
            command=lambda: self.test_click_position("Pos B"),
            fg_color="#7f8c8d",
            hover_color="#95a5a6",
        ).pack(side="right")

        # Pos C Row
        frame_pos_c = ctk.CTkFrame(self.tab_ctrl, fg_color="transparent")
        frame_pos_c.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(frame_pos_c, text=f"{self.strings['label_pos_c']} (Create):", width=95, anchor="w").pack(side="left")
        ctk.CTkLabel(frame_pos_c, text="X:").pack(side="left", padx=(5, 2))
        self.entry_pos_c_x = ctk.CTkEntry(frame_pos_c, width=65)
        self.entry_pos_c_x.insert(0, str(self.config["pos_c"]["x"]))
        self.entry_pos_c_x.pack(side="left")
        ctk.CTkLabel(frame_pos_c, text="Y:").pack(side="left", padx=(8, 2))
        self.entry_pos_c_y = ctk.CTkEntry(frame_pos_c, width=65)
        self.entry_pos_c_y.insert(0, str(self.config["pos_c"]["y"]))
        self.entry_pos_c_y.pack(side="left")

        ctk.CTkButton(
            frame_pos_c,
            text=self.strings["btn_capture"],
            width=65,
            command=lambda: self.start_single_capture("Pos C"),
            fg_color="#2980b9",
            hover_color="#1f618d",
        ).pack(side="right", padx=(5, 0))
        ctk.CTkButton(
            frame_pos_c,
            text=self.strings["btn_test"],
            width=55,
            command=lambda: self.test_click_position("Pos C"),
            fg_color="#7f8c8d",
            hover_color="#95a5a6",
        ).pack(side="right")

        # Section Controls
        lbl_sec_ctrl = ctk.CTkLabel(
            self.tab_ctrl,
            text=self.strings["section_controls"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_sec_ctrl.pack(anchor="w", padx=10, pady=(12, 4))

        frame_hotkey = ctk.CTkFrame(self.tab_ctrl, fg_color="transparent")
        frame_hotkey.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(frame_hotkey, text=self.strings["label_hotkey"]).pack(side="left")
        self.hotkey_menu = ctk.CTkOptionMenu(
            frame_hotkey,
            values=["F10", "F4", "F6", "F8", "F9", "F11", "F12"],
            command=self.on_change_hotkey,
            width=90,
        )
        self.hotkey_menu.set(self.config.get("toggle_hotkey", "F10"))
        self.hotkey_menu.pack(side="right")

        # Section Activity Log
        lbl_sec_log = ctk.CTkLabel(
            self.tab_ctrl,
            text=self.strings["section_log"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_sec_log.pack(anchor="w", padx=10, pady=(10, 4))

        self.txt_log = ctk.CTkTextbox(self.tab_ctrl, font=("Consolas", 11), wrap="word")
        self.txt_log.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        # ================= TAB 2: SETTINGS =================
        lbl_sec_timing = ctk.CTkLabel(
            self.tab_settings,
            text=self.strings["section_timing"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_sec_timing.pack(anchor="w", padx=15, pady=(12, 6))

        # Delay A->B
        frame_dab = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame_dab.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(frame_dab, text=self.strings["label_delay_ab"]).pack(side="left")
        self.entry_delay_ab = ctk.CTkEntry(frame_dab, width=80)
        self.entry_delay_ab.insert(0, str(self.config.get("delay_ab_ms", 300)))
        self.entry_delay_ab.pack(side="right")

        # Delay B->C
        frame_dbc = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame_dbc.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(frame_dbc, text=self.strings["label_delay_bc"]).pack(side="left")
        self.entry_delay_bc = ctk.CTkEntry(frame_dbc, width=80)
        self.entry_delay_bc.insert(0, str(self.config.get("delay_bc_ms", 200)))
        self.entry_delay_bc.pack(side="right")

        # Delay C->A
        frame_dca = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame_dca.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(frame_dca, text=self.strings["label_delay_ca"]).pack(side="left")
        self.entry_delay_ca = ctk.CTkEntry(frame_dca, width=80)
        self.entry_delay_ca.insert(0, str(self.config.get("delay_ca_ms", 400)))
        self.entry_delay_ca.pack(side="right")

        # Anti-Detection
        lbl_sec_anti = ctk.CTkLabel(
            self.tab_settings,
            text=self.strings["section_antidetect"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_sec_anti.pack(anchor="w", padx=15, pady=(18, 6))

        self.switch_human_var = ctk.BooleanVar(value=self.config.get("human_mouse", True))
        self.switch_human = ctk.CTkSwitch(
            self.tab_settings,
            text=self.strings["switch_human_mouse"],
            variable=self.switch_human_var,
        )
        self.switch_human.pack(anchor="w", padx=15, pady=5)

        self.switch_jitter_var = ctk.BooleanVar(value=self.config.get("jitter", True))
        self.switch_jitter = ctk.CTkSwitch(
            self.tab_settings,
            text=self.strings["switch_jitter"],
            variable=self.switch_jitter_var,
        )
        self.switch_jitter.pack(anchor="w", padx=15, pady=5)

        # Max Items Limit
        frame_limit = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame_limit.pack(fill="x", padx=15, pady=(10, 4))
        ctk.CTkLabel(frame_limit, text=self.strings["label_max_items"]).pack(side="left")
        self.entry_max_items = ctk.CTkEntry(frame_limit, width=80)
        self.entry_max_items.insert(0, str(self.config.get("max_items", 0)))
        self.entry_max_items.pack(side="right")

        # Save Button in Settings
        ctk.CTkButton(
            self.tab_settings,
            text=self.strings["btn_save_settings"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.save_config,
            height=40,
        ).pack(fill="x", padx=15, pady=25)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message: str, category: str = "Log"):
        t_str = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{t_str}] [{category}] {message}\n"
        if hasattr(self, "txt_log"):
            self.txt_log.insert("end", entry)
            self.txt_log.see("end")

    def bind_global_hotkey(self, key_name: str):
        try:
            if self.registered_hotkey:
                keyboard.remove_hotkey(self.registered_hotkey)
        except Exception:
            pass

        try:
            self.registered_hotkey = keyboard.add_hotkey(key_name, self.toggle_clicking)
            self.log(f"Global hotkey registered: {key_name}", category="Hotkey")
        except Exception as e:
            self.log(f"⚠️ Could not bind hotkey {key_name}: {e}", category="Hotkey")

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

    # --- SETUP WIZARD & MOUSE CAPTURE ---
    def start_setup_wizard(self):
        if self.is_running:
            self.stop_clicking()

        self.wizard_step = 1
        self.single_capture_target = None
        self.btn_wizard.configure(text=f"Wizard: Step 1/3 (Click 'Sell')", fg_color="#e67e22")
        self.log(self.strings["wizard_step_1"], category="Wizard")

        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()

        self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        self.mouse_listener.start()

    def start_single_capture(self, target_name: str):
        if self.is_running:
            self.stop_clicking()

        self.wizard_step = 0
        self.single_capture_target = target_name
        self.log(self.strings["capture_single"].format(target_name), category="Capture")

        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()

        self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        self.mouse_listener.start()

    def _on_mouse_click(self, x, y, button, pressed):
        if not pressed or button != mouse.Button.left:
            return

        # Handle Single Point Capture
        if self.single_capture_target:
            target = self.single_capture_target
            self.single_capture_target = None
            self.root.after(0, lambda: self._apply_single_capture(target, int(x), int(y)))
            return False

        # Handle Setup Wizard (Steps 1 -> 2 -> 3)
        if self.wizard_step == 1:
            self.root.after(0, lambda: self._apply_wizard_step_1(int(x), int(y)))
        elif self.wizard_step == 2:
            self.root.after(0, lambda: self._apply_wizard_step_2(int(x), int(y)))
        elif self.wizard_step == 3:
            self.root.after(0, lambda: self._apply_wizard_step_3(int(x), int(y)))
            return False

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

        self.log(self.strings["capture_done"].format(target, x, y), category="Capture")
        self.save_config()

    def _apply_wizard_step_1(self, x: int, y: int):
        self.entry_pos_a_x.delete(0, "end")
        self.entry_pos_a_x.insert(0, str(x))
        self.entry_pos_a_y.delete(0, "end")
        self.entry_pos_a_y.insert(0, str(y))
        self.log(self.strings["capture_done"].format("Position A", x, y), category="Capture")

        self.wizard_step = 2
        self.btn_wizard.configure(text=f"Wizard: Step 2/3 (Click '[-]')", fg_color="#e67e22")
        self.log(self.strings["wizard_step_2"], category="Wizard")

    def _apply_wizard_step_2(self, x: int, y: int):
        self.entry_pos_b_x.delete(0, "end")
        self.entry_pos_b_x.insert(0, str(x))
        self.entry_pos_b_y.delete(0, "end")
        self.entry_pos_b_y.insert(0, str(y))
        self.log(self.strings["capture_done"].format("Position B", x, y), category="Capture")

        self.wizard_step = 3
        self.btn_wizard.configure(text=f"Wizard: Step 3/3 (Click 'Create')", fg_color="#e67e22")
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

    def test_click_position(self, target: str):
        try:
            if target == "Pos A":
                x = int(self.entry_pos_a_x.get())
                y = int(self.entry_pos_a_y.get())
            elif target == "Pos B":
                x = int(self.entry_pos_b_x.get())
                y = int(self.entry_pos_b_y.get())
            else:
                x = int(self.entry_pos_c_x.get())
                y = int(self.entry_pos_c_y.get())

            self.log(f"Testing {target} at ({x}, {y}). Moving mouse...", category="Test")
            human_move_to(x, y, enabled=False)
            pyautogui.click()
            self.log(f"✅ Click performed at {target} ({x}, {y})", category="Test")
        except Exception as e:
            self.log(f"⚠️ Error testing {target}: {e}", category="Error")

    # --- CLICKING WORKER LOOP (A -> B -> C) ---
    def toggle_clicking(self):
        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        if self.is_running:
            return

        try:
            pos_a = (int(self.entry_pos_a_x.get()), int(self.entry_pos_a_y.get()))
            pos_b = (int(self.entry_pos_b_x.get()), int(self.entry_pos_b_y.get()))
            pos_c = (int(self.entry_pos_c_x.get()), int(self.entry_pos_c_y.get()))
        except ValueError:
            messagebox.showerror("Error", "Please set valid integer coordinates for Pos A, B, and C.")
            return

        self.is_running = True
        self.btn_toggle.configure(text=self.strings["btn_stop"], fg_color="#e74c3c", hover_color="#c0392b")
        self.log(self.strings["loop_started"], category="Control")

        self.worker_thread = threading.Thread(
            target=self._clicking_worker_loop,
            args=(pos_a, pos_b, pos_c),
            daemon=True,
        )
        self.worker_thread.start()

    def stop_clicking(self):
        self.is_running = False
        self.btn_toggle.configure(text=self.strings["btn_start"], fg_color="#2ecc71", hover_color="#27ae60")
        self.log(self.strings["loop_stopped"].format(self.stats.total_orders), category="Control")

    def _clicking_worker_loop(self, pos_a, pos_b, pos_c):
        delay_ab = max(50, int(self.entry_delay_ab.get())) / 1000.0
        delay_bc = max(50, int(self.entry_delay_bc.get())) / 1000.0
        delay_ca = max(100, int(self.entry_delay_ca.get())) / 1000.0
        humanize = self.switch_human_var.get()
        jitter = self.switch_jitter_var.get()
        max_items = max(0, int(self.entry_max_items.get()))

        cycle_count = 0
        while self.is_running:
            try:
                # 1. Click Position A (Top Item 'Sell' Button)
                human_move_to(pos_a[0], pos_a[1], enabled=humanize)
                if not self.is_running:
                    break
                pyautogui.click()

                if jitter:
                    time.sleep(get_gaussian_delay(delay_ab * 0.85, delay_ab * 1.15))
                else:
                    time.sleep(delay_ab)
                if not self.is_running:
                    break

                # 2. Click Position B ([-] Undercut 1 Silver Button)
                human_move_to(pos_b[0], pos_b[1], enabled=humanize)
                if not self.is_running:
                    break
                pyautogui.click()

                if jitter:
                    time.sleep(get_gaussian_delay(delay_bc * 0.85, delay_bc * 1.15))
                else:
                    time.sleep(delay_bc)
                if not self.is_running:
                    break

                # 3. Click Position C ('Create' Sell Order Button)
                human_move_to(pos_c[0], pos_c[1], enabled=humanize)
                if not self.is_running:
                    break
                pyautogui.click()

                cycle_count += 1
                self.stats.record_sale(price=0, strategy="3point_clicker")
                self.root.after(0, lambda c=cycle_count: self.log(self.strings["cycle_sold"].format(c), category="Cycle"))

                if max_items > 0 and cycle_count >= max_items:
                    self.root.after(0, self.stop_clicking)
                    break

                # Wait for order to place and next item to slide into position A
                if jitter:
                    time.sleep(get_gaussian_delay(delay_ca * 0.85, delay_ca * 1.15))
                else:
                    time.sleep(delay_ca)

            except pyautogui.FailSafeException:
                self.root.after(0, self.stop_clicking)
                self.root.after(0, lambda: self.log("⚠️ PyAutoGUI FailSafe triggered!", category="Failsafe"))
                break
            except Exception as e:
                self.root.after(0, lambda err=e: self.log(f"⚠️ Worker error: {err}", category="Error"))
                time.sleep(0.5)

    def on_closing(self):
        self.is_running = False
        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
        try:
            if self.registered_hotkey:
                keyboard.remove_hotkey(self.registered_hotkey)
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
