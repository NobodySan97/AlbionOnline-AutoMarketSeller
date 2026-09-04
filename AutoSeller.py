"""
Albion Online — Auto Market Seller
Dual-Mode Market Automation:
  Mode 1: 3-Point Fast Clicker (Sell -> [-] Undercut 1 Silver -> Create Order)
  Mode 2: Smart OCR Seller (Sell -> OCR Lowest Order -> Custom % Discount & Floor Protection -> Type Price -> Create Order)
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
from collections import Counter
from tkinter import filedialog, messagebox

import cv2
import keyboard
import numpy as np
import pyautogui
from PIL import Image, ImageGrab
from pynput import mouse
import pytesseract

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
pyautogui.FAILSAFE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# --- MULTILINGUAL STRINGS (STRICT 1:1 KEY & PLACEHOLDER PARITY) ---
STRINGS = {
    "en": {
        "app_title": "Market Seller — Auto Clicker & Smart OCR",
        "header_title": "MARKET SELLER AUTO CLICKER",
        "tab_positions": "Positions & Controls",
        "tab_settings": "Settings",
        "section_positions": "Click Positions",
        "btn_wizard": "Setup Wizard (3 Click)",
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
        "label_delay_ocr": "Delay before OCR read:",
        "section_antidetect": "Anti-Detection & Humanization",
        "switch_human_mouse": "Humanized Bézier Mouse Movement",
        "switch_human_type": "Humanized Typing Simulation",
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
        "mode_label": "Operating Mode:",
        "mode_3point": "⚡ 3-Point Fast ([-])",
        "mode_ocr": "🧠 Smart OCR (Price + %)",
        "section_ocr_coords": "Smart OCR Coordinates",
        "label_pos_sell": "Pos Sell (Item)",
        "label_price_box": "Price Area (OCR)",
        "label_price_input": "Price Input Field",
        "label_create_order": "Create Order Button",
        "section_pricing": "Pricing Strategy & Discount",
        "label_discount_percent": "Discount Percentage (%):",
        "label_floor_price": "Safety Floor Price (Silver):",
        "label_strategy_type": "Discount Strategy:",
        "btn_test_ocr": "🔍 Test OCR",
        "btn_capture_area": "Capture Box",
        "btn_wizard_ocr": "OCR Wizard (4 Steps)",
        "ocr_test_result": "[OCR Test] Detected: {:,} Silver | Target: {:,} Silver ({})",
        "ocr_read_fail": "❌ Could not read price from screen area.",
        "ocr_below_floor": "⚠️ Detected price ({:,}) is below floor price ({:,}). Item protected!",
        "ocr_sold": "[Cycle #{}] Detected: {:,} -> Sold at {:,} Silver ({})",
        "label_tesseract": "Tesseract Executable:",
        "btn_browse_tesseract": "📁 Browse...",
        "btn_detect_tesseract": "🔍 Auto-Detect",
        "tesseract_found": "✅ Tesseract located at: {}",
        "tesseract_not_found": "⚠️ Tesseract not found. Please specify path or install Tesseract OCR.",
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
        "app_title": "Market Seller — Auto Clicker & Smart OCR",
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
        "label_delay_ocr": "Ritardo prima di lettura OCR:",
        "section_antidetect": "Anti-Rilevamento & Umanizzazione",
        "switch_human_mouse": "Movimento Mouse Naturale (Bézier)",
        "switch_human_type": "Digitazione Umana Naturale",
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
        "mode_label": "Modalità Operativa:",
        "mode_3point": "⚡ 3-Point Veloce ([-])",
        "mode_ocr": "🧠 Smart OCR (Prezzo + %)",
        "section_ocr_coords": "Coordinate Smart OCR",
        "label_pos_sell": "Pos Vendita (Oggetto)",
        "label_price_box": "Area Prezzo (OCR)",
        "label_price_input": "Campo Input Prezzo",
        "label_create_order": "Pulsante Crea Ordine",
        "section_pricing": "Strategia Prezzo & Sconto",
        "label_discount_percent": "Sconto Percentuale (%):",
        "label_floor_price": "Prezzo Minimo Floor (Silver):",
        "label_strategy_type": "Strategia di Sconto:",
        "btn_test_ocr": "🔍 Test OCR",
        "btn_capture_area": "Cattura Area",
        "btn_wizard_ocr": "Setup Wizard OCR (4 Step)",
        "ocr_test_result": "[Test OCR] Rilevato: {:,} Silver | Calcolato: {:,} Silver ({})",
        "ocr_read_fail": "❌ Impossibile leggere il prezzo dall'area indicata.",
        "ocr_below_floor": "⚠️ Prezzo rilevato ({:,}) inferiore al prezzo minimo ({:,}). Oggetto protetto!",
        "ocr_sold": "[Ciclo #{}] Rilevato: {:,} -> Venduto a {:,} Silver ({})",
        "switch_human_type": "Digitazione Umana Naturale",
        "label_tesseract": "Eseguibile Tesseract:",
        "btn_browse_tesseract": "📁 Sfoglia...",
        "btn_detect_tesseract": "🔍 Rileva Automaticamente",
        "tesseract_found": "✅ Tesseract trovato su: {}",
        "tesseract_not_found": "⚠️ Tesseract non trovato. Specifica il percorso o installa Tesseract OCR.",
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


def human_type(text: str, enabled: bool = True):
    """Types characters with natural randomized keystroke intervals."""
    if not enabled:
        pyautogui.write(text, interval=0.0)
        return
    for ch in text:
        pyautogui.write(ch)
        time.sleep(random.uniform(0.015, 0.040))


# --- HARDWARE-LEVEL GLOBAL HOTKEY POLLING (GetAsyncKeyState) ---
VK_KEY_MAP = {
    "F1": 0x70,
    "F2": 0x71,
    "F3": 0x72,
    "F4": 0x73,
    "F5": 0x74,
    "F6": 0x75,
    "F7": 0x76,
    "F8": 0x77,
    "F9": 0x78,
    "F10": 0x79,
    "F11": 0x7A,
    "F12": 0x7B,
    "`": 0xC0,
    "~": 0xC0,
    "INSERT": 0x2D,
    "DELETE": 0x2E,
    "HOME": 0x24,
    "END": 0x23,
    "PAGEUP": 0x21,
    "PAGEDOWN": 0x22,
    "PAUSE": 0x13,
}

if sys.platform == "win32":
    try:
        ctypes.windll.user32.GetAsyncKeyState.restype = ctypes.c_short
        ctypes.windll.user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
    except Exception:
        pass


def is_key_pressed_win32(vk_code: int) -> bool:
    """Checks if virtual key is currently pressed down via Windows GetAsyncKeyState."""
    if sys.platform != "win32":
        return False
    try:
        return bool(ctypes.windll.user32.GetAsyncKeyState(vk_code) & 0x8000)
    except Exception:
        return False


class WindowsHotkeyPoller:
    """Hardware-level polling using Windows GetAsyncKeyState.

    Bypasses UIPI (User Interface Privilege Isolation) and anti-cheat hooks.
    Operates 100% reliably even when Albion Online is running with elevated privileges
    or exclusive fullscreen.
    """

    def __init__(self, on_hotkey, default_key: str = "F10", poll_interval: float = 0.02):
        self.on_hotkey = on_hotkey
        self.key_name = default_key
        self.target_vk = VK_KEY_MAP.get(default_key.upper(), 0x79)
        self.poll_interval = poll_interval
        self.running = True
        self.last_press_time = 0.0
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def set_key(self, key_name: str):
        self.key_name = key_name
        self.target_vk = VK_KEY_MAP.get(key_name.upper(), 0x79)

    def _poll_loop(self):
        if sys.platform != "win32":
            return
        user32 = ctypes.windll.user32
        while self.running:
            time.sleep(self.poll_interval)
            if not self.target_vk:
                continue
            try:
                state = user32.GetAsyncKeyState(self.target_vk)
                if state & 0x8000:
                    now = time.time()
                    if now - self.last_press_time > 0.4:
                        self.last_press_time = now
                        try:
                            self.on_hotkey()
                        except Exception:
                            pass
                        while self.running and (user32.GetAsyncKeyState(self.target_vk) & 0x8000):
                            time.sleep(0.03)
            except Exception:
                pass

    def stop(self):
        self.running = False


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
            val = float(clean_str)
        else:
            clean_str = num_part.replace(".", "").replace(",", ".")
            val = float(clean_str)
    elif dot_count > 1:
        clean_str = num_part.replace(".", "")
        val = float(clean_str)
    elif comma_count > 1:
        clean_str = num_part.replace(",", "")
        val = float(clean_str)
    elif dot_count == 1:
        parts = num_part.split(".")
        if suffix:
            val = float(num_part)
        elif len(parts[1]) == 3:
            val = float(parts[0] + parts[1])
        else:
            val = float(num_part)
    elif comma_count == 1:
        parts = num_part.split(",")
        if suffix:
            val = float(parts[0] + "." + parts[1])
        elif len(parts[1]) == 3:
            val = float(parts[0] + parts[1])
        else:
            val = float(parts[0] + "." + parts[1])
    else:
        try:
            val = float(num_part)
        except ValueError:
            return None

    if suffix == "K":
        val *= 1_000
    elif suffix == "M":
        val *= 1_000_000
    elif suffix == "T":
        val *= 1_000

    return int(round(val))


def detect_tesseract_binary(custom_config_path: str = "") -> str:
    """Detects Tesseract executable across PyInstaller, portable project, and common Windows locations."""
    meipass = getattr(sys, "_MEIPASS", "")
    candidate_paths = [
        custom_config_path if custom_config_path else "",
        os.path.join(meipass, "tesseract", "tesseract.exe") if meipass else "",
        os.path.join(meipass, "tesseract.exe") if meipass else "",
        os.path.join(BASE_DIR, "tesseract", "tesseract.exe"),
        os.path.join(BASE_DIR, "tesseract-portable", "tesseract.exe"),
        os.path.join(BASE_DIR, "tesseract.exe"),
        r"C:\Program Files\Tesseract-OCR	esseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR	esseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR	esseract.exe"),
        os.path.expandvars(r"%APPDATA%\Tesseract-OCR	esseract.exe"),
        r"C:	ools	esseract	esseract.exe",
        shutil.which("tesseract.exe") or "",
        shutil.which("tesseract") or "",
    ]
    for p in candidate_paths:
        if p and os.path.isfile(p):
            return os.path.abspath(p)
    return ""


class OcrReader:
    """Preprocesses cropped regions and executes Tesseract OCR for numerical price detection."""

    @staticmethod
    def preprocess_image(pil_image: Image.Image) -> list[Image.Image]:
        img_np = np.array(pil_image)
        if len(img_np.shape) == 3:
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_np

        scale = 3.0
        width = int(gray.shape[1] * scale)
        height = int(gray.shape[0] * scale)
        resized = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

        variants = []
        block_size = max(15, (resized.shape[0] // 4) * 2 + 1)
        blurred = cv2.GaussianBlur(resized, (3, 3), 0)
        thresh_adapt = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, 3
        )
        variants.append(Image.fromarray(thresh_adapt))
        variants.append(Image.fromarray(cv2.bitwise_not(thresh_adapt)))

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(resized)
        _, thresh_otsu = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(Image.fromarray(thresh_otsu))
        variants.append(Image.fromarray(cv2.bitwise_not(thresh_otsu)))

        return variants

    @classmethod
    def read_number_from_bbox(
        cls, bbox: tuple[int, int, int, int], whitelist: str = "0123456789.,kKmMtT"
    ) -> int | None:
        x1, y1, x2, y2 = bbox
        if x2 <= x1 or y2 <= y1:
            return None
        try:
            grab = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            variants = cls.preprocess_image(grab)
        except Exception:
            return None

        psm_configs = ["--psm 7", "--psm 8", "--psm 6"]
        results = []
        for i, img in enumerate(variants):
            psm = psm_configs[i % len(psm_configs)]
            tess_config = f"{psm} -c tessedit_char_whitelist={whitelist}"
            try:
                raw_text = pytesseract.image_to_string(img, config=tess_config).strip()
                parsed = parse_albion_number(raw_text)
                if parsed is not None and parsed > 0:
                    results.append(parsed)
            except Exception:
                pass

        if not results:
            return None

        return Counter(results).most_common(1)[0][0]


# --- PRICING ENGINE ---
def calculate_target_price(
    detected_price: int | None,
    discount_percent: float = 1.0,
    floor_price: int = 0,
    strategy: str = "percentage",
) -> tuple[int, str]:
    """
    Calculates target sell price based on percentage discount and safety floor.
    strategy:
      - 'percentage': applies discount_percent (e.g. 1%, 2%, 5%) -> price * (1 - discount/100)
      - 'undercut_1': undercuts by exactly 1 Silver -> price - 1
    """
    if detected_price is None or detected_price <= 0:
        return (0, "ocr_failure")

    if strategy == "undercut_1":
        raw_price = detected_price - 1 if detected_price > 1 else 1
        reason = "undercut_1"
    else:
        discount_factor = max(0.0, 1.0 - (discount_percent / 100.0))
        raw_price = int(round(detected_price * discount_factor))
        reason = f"discount_{discount_percent:.1f}%"

    calculated = max(1, raw_price)

    if floor_price > 0:
        if detected_price < floor_price:
            return (floor_price, "below_floor_safety_stop")
        if calculated < floor_price:
            return (floor_price, "floor_price_clamped")

    return (calculated, reason)


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


# --- CONFIG DEEP MERGE ---
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
            writer = csv.DictWriter(
                f, fieldnames=["timestamp", "item", "price", "strategy", "reason", "diff_percent"]
            )
            writer.writeheader()
            writer.writerows(self.records)


# =====================================================================
#                MAIN AUTO MARKET SELLER APPLICATION
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
        self.area_p1 = None
        self.registered_hotkey = None
        self.hotkey_poller = None
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
        self.root.geometry("660x780")
        self.root.minsize(620, 720)

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
            text=f"{self.strings['btn_start']} [{self.config.get('toggle_hotkey', 'F10')}]",
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
        # Mode Selector (Segmented Button)
        self.mode_var = ctk.StringVar(value=self.config.get("mode", "3point"))
        mode_val = self.strings["mode_3point"] if self.mode_var.get() == "3point" else self.strings["mode_ocr"]

        self.mode_selector = ctk.CTkSegmentedButton(
            self.tab_ctrl,
            values=[self.strings["mode_3point"], self.strings["mode_ocr"]],
            command=self.on_change_mode,
            font=ctk.CTkFont(size=13, weight="bold"),
            selected_color="#2980b9",
            selected_hover_color="#1f618d",
            height=36,
        )
        self.mode_selector.set(mode_val)
        self.mode_selector.pack(fill="x", padx=10, pady=(6, 8))

        # --- FRAME 1: 3-POINT MODE CONTROLS ---
        self.frame_3point = ctk.CTkFrame(self.tab_ctrl, fg_color="transparent")

        # 3-Point Wizard Button
        self.btn_wizard = ctk.CTkButton(
            self.frame_3point,
            text=self.strings["btn_wizard"],
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8e44ad",
            hover_color="#732d91",
            height=32,
            command=self.start_setup_wizard,
        )
        self.btn_wizard.pack(fill="x", padx=0, pady=(0, 8))

        # Pos A Row
        frame_pos_a = ctk.CTkFrame(self.frame_3point, fg_color="transparent")
        frame_pos_a.pack(fill="x", pady=2)
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
        frame_pos_b = ctk.CTkFrame(self.frame_3point, fg_color="transparent")
        frame_pos_b.pack(fill="x", pady=2)
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
        frame_pos_c = ctk.CTkFrame(self.frame_3point, fg_color="transparent")
        frame_pos_c.pack(fill="x", pady=2)
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

        # --- FRAME 2: SMART OCR CONTROLS ---
        self.frame_ocr = ctk.CTkFrame(self.tab_ctrl, fg_color="transparent")

        # OCR Wizard Button
        self.btn_wizard_ocr = ctk.CTkButton(
            self.frame_ocr,
            text=self.strings["btn_wizard_ocr"],
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8e44ad",
            hover_color="#732d91",
            height=32,
            command=self.start_ocr_wizard,
        )
        self.btn_wizard_ocr.pack(fill="x", padx=0, pady=(0, 6))

        # Pos Sell (Item)
        f_ocr_sell = ctk.CTkFrame(self.frame_ocr, fg_color="transparent")
        f_ocr_sell.pack(fill="x", pady=2)
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
        f_ocr_box = ctk.CTkFrame(self.frame_ocr, fg_color="transparent")
        f_ocr_box.pack(fill="x", pady=2)
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
        f_ocr_inp = ctk.CTkFrame(self.frame_ocr, fg_color="transparent")
        f_ocr_inp.pack(fill="x", pady=2)
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
        f_ocr_crt = ctk.CTkFrame(self.frame_ocr, fg_color="transparent")
        f_ocr_crt.pack(fill="x", pady=2)
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
        card_pricing = ctk.CTkFrame(self.frame_ocr, fg_color="#21252d", corner_radius=6)
        card_pricing.pack(fill="x", pady=(6, 4), padx=2)

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

        # Quick Preset Buttons
        f_presets = ctk.CTkFrame(card_pricing, fg_color="transparent")
        f_presets.pack(fill="x", padx=8, pady=(2, 4))
        for p_val in [1.0, 2.0, 5.0, 10.0]:
            ctk.CTkButton(
                f_presets,
                text=f"{p_val:.0f}%",
                width=45,
                height=24,
                fg_color="#34495e",
                command=lambda v=p_val: self.apply_preset_discount(v),
            ).pack(side="left", padx=2)

        ctk.CTkButton(
            f_presets,
            text="-1 Silver",
            width=70,
            height=24,
            fg_color="#d35400",
            command=lambda: self.apply_preset_discount("undercut_1"),
        ).pack(side="left", padx=4)

        # Floor Price
        f_floor = ctk.CTkFrame(card_pricing, fg_color="transparent")
        f_floor.pack(fill="x", padx=8, pady=(2, 6))
        ctk.CTkLabel(f_floor, text=self.strings["label_floor_price"]).pack(side="left")
        self.entry_floor_price = ctk.CTkEntry(f_floor, width=90)
        self.entry_floor_price.insert(0, str(self.config.get("floor_price", 0)))
        self.entry_floor_price.pack(side="right")

        # Pack initial mode frame
        if self.mode_var.get() == "ocr":
            self.frame_ocr.pack(fill="x", padx=10, pady=(0, 4))
        else:
            self.frame_3point.pack(fill="x", padx=10, pady=(0, 4))

        # Common Controls Frame
        self.frame_controls = ctk.CTkFrame(self.tab_ctrl, fg_color="transparent")
        self.frame_controls.pack(fill="both", expand=True, padx=10, pady=(4, 8))

        # Section Controls / Hotkey
        frame_hotkey = ctk.CTkFrame(self.frame_controls, fg_color="transparent")
        frame_hotkey.pack(fill="x", pady=2)
        ctk.CTkLabel(frame_hotkey, text=self.strings["label_hotkey"], font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.hotkey_menu = ctk.CTkOptionMenu(
            frame_hotkey,
            values=["F10", "F4", "F6", "F8", "F9", "F11", "F12", "PAUSE", "INSERT"],
            command=self.on_change_hotkey,
            width=100,
        )
        self.hotkey_menu.set(self.config.get("toggle_hotkey", "F10"))
        self.hotkey_menu.pack(side="right")

        # Section Activity Log
        lbl_sec_log = ctk.CTkLabel(
            self.frame_controls,
            text=self.strings["section_log"],
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        lbl_sec_log.pack(anchor="w", pady=(6, 2))

        self.txt_log = ctk.CTkTextbox(self.frame_controls, font=("Consolas", 11), wrap="word")
        self.txt_log.pack(fill="both", expand=True, pady=(0, 4))

        # ================= TAB 2: SETTINGS =================
        lbl_sec_timing = ctk.CTkLabel(
            self.tab_settings,
            text=self.strings["section_timing"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_sec_timing.pack(anchor="w", padx=15, pady=(10, 4))

        # Delay A->B
        frame_dab = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame_dab.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(frame_dab, text=self.strings["label_delay_ab"]).pack(side="left")
        self.entry_delay_ab = ctk.CTkEntry(frame_dab, width=80)
        self.entry_delay_ab.insert(0, str(self.config.get("delay_ab_ms", 300)))
        self.entry_delay_ab.pack(side="right")

        # Delay B->C
        frame_dbc = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame_dbc.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(frame_dbc, text=self.strings["label_delay_bc"]).pack(side="left")
        self.entry_delay_bc = ctk.CTkEntry(frame_dbc, width=80)
        self.entry_delay_bc.insert(0, str(self.config.get("delay_bc_ms", 200)))
        self.entry_delay_bc.pack(side="right")

        # Delay C->A
        frame_dca = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame_dca.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(frame_dca, text=self.strings["label_delay_ca"]).pack(side="left")
        self.entry_delay_ca = ctk.CTkEntry(frame_dca, width=80)
        self.entry_delay_ca.insert(0, str(self.config.get("delay_ca_ms", 400)))
        self.entry_delay_ca.pack(side="right")

        # Delay OCR
        frame_docr = ctk.CTkFrame(self.tab_settings, fg_color="transparent")
        frame_docr.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(frame_docr, text=self.strings["label_delay_ocr"]).pack(side="left")
        self.entry_delay_ocr = ctk.CTkEntry(frame_docr, width=80)
        self.entry_delay_ocr.insert(0, str(self.config.get("delay_ocr_ms", 250)))
        self.entry_delay_ocr.pack(side="right")

        # Anti-Detection
        lbl_sec_anti = ctk.CTkLabel(
            self.tab_settings,
            text=self.strings["section_antidetect"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        lbl_sec_anti.pack(anchor="w", padx=15, pady=(14, 4))

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
            height=38,
        ).pack(fill="x", padx=15, pady=20)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log(self, message: str, category: str = "Log"):
        t_str = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{t_str}] [{category}] {message}\n"
        if hasattr(self, "txt_log"):
            self.txt_log.insert("end", entry)
            self.txt_log.see("end")

    # --- MODE & SETTINGS SWITCHING ---
    def on_change_mode(self, chosen_value: str):
        if "3-Point" in chosen_value:
            self.mode_var.set("3point")
            self.frame_ocr.pack_forget()
            self.frame_3point.pack(fill="x", padx=10, pady=(0, 4), before=self.frame_controls)
        else:
            self.mode_var.set("ocr")
            self.frame_3point.pack_forget()
            self.frame_ocr.pack(fill="x", padx=10, pady=(0, 4), before=self.frame_controls)
        self.config["mode"] = self.mode_var.get()
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
            self.log("Strategia impostata su: Sconto 1 Silver (Undercut-1)", category="Pricing")
        else:
            self.config["strategy"] = "percentage"
            self.config["discount_percent"] = float(val)
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

        try:
            import winsound
            if not self.is_running:
                winsound.Beep(1200, 100)
            else:
                winsound.Beep(600, 140)
        except Exception:
            pass

        self.root.after(0, self.toggle_clicking)

    def bind_global_hotkey(self, key_name: str):
        # 1. Hardware/Kernel polling (Primary: works when Albion/EAC is focused or Admin)
        if hasattr(self, "hotkey_poller") and self.hotkey_poller is not None:
            self.hotkey_poller.set_key(key_name)
        else:
            self.hotkey_poller = WindowsHotkeyPoller(self.handle_hotkey_press, default_key=key_name)

        # 2. Secondary layer: low-level keyboard hook
        try:
            if self.registered_hotkey:
                keyboard.remove_hotkey(self.registered_hotkey)
        except Exception:
            pass

        try:
            self.registered_hotkey = keyboard.add_hotkey(key_name, self.handle_hotkey_press)
        except Exception:
            self.registered_hotkey = None

        # 3. Tertiary layer: Tkinter local window binding
        try:
            self.root.bind_all(f"<{key_name}>", lambda e: self.handle_hotkey_press())
        except Exception:
            pass

        self.update_toggle_button_text()
        self.log(f"Hotkey {key_name} attivo (Kernel Polling + Hook)", category="Hotkey")

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

    def start_ocr_wizard(self):
        if self.is_running:
            self.stop_clicking()
        self.wizard_step = 11  # Step 11: Sell, 12: Box Top-Left, 13: Box Bottom-Right, 14: Input, 15: Create
        self.single_capture_target = None
        self.btn_wizard_ocr.configure(text="Wizard OCR: 1/4 Click 'Sell'", fg_color="#e67e22")
        self.log("[Wizard OCR] Passo 1/4: Fai click sul tasto 'Sell' dell'oggetto in inventario", category="Wizard")

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

    def start_area_capture(self):
        if self.is_running:
            self.stop_clicking()
        self.wizard_step = 101  # Top-Left point
        self.area_p1 = None
        self.log("[Cattura Area] Fai click nell'angolo in ALTO A SINISTRA dell'area prezzo...", category="Capture")

        if self.mouse_listener and self.mouse_listener.is_alive():
            self.mouse_listener.stop()
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
            if self.mouse_listener and self.mouse_listener.is_alive():
                self.mouse_listener.stop()
            self.btn_wizard.configure(text=self.strings["btn_wizard"], fg_color="#8e44ad")
            self.btn_wizard_ocr.configure(text=self.strings["btn_wizard_ocr"], fg_color="#8e44ad")
            self.log("Wizard / Cattura annullata.", category="Wizard")
            return

        if self.is_running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        if self.is_running:
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
        while self.is_running:
            try:
                if mode == "3point":
                    # 1. Click Position A (Top Item 'Sell' Button)
                    human_move_to(pos_a[0], pos_a[1], enabled=humanize)
                    if not self.is_running:
                        break
                    pyautogui.click()

                    time.sleep(get_gaussian_delay(delay_ab * 0.85, delay_ab * 1.15) if jitter else delay_ab)
                    if not self.is_running:
                        break

                    # 2. Click Position B ([-] Undercut 1 Silver Button)
                    human_move_to(pos_b[0], pos_b[1], enabled=humanize)
                    if not self.is_running:
                        break
                    pyautogui.click()

                    time.sleep(get_gaussian_delay(delay_bc * 0.85, delay_bc * 1.15) if jitter else delay_bc)
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

                else:
                    # SMART OCR MODE
                    # 1. Click Sell on top item
                    human_move_to(pos_sell[0], pos_sell[1], enabled=humanize)
                    if not self.is_running:
                        break
                    pyautogui.click()

                    time.sleep(get_gaussian_delay(delay_ab * 0.85, delay_ab * 1.15) if jitter else delay_ab)
                    if not self.is_running:
                        break

                    # 2. OCR Read Price
                    time.sleep(delay_ocr)
                    detected = None
                    for attempt in range(3):
                        if not self.is_running:
                            break
                        detected = OcrReader.read_number_from_bbox(price_box)
                        if detected is not None and detected > 0:
                            break
                        time.sleep(0.04)

                    if not self.is_running:
                        break

                    if detected is None or detected <= 0:
                        self.root.after(0, lambda: self.log(self.strings["ocr_read_fail"], category="OCR"))
                        time.sleep(0.5)
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
                        time.sleep(0.5)
                        continue

                    # 4. Click Price Input Field -> Clear -> Type Target Price
                    human_move_to(pos_input[0], pos_input[1], enabled=humanize)
                    if not self.is_running:
                        break
                    pyautogui.click()
                    time.sleep(0.04)

                    pyautogui.hotkey("ctrl", "a")
                    pyautogui.press("backspace")
                    time.sleep(0.02)

                    human_type(str(target_price), enabled=human_type_enabled)
                    if not self.is_running:
                        break

                    time.sleep(get_gaussian_delay(delay_bc * 0.85, delay_bc * 1.15) if jitter else delay_bc)
                    if not self.is_running:
                        break

                    # 5. Click Create Order Button
                    human_move_to(pos_create[0], pos_create[1], enabled=humanize)
                    if not self.is_running:
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

                # Inter-cycle delay
                time.sleep(get_gaussian_delay(delay_ca * 0.85, delay_ca * 1.15) if jitter else delay_ca)

            except pyautogui.FailSafeException:
                self.root.after(0, self.stop_clicking)
                self.root.after(0, lambda: self.log("⚠️ PyAutoGUI FailSafe triggered!", category="Failsafe"))
                break
            except Exception as e:
                self.root.after(0, lambda err=e: self.log(f"⚠️ Worker error: {err}", category="Error"))
                time.sleep(0.5)

    def on_closing(self):
        self.is_running = False
        if hasattr(self, "hotkey_poller") and self.hotkey_poller:
            self.hotkey_poller.stop()
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
