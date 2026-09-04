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
from collections import Counter
import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
import keyboard
import numpy as np
from PIL import Image, ImageGrab
import pyautogui
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
pyautogui.FAILSAFE = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# MULTILINGUAL STRINGS
STRINGS = {
    "en": {
        "app_title": "🤖 Albion Auto Market Seller v2.0 Pro",
        "tab_dashboard": "📊 Dashboard",
        "tab_pricing": "💰 Pricing & Strategy",
        "tab_anti_bot": "🛡️ Anti-Bot & Input",
        "tab_logs": "📋 Activity Log",
        "status_ready": "Status: Ready",
        "status_running": "Status: Running",
        "status_paused": "Status: Paused",
        "status_calibrating": "Status: Calibrating...",
        "author_label": "Author: NobodySan97",
        "resolution_label": "Resolution: {}x{}",
        "button_start": "▶ Start Cycle (F4)",
        "button_stop": "■ Stop Cycle (F4)",
        "button_skip": "⏩ Skip Item (F5)",
        "button_cal_full": "🔧 Full Calibration (F1)",
        "button_export_csv": "💾 Export CSV Report",
        "button_reset_stats": "🔄 Reset Statistics",
        "button_save_config": "💾 Save Config",
        "button_tesseract": "⚙️ Set Tesseract Path",
        "button_test_templates": "🔍 Test Template Match (OpenCV)",
        "label_strategy": "Pricing Strategy:",
        "strategy_undercut_1": "1 Silver Undercut (-1 Silver)",
        "strategy_percentage": "Discount Ratio (% of Price)",
        "strategy_tiered": "Tiered Dynamic Undercut",
        "label_fallback_ratio": "Discount Ratio (% of Price):",
        "label_max_diff": "Max Allowed Price Diff (%):",
        "label_floor_price": "Floor Price (Min Silver Allowed):",
        "switch_human_mouse": "Humanized Bézier Mouse Movement",
        "switch_human_typing": "Natural Typing Variations",
        "switch_auto_template": "Auto-Detect Buttons (Template Match)",
        "card_orders": "Orders Created",
        "card_total_silver": "Total Silver Listed",
        "card_avg_price": "Avg Order Price",
        "card_time_active": "Active Time",
        "info_config_loaded": "✅ Configuration loaded.",
        "info_config_saved": "💾 Configuration saved.",
        "info_no_config": "ℹ️ Created default configuration.",
        "log_ready": "🎯 AutoMarketSeller Pro Ready.",
        "log_cal_start": "🔧 Calibration started. Follow the overlay instructions.",
        "log_cal_hint": "ℹ️ Press 'Esc' to cancel calibration at any time.",
        "log_cal_done": "✅ Calibration complete! Saved to auto_config.json.",
        "log_cal_cancel": "❌ Calibration cancelled.",
        "log_main_start": "🚀 Sales automation started (F4 to stop, F5 to skip).",
        "log_main_stop": "🛑 Sales cycle stopped by user (F4).",
        "log_cycle_skip": "⏩ Skipped current item by user (F5).",
        "log_test_price": "Test 'Price': {:,}",
        "log_test_price_fail": "❌ Test 'Price': OCR recognition failed.",
        "log_test_avg_price": "Test 'Avg Price': {:,}",
        "log_test_avg_price_fail": "❌ Test 'Avg Price': OCR recognition failed.",
        "cal_window_title": "Calibration Mode",
        "cal_step_info": "[Step {}/{}]",
        "cal_instruction_point": "{}\nRIGHT-CLICK on:\n'{}'",
        "cal_instruction_area": "{}\nHold SHIFT and drag to select area of:\n'{}'\n\n(Release and RIGHT-CLICK to confirm)",
        "main_num1_ok": "Lowest Sell Order: {:,} Silver",
        "main_num1_fail": "⚠️ Could not read lowest sell order.",
        "main_num2_ok": "Average Market Price: {:,} Silver",
        "main_num2_fail": "❌ Could not read average price. Skipping item.",
        "main_value_entered": "✅ Order placed at: {:,} Silver (Strategy: {})",
        "main_failsafe": "⚠️ PyAutoGUI Failsafe triggered (cursor at screen corner).",
        "main_critical_error": "Critical error in main loop: {}",
        "tesseract_configured": "✅ Tesseract configured at: {}",
        "export_success": "✅ Statistics exported to:\n{}",
        "log_template_found": "✅ Template matched for '{}': at ({}, {}) [Confidence: {:.0f}%]",
        "log_template_not_found": "⚠️ Template for '{}' not detected on screen. Using saved coords.",
        "log_template_saved": "📸 Template captured & saved for '{}'",
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
        "app_title": "🤖 Albion Auto Market Seller v2.0 Pro",
        "tab_dashboard": "📊 Dashboard",
        "tab_pricing": "💰 Prezzo & Strategia",
        "tab_anti_bot": "🛡️ Anti-Bot & Input",
        "tab_logs": "📋 Log Attività",
        "status_ready": "Stato: Pronto",
        "status_running": "Stato: In Esecuzione",
        "status_paused": "Stato: In Pausa",
        "status_calibrating": "Stato: Calibrazione...",
        "author_label": "Autore: NobodySan97",
        "resolution_label": "Risoluzione: {}x{}",
        "button_start": "▶ Avvia Ciclo (F4)",
        "button_stop": "■ Ferma Ciclo (F4)",
        "button_skip": "⏩ Salta Oggetto (F5)",
        "button_cal_full": "🔧 Calibrazione Completa (F1)",
        "button_export_csv": "💾 Esporta Report CSV",
        "button_reset_stats": "🔄 Azzera Statistiche",
        "button_save_config": "💾 Salva Configurazione",
        "button_tesseract": "⚙️ Imposta Percorso Tesseract",
        "button_test_templates": "🔍 Testa Template Match (OpenCV)",
        "label_strategy": "Strategia di Prezzo:",
        "strategy_undercut_1": "Undercut 1 Silver (-1 Silver)",
        "strategy_percentage": "Sconto Percentuale (% Prezzo)",
        "strategy_tiered": "Undercut Dinamico per Fasce",
        "label_fallback_ratio": "Rapporto di Sconto (% del Prezzo):",
        "label_max_diff": "Differenza Massima Ammessa (%):",
        "label_floor_price": "Prezzo Minimo Floor (Silver):",
        "switch_human_mouse": "Movimento Mouse con Curve di Bézier",
        "switch_human_typing": "Variazione Naturale Digitazione",
        "switch_auto_template": "Auto-Rileva Pulsanti (Template Match)",
        "card_orders": "Ordini Creati",
        "card_total_silver": "Totale Silver Piazzato",
        "card_avg_price": "Prezzo Medio Ordine",
        "card_time_active": "Tempo Attivo",
        "info_config_loaded": "✅ Configurazione caricata.",
        "info_config_saved": "💾 Configurazione salvata.",
        "info_no_config": "ℹ️ Creata configurazione predefinita.",
        "log_ready": "🎯 AutoMarketSeller Pro Pronto.",
        "log_cal_start": "🔧 Calibrazione avviata. Segui le istruzioni a schermo.",
        "log_cal_hint": "ℹ️ Premi 'Esc' per annullare la calibrazione.",
        "log_cal_done": "✅ Calibrazione completata! Salvata in auto_config.json.",
        "log_cal_cancel": "❌ Calibrazione annullata.",
        "log_main_start": "🚀 Ciclo di vendita avviato (F4 ferma, F5 salta).",
        "log_main_stop": "🛑 Ciclo di vendita fermato dall'utente (F4).",
        "log_cycle_skip": "⏩ Oggetto corrente saltato dall'utente (F5).",
        "log_test_price": "Test 'Prezzo': {:,}",
        "log_test_price_fail": "❌ Test 'Prezzo': Riconoscimento OCR fallito.",
        "log_test_avg_price": "Test 'Prezzo Medio': {:,}",
        "log_test_avg_price_fail": "❌ Test 'Prezzo Medio': Riconoscimento OCR fallito.",
        "cal_window_title": "Modalità Calibrazione",
        "cal_step_info": "[Passo {}/{}]",
        "cal_instruction_point": "{}\nFai clic con il TASTO DESTRO su:\n'{}'",
        "cal_instruction_area": "{}\nTieni premuto MAIUSC e trascina per selezionare:\n'{}'\n\n(Rilascia e fai clic con il TASTO DESTRO per confermare)",
        "main_num1_ok": "Prezzo Minimo Ordine: {:,} Silver",
        "main_num1_fail": "⚠️ Impossibile leggere il prezzo minimo.",
        "main_num2_ok": "Prezzo Medio di Mercato: {:,} Silver",
        "main_num2_fail": "❌ Impossibile leggere il prezzo medio. Salto l'oggetto.",
        "main_value_entered": "✅ Ordine inserito a: {:,} Silver (Strategia: {})",
        "main_failsafe": "⚠️ PyAutoGUI Failsafe attivato (cursore all'angolo dello schermo).",
        "main_critical_error": "Errore critico nel ciclo: {}",
        "tesseract_configured": "✅ Tesseract configurato su: {}",
        "export_success": "✅ Statistiche esportate in:\n{}",
        "log_template_found": "✅ Template rilevato per '{}': a ({}, {}) [Confidenza: {:.0f}%]",
        "log_template_not_found": "⚠️ Template per '{}' non trovato a schermo. Uso coordinate salvate.",
        "log_template_saved": "📸 Template catturato e salvato per '{}'",
        "region_map": {
            "sell_button": "Pulsante Tab 'Vendi'",
            "order_button": "Pulsante 'Ordine di vendita'",
            "price_input": "Campo input 'Prezzo'",
            "submit_button": "Pulsante 'Crea ordine'",
            "price_value": "Area 'Prezzo Attuale'",
            "average_price": "Area 'Prezzo Medio'",
        },
    },
}


# --- BEZIER MOUSE CURVES & HUMANIZED INPUT ---
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
        t_raw = i / (num_points - 1)
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
    """Types text with natural human keystroke intervals."""
    for ch in text:
        pyautogui.write(ch)
        if enabled:
            time.sleep(get_gaussian_delay(0.025, 0.065))


# --- SESSION STATISTICS TRACKER ---
class SessionStats:
    def __init__(self):
        self.start_time = time.time()
        self.total_orders = 0
        self.total_silver = 0
        self.records = []
        self.lock = threading.Lock()

    def record_sale(self, price: int, strategy: str = "normal", reason: str = "ok", diff_percent: float = 0.0, item_name: str = "Item"):
        with self.lock:
            self.total_orders += 1
            self.total_silver += price
            self.records.append({
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "item": item_name,
                "price": price,
                "strategy": strategy,
                "reason": reason,
                "diff_percent": round(diff_percent, 2),
            })

    @property
    def average_price(self) -> int:
        with self.lock:
            return int(self.total_silver / self.total_orders) if self.total_orders > 0 else 0

    @property
    def elapsed_formatted(self) -> str:
        elapsed = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def reset(self):
        with self.lock:
            self.start_time = time.time()
            self.total_orders = 0
            self.total_silver = 0
            self.records.clear()

    def export_csv(self, file_path: str):
        with self.lock:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["timestamp", "item", "price", "strategy", "reason", "diff_percent"]
                )
                writer.writeheader()
                writer.writerows(self.records)


# --- PRICING ENGINE ---
def calculate_sell_price(
    number1: int | None,
    number2: int | None,
    fallback_ratio: float = 0.90,
    max_diff_percent: float = 30.0,
    strategy: str = "percentage",
    floor_price: int = 0,
) -> tuple[int, str, float]:
    """
    Intelligent pricing logic supporting Undercut-1, Percentage, and Tiered pricing.
    """
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

    # Anomaly protection: if lowest sell order is severely undercut / troll price
    if diff_percent > max_diff_percent and number1 < number2 * (1.0 - max_diff_percent / 100.0):
        raw_price = int(round(number2 * fallback_ratio))
        price = max(1, raw_price, floor_price)
        return (price, "diff_protected", diff_percent)

    # Normal calculations based on selected strategy
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
    merged = default_cfg.copy()
    for k, v in user_cfg.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = deep_merge_config(merged[k], v)
        else:
            merged[k] = v
    return merged


# --- NUMBER PARSER ---
def parse_albion_number(text: str) -> int | None:
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


# --- TEMPLATE MATCHER (OPENCV) ---
class TemplateMatcher:
    @staticmethod
    def find_template_in_image(
        image_bgr: np.ndarray, template_path: str, threshold: float = 0.75
    ) -> tuple[tuple[int, int] | None, float]:
        if not os.path.isfile(template_path) or image_bgr is None:
            return None, 0.0
        try:
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                return None, 0.0

            h, w = template.shape[:2]
            img_h, img_w = image_bgr.shape[:2]
            if h > img_h or w > img_w:
                return None, 0.0

            res = cv2.matchTemplate(image_bgr, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val >= threshold:
                center_x = int(max_loc[0] + w // 2)
                center_y = int(max_loc[1] + h // 2)
                return (center_x, center_y), float(max_val)
            return None, float(max_val)
        except Exception:
            return None, 0.0

    @classmethod
    def match_template_on_screen(
        cls, template_path: str, threshold: float = 0.75
    ) -> tuple[tuple[int, int] | None, float]:
        try:
            screen = np.array(ImageGrab.grab())
            screen_bgr = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
            return cls.find_template_in_image(screen_bgr, template_path, threshold=threshold)
        except Exception:
            return None, 0.0


# --- APPLICATION CLASS ---
class AutoMarketSeller:
    def __init__(self, root):
        self.root = root
        self.calibration_active = False
        self.main_loop_running = False
        self.drag_start_point = None
        self.current_drag_box = None
        self.is_dragging = False
        self.calibration_step = 0
        self.calibration_regions = []

        self.main_loop_thread = None
        self.stop_worker_event = threading.Event()
        self.skip_iteration_event = threading.Event()
        self.state_lock = threading.Lock()

        self.stats = SessionStats()
        self.log_queue = []
        self.log_lock = threading.Lock()

        self.selection_overlay = None
        self.selection_canvas = None
        self.instruction_window = None
        self.instruction_label = None

        self.CONFIG_FILE = os.path.join(BASE_DIR, "auto_config.json")
        self.screen_width, self.screen_height = pyautogui.size()
        self.config = self._get_default_config()
        self.lang = self.config.get("language", "it")
        self.strings = STRINGS.get(self.lang, STRINGS["en"])
        self.load_config()
        self.lang = self.config.get("language", "it")
        self.strings = STRINGS.get(self.lang, STRINGS["en"])

        self.setup_gui()
        self.update_gui_from_config()

        self.mouse_listener = None
        self.setup_hotkeys()
        self.start_input_listeners()

        self.root.after(200, self.update_log_area)
        self.root.after(1000, self.update_dashboard_stats)
        self.log_message("INFO", self.strings["log_ready"])

    def _safe_gui_call(self, func, *args, **kwargs):
        try:
            self.root.after(0, lambda: func(*args, **kwargs))
        except Exception:
            pass

    def _get_default_config(self):
        return {
            "language": "it",
            "tesseract_path": "",
            "strategy": "undercut_1",  # "undercut_1", "percentage", "tiered"
            "floor_price": 0,
            "human_mouse": True,
            "human_typing": True,
            "auto_template": True,
            "regions": {
                "sell_button": {"x": 0.0, "y": 0.0},
                "order_button": {"x": 0.0, "y": 0.0},
                "price_input": {"x": 0.0, "y": 0.0},
                "submit_button": {"x": 0.0, "y": 0.0},
                "price_value": {"x1": 0.0, "y1": 0.0, "x2": 0.0, "y2": 0.0},
                "average_price": {"x1": 0.0, "y1": 0.0, "x2": 0.0, "y2": 0.0},
            },
            "logic": {
                "fallback_ratio": 0.90,
                "max_difference_percent": 30,
                "robust_attempts": 10,
                "min_majority_count": 3,
            },
            "ocr": {
                "whitelist_digits": "0123456789.,MTKmtk",
            },
            "sleep": {
                "between_clicks": {"min": 0.04, "max": 0.07},
                "after_recognition": {"min": 0.04, "max": 0.07},
                "before_input": {"min": 0.04, "max": 0.07},
                "after_input": {"min": 0.14, "max": 0.18},
                "between_cycles": {"min": 0.4, "max": 0.6},
                "robust_recognition": {"min": 0.02, "max": 0.03},
            },
        }

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                self.config = deep_merge_config(self.config, loaded_config)
                self.log_message("CONFIG", self.strings["info_config_loaded"])
            except Exception as e:
                self.log_message("ERROR", f"Config load error: {e}")
        else:
            self.log_message("INFO", self.strings["info_no_config"])
            self.save_config()

    def save_config(self):
        try:
            self.update_config_from_gui()
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            self.log_message("CONFIG", self.strings["info_config_saved"])
        except Exception as e:
            self.log_message("ERROR", f"Config save error: {e}")

    def set_language(self, lang_code: str, save: bool = True):
        self.lang = lang_code
        self.strings = STRINGS.get(lang_code, STRINGS["en"])
        self.config["language"] = lang_code
        if save:
            self.save_config()

        for widget in self.root.winfo_children():
            widget.destroy()

        self.setup_gui()
        self.update_gui_from_config()
        self.update_dashboard_stats()

    # --- MODERN GUI SETUP ---
    def setup_gui(self):
        if USE_CUSTOMTKINTER:
            self._setup_customtkinter_gui()
        else:
            self._setup_standard_gui()

    def _setup_customtkinter_gui(self):
        self.root.title(self.strings["app_title"])
        self.root.geometry("880x660")
        self.root.minsize(800, 580)
        self.root.attributes("-topmost", True)

        # Header Frame (Title + Language Selector)
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(fill="x", padx=12, pady=(10, 0))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text=self.strings["app_title"],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#3498db",
        )
        title_lbl.pack(side="left", padx=5)

        current_lang_text = "🇮🇹 Italiano" if self.lang == "it" else "🇬🇧 English"
        self.lang_menu = ctk.CTkOptionMenu(
            header_frame,
            values=["🇮🇹 Italiano", "🇬🇧 English"],
            command=self._on_language_select,
            width=130,
            height=28,
        )
        self.lang_menu.set(current_lang_text)
        self.lang_menu.pack(side="right", padx=5)

        # Tabview
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=12, pady=(5, 12))

        tab_dash = self.tabview.add(self.strings["tab_dashboard"])
        tab_pricing = self.tabview.add(self.strings["tab_pricing"])
        tab_anti = self.tabview.add(self.strings["tab_anti_bot"])
        tab_log = self.tabview.add(self.strings["tab_logs"])

        # Top Control Bar in Dashboard
        top_ctrl_frame = ctk.CTkFrame(tab_dash)
        top_ctrl_frame.pack(fill="x", padx=10, pady=10)

        btn_text = self.strings["button_stop"] if self.main_loop_running else self.strings["button_start"]
        btn_color = "#e74c3c" if self.main_loop_running else "#2ecc71"
        btn_hover = "#c0392b" if self.main_loop_running else "#27ae60"

        self.start_stop_btn = ctk.CTkButton(
            top_ctrl_frame,
            text=btn_text,
            command=self.toggle_main_loop,
            fg_color=btn_color,
            hover_color=btn_hover,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
        )
        self.start_stop_btn.pack(side="left", padx=8, pady=8, expand=True, fill="x")

        self.skip_btn = ctk.CTkButton(
            top_ctrl_frame,
            text=self.strings["button_skip"],
            command=self.skip_current_item,
            fg_color="#f39c12",
            hover_color="#d68910",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
        )
        self.skip_btn.pack(side="left", padx=8, pady=8, expand=True, fill="x")

        self.cal_btn = ctk.CTkButton(
            top_ctrl_frame,
            text=self.strings["button_cal_full"],
            command=self.start_full_calibration,
            fg_color="#3498db",
            hover_color="#2980b9",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
        )
        self.cal_btn.pack(side="left", padx=8, pady=8, expand=True, fill="x")

        # Metric Cards Frame
        cards_frame = ctk.CTkFrame(tab_dash)
        cards_frame.pack(fill="x", padx=10, pady=10)
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Card 1: Orders
        c1 = ctk.CTkFrame(cards_frame, fg_color="#2c3e50")
        c1.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        ctk.CTkLabel(c1, text=self.strings["card_orders"], font=ctk.CTkFont(size=11)).pack(pady=(8, 2))
        self.lbl_orders_val = ctk.CTkLabel(c1, text="0", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1abc9c")
        self.lbl_orders_val.pack(pady=(0, 8))

        # Card 2: Total Silver
        c2 = ctk.CTkFrame(cards_frame, fg_color="#2c3e50")
        c2.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
        ctk.CTkLabel(c2, text=self.strings["card_total_silver"], font=ctk.CTkFont(size=11)).pack(pady=(8, 2))
        self.lbl_silver_val = ctk.CTkLabel(c2, text="0 Silver", font=ctk.CTkFont(size=16, weight="bold"), text_color="#f1c40f")
        self.lbl_silver_val.pack(pady=(0, 8))

        # Card 3: Avg Price
        c3 = ctk.CTkFrame(cards_frame, fg_color="#2c3e50")
        c3.grid(row=0, column=2, padx=6, pady=6, sticky="nsew")
        ctk.CTkLabel(c3, text=self.strings["card_avg_price"], font=ctk.CTkFont(size=11)).pack(pady=(8, 2))
        self.lbl_avg_val = ctk.CTkLabel(c3, text="0 Silver", font=ctk.CTkFont(size=16, weight="bold"), text_color="#3498db")
        self.lbl_avg_val.pack(pady=(0, 8))

        # Card 4: Active Time
        c4 = ctk.CTkFrame(cards_frame, fg_color="#2c3e50")
        c4.grid(row=0, column=3, padx=6, pady=6, sticky="nsew")
        ctk.CTkLabel(c4, text=self.strings["card_time_active"], font=ctk.CTkFont(size=11)).pack(pady=(8, 2))
        self.lbl_time_val = ctk.CTkLabel(c4, text="00:00:00", font=ctk.CTkFont(size=16, weight="bold"), text_color="#e67e22")
        self.lbl_time_val.pack(pady=(0, 8))

        # Quick Log Area in Dashboard
        ctk.CTkLabel(tab_dash, text="Live Log", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=12, pady=(8, 0))
        self.text_area = ctk.CTkTextbox(tab_dash, font=("Consolas", 11), wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=10, pady=8)

        # Bottom Actions Frame
        btm_frame = ctk.CTkFrame(tab_dash, fg_color="transparent")
        btm_frame.pack(fill="x", padx=10, pady=(0, 5))
        ctk.CTkButton(btm_frame, text=self.strings["button_export_csv"], command=self.export_stats_csv).pack(side="left", padx=5)
        ctk.CTkButton(btm_frame, text=self.strings["button_reset_stats"], command=self.reset_session_stats, fg_color="#7f8c8d").pack(side="left", padx=5)
        self.status_lbl = ctk.CTkLabel(btm_frame, text=self.strings["status_ready"], text_color="#2ecc71", font=ctk.CTkFont(weight="bold"))
        self.status_lbl.pack(side="right", padx=10)

        # TAB PRICING
        ctk.CTkLabel(tab_pricing, text=self.strings["label_strategy"], font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        self.strategy_var = ctk.StringVar(value=self.config.get("strategy", "undercut_1"))
        self.strategy_menu = ctk.CTkSegmentedButton(
            tab_pricing,
            values=[self.strings["strategy_undercut_1"], self.strings["strategy_percentage"], self.strings["strategy_tiered"]],
            command=self._on_strategy_change,
        )
        self.strategy_menu.pack(fill="x", padx=15, pady=(0, 15))

        # Discount Slider
        self.fallback_ratio_var = tk.DoubleVar()
        ctk.CTkLabel(tab_pricing, text=self.strings["label_fallback_ratio"]).pack(anchor="w", padx=15)
        self.fallback_lbl = ctk.CTkLabel(tab_pricing, text="", text_color="#1abc9c", font=ctk.CTkFont(weight="bold"))
        self.fallback_lbl.pack(anchor="w", padx=15)
        self.fallback_slider = ctk.CTkSlider(
            tab_pricing, from_=50, to=100, variable=self.fallback_ratio_var,
            command=lambda v: self.fallback_lbl.configure(text=f"{int(float(v))}%")
        )
        self.fallback_slider.pack(fill="x", padx=15, pady=(0, 15))

        # Max Diff Slider
        self.max_diff_var = tk.IntVar()
        ctk.CTkLabel(tab_pricing, text=self.strings["label_max_diff"]).pack(anchor="w", padx=15)
        self.max_diff_lbl = ctk.CTkLabel(tab_pricing, text="", text_color="#1abc9c", font=ctk.CTkFont(weight="bold"))
        self.max_diff_lbl.pack(anchor="w", padx=15)
        self.max_diff_slider = ctk.CTkSlider(
            tab_pricing, from_=5, to=100, variable=self.max_diff_var,
            command=lambda v: self.max_diff_lbl.configure(text=f"{int(float(v))}%")
        )
        self.max_diff_slider.pack(fill="x", padx=15, pady=(0, 15))

        # Floor Price Input
        ctk.CTkLabel(tab_pricing, text=self.strings["label_floor_price"]).pack(anchor="w", padx=15)
        self.floor_price_entry = ctk.CTkEntry(tab_pricing, placeholder_text="0")
        self.floor_price_entry.pack(anchor="w", padx=15, pady=(0, 15), fill="x")

        # Save Button in Pricing
        ctk.CTkButton(tab_pricing, text=self.strings["button_save_config"], command=self.save_config).pack(anchor="e", padx=15, pady=10)

        # TAB ANTI-BOT
        ctk.CTkLabel(tab_anti, text="Humanized Input Controls", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        self.human_mouse_var = ctk.BooleanVar(value=self.config.get("human_mouse", True))
        self.switch_mouse = ctk.CTkSwitch(tab_anti, text=self.strings["switch_human_mouse"], variable=self.human_mouse_var)
        self.switch_mouse.pack(anchor="w", padx=15, pady=8)

        self.human_typing_var = ctk.BooleanVar(value=self.config.get("human_typing", True))
        self.switch_typing = ctk.CTkSwitch(tab_anti, text=self.strings["switch_human_typing"], variable=self.human_typing_var)
        self.switch_typing.pack(anchor="w", padx=15, pady=8)

        self.auto_template_var = ctk.BooleanVar(value=self.config.get("auto_template", True))
        self.switch_template = ctk.CTkSwitch(tab_anti, text=self.strings["switch_auto_template"], variable=self.auto_template_var)
        self.switch_template.pack(anchor="w", padx=15, pady=8)

        ctk.CTkLabel(tab_anti, text="Computer Vision & OpenCV", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(20, 10))
        buttons_subframe = ctk.CTkFrame(tab_anti, fg_color="transparent")
        buttons_subframe.pack(anchor="w", padx=15, pady=5, fill="x")
        ctk.CTkButton(buttons_subframe, text=self.strings["button_test_templates"], command=self.test_all_templates, fg_color="#8e44ad", hover_color="#732d91").pack(side="left", padx=(0, 10))
        ctk.CTkButton(buttons_subframe, text=self.strings["button_tesseract"], command=self.prompt_select_tesseract).pack(side="left")

        # TAB LOGS (Full view)
        self.full_log_text = ctk.CTkTextbox(tab_log, font=("Consolas", 11), wrap="word")
        self.full_log_text.pack(fill="both", expand=True, padx=10, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_standard_gui(self):
        self.root.title(self.strings["app_title"])
        self.root.geometry("780x580")
        self.fallback_ratio_var = tk.DoubleVar()
        self.max_diff_var = tk.IntVar()
        self.strategy_var = tk.StringVar(value="undercut_1")

    def _on_language_select(self, chosen: str):
        lang = "it" if "Italiano" in chosen else "en"
        if lang != self.lang:
            self.set_language(lang, save=True)

    def _on_strategy_change(self, val):
        if val == self.strings["strategy_undercut_1"]:
            self.config["strategy"] = "undercut_1"
        elif val == self.strings["strategy_tiered"]:
            self.config["strategy"] = "tiered"
        else:
            self.config["strategy"] = "percentage"

    def update_gui_from_config(self):
        try:
            self.fallback_ratio_var.set(self.config["logic"]["fallback_ratio"] * 100)
            self.max_diff_var.set(self.config["logic"]["max_difference_percent"])
            self.fallback_lbl.configure(text=f"{self.fallback_ratio_var.get():.0f}%")
            self.max_diff_lbl.configure(text=f"{self.max_diff_var.get()}%")

            strat = self.config.get("strategy", "undercut_1")
            if strat == "undercut_1":
                self.strategy_menu.set(self.strings["strategy_undercut_1"])
            elif strat == "tiered":
                self.strategy_menu.set(self.strings["strategy_tiered"])
            else:
                self.strategy_menu.set(self.strings["strategy_percentage"])

            if hasattr(self, "floor_price_entry"):
                self.floor_price_entry.delete(0, tk.END)
                self.floor_price_entry.insert(0, str(self.config.get("floor_price", 0)))
        except Exception:
            pass

    def update_config_from_gui(self):
        try:
            self.config["logic"]["fallback_ratio"] = self.fallback_ratio_var.get() / 100.0
            self.config["logic"]["max_difference_percent"] = self.max_diff_var.get()
            if hasattr(self, "human_mouse_var"):
                self.config["human_mouse"] = self.human_mouse_var.get()
            if hasattr(self, "human_typing_var"):
                self.config["human_typing"] = self.human_typing_var.get()
            if hasattr(self, "auto_template_var"):
                self.config["auto_template"] = self.auto_template_var.get()
            if hasattr(self, "floor_price_entry"):
                try:
                    self.config["floor_price"] = max(0, int(self.floor_price_entry.get().strip()))
                except Exception:
                    self.config["floor_price"] = 0
        except Exception:
            pass

    def update_status_label(self, text_key: str, color: str):
        def _update():
            if hasattr(self, "status_lbl"):
                self.status_lbl.configure(text=self.strings.get(text_key, text_key), text_color=color)
        self._safe_gui_call(_update)

    def update_dashboard_stats(self):
        def _update():
            if hasattr(self, "lbl_orders_val"):
                self.lbl_orders_val.configure(text=str(self.stats.total_orders))
                silver_text = f"{self.stats.total_silver:,} Silver" if self.stats.total_silver < 1_000_000 else f"{self.stats.total_silver / 1_000_000:.2f}M Silver"
                self.lbl_silver_val.configure(text=silver_text)
                avg_text = f"{self.stats.average_price:,} Silver"
                self.lbl_avg_val.configure(text=avg_text)
                self.lbl_time_val.configure(text=self.stats.elapsed_formatted)
        self._safe_gui_call(_update)
        self.root.after(1000, self.update_dashboard_stats)

    def export_stats_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv"), ("All Files", "*.*")],
            initialfile=f"albion_market_session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        )
        if path:
            self.stats.export_csv(path)
            messagebox.showinfo("Export Success", self.strings["export_success"].format(path))

    def reset_session_stats(self):
        self.stats.reset()
        self.update_dashboard_stats()

    def prompt_select_tesseract(self):
        path = filedialog.askopenfilename(
            title="Select tesseract.exe",
            filetypes=[("Tesseract Executable", "tesseract.exe"), ("All Executables", "*.exe")],
        )
        if path and os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            self.config["tesseract_path"] = path
            self.save_config()
            self.log_message("CONFIG", self.strings["tesseract_configured"].format(path))

    def test_all_templates(self):
        threading.Thread(target=self._run_test_all_templates, daemon=True).start()

    def _run_test_all_templates(self):
        self.log_message("TEMPLATE", "🔍 Scanning screen for UI buttons via OpenCV...")
        found_any = False
        for region_key, region_label in self.strings["region_map"].items():
            tpl_path = os.path.join(TEMPLATES_DIR, f"{region_key}.png")
            if not os.path.isfile(tpl_path):
                self.log_message("TEMPLATE", f"ℹ️ '{region_label}': No saved template found in templates/ folder.")
                continue
            center, conf = TemplateMatcher.match_template_on_screen(tpl_path, threshold=0.75)
            if center is not None:
                found_any = True
                self.log_message("TEMPLATE", self.strings["log_template_found"].format(
                    region_label, center[0], center[1], conf * 100
                ))
            else:
                self.log_message("TEMPLATE", self.strings["log_template_not_found"].format(region_label))
        if not found_any:
            self.log_message("HINT", "ℹ️ Run Calibration (F1) to auto-capture button templates!")

    def log_message(self, level, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {level.upper()}: {message}"
        with self.log_lock:
            self.log_queue.append(entry)

    def update_log_area(self):
        entries = []
        with self.log_lock:
            while self.log_queue:
                entries.append(self.log_queue.pop(0))
        if entries:
            try:
                for item in entries:
                    if hasattr(self, "text_area"):
                        self.text_area.insert(tk.END, item + "\n")
                        self.text_area.see(tk.END)
                    if hasattr(self, "full_log_text"):
                        self.full_log_text.insert(tk.END, item + "\n")
                        self.full_log_text.see(tk.END)
            except Exception:
                pass
        self.root.after(200, self.update_log_area)

    # --- CALIBRATION ---
    def start_full_calibration(self):
        self._start_calibration_process(list(self.strings["region_map"].keys()))

    def _start_calibration_process(self, region_list):
        with self.state_lock:
            if self.calibration_active or self.main_loop_running:
                return
            self.calibration_active = True
            self.calibration_step = 0
            self.calibration_regions = region_list
            self.drag_start_point = None
            self.current_drag_box = None
            self.is_dragging = False

        self.update_status_label("status_calibrating", "#e67e22")
        self.log_message("CALIBRATE", self.strings["log_cal_start"])
        self.log_message("HINT", self.strings["log_cal_hint"])
        self._safe_gui_call(self.create_instruction_window)

    def create_instruction_window(self):
        if self.instruction_window:
            try:
                self.instruction_window.destroy()
            except Exception:
                pass
        self.instruction_window = tk.Toplevel(self.root)
        self.instruction_window.title(self.strings["cal_window_title"])
        self.instruction_window.geometry("520x160")
        self.instruction_window.attributes("-topmost", True)
        self.instruction_window.configure(bg="black")
        self.instruction_label = tk.Label(
            self.instruction_window,
            text="",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="black",
            wraplength=490,
        )
        self.instruction_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.update_instruction_window()

    def update_instruction_window(self):
        if not self.calibration_active or self.calibration_step >= len(self.calibration_regions):
            if self.instruction_window:
                try:
                    self.instruction_window.destroy()
                except Exception:
                    pass
                self.instruction_window = None
            return

        current_region_key = self.calibration_regions[self.calibration_step]
        region_name = self.strings["region_map"][current_region_key]
        is_area = "1" in list(self.config["regions"][current_region_key].keys())[0]

        step_info = self.strings["cal_step_info"].format(self.calibration_step + 1, len(self.calibration_regions))
        instruction_template = self.strings["cal_instruction_area" if is_area else "cal_instruction_point"]
        instruction_text = instruction_template.format(step_info, region_name)

        if self.instruction_label:
            try:
                self.instruction_label.config(text=instruction_text)
            except Exception:
                pass

    def handle_calibration_click(self, x, y, button, pressed):
        if not self.calibration_active or not pressed or button != mouse.Button.right:
            return

        self._safe_gui_call(self._destroy_selection_overlay)
        current_region = self.calibration_regions[self.calibration_step]
        is_area = "1" in list(self.config["regions"][current_region].keys())[0]

        if is_area:
            if not self.drag_start_point or not self.current_drag_box:
                return
            x1, y1 = self.drag_start_point
            x2, y2 = self.current_drag_box
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            rel_x1, rel_y1 = (x1 / self.screen_width * 100), (y1 / self.screen_height * 100)
            rel_x2, rel_y2 = (x2 / self.screen_width * 100), (y2 / self.screen_height * 100)
            self.config["regions"][current_region] = {"x1": rel_x1, "y1": rel_y1, "x2": rel_x2, "y2": rel_y2}

            # Auto-save template crop
            try:
                crop_img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                tpl_path = os.path.join(TEMPLATES_DIR, f"{current_region}.png")
                crop_img.save(tpl_path)
                self.log_message("TEMPLATE", self.strings["log_template_saved"].format(self.strings["region_map"][current_region]))
            except Exception:
                pass
        else:
            rel_x, rel_y = (x / self.screen_width * 100), (y / self.screen_height * 100)
            self.config["regions"][current_region] = {"x": rel_x, "y": rel_y}

            # Auto-save button template snippet (70x36 area around click)
            try:
                bx1 = max(0, int(x - 35))
                by1 = max(0, int(y - 18))
                bx2 = min(self.screen_width, int(x + 35))
                by2 = min(self.screen_height, int(y + 18))
                crop_img = ImageGrab.grab(bbox=(bx1, by1, bx2, by2))
                tpl_path = os.path.join(TEMPLATES_DIR, f"{current_region}.png")
                crop_img.save(tpl_path)
                self.log_message("TEMPLATE", self.strings["log_template_saved"].format(self.strings["region_map"][current_region]))
            except Exception:
                pass

        self.drag_start_point = None
        self.current_drag_box = None
        self.is_dragging = False
        self.calibration_step += 1

        if self.calibration_step >= len(self.calibration_regions):
            self._safe_gui_call(lambda: self.finish_calibration(cancelled=False))
        else:
            self._safe_gui_call(self.update_instruction_window)

    def finish_calibration(self, cancelled=False):
        if not self.calibration_active:
            return
        self.calibration_active = False
        self.drag_start_point = None
        self.current_drag_box = None
        self.is_dragging = False

        self._destroy_selection_overlay()
        if self.instruction_window:
            try:
                self.instruction_window.destroy()
            except Exception:
                pass
            self.instruction_window = None

        self.update_status_label("status_ready", "#2ecc71")
        if cancelled:
            self.log_message("CALIBRATE", self.strings["log_cal_cancel"])
        else:
            self.save_config()
            self.log_message("CALIBRATE", self.strings["log_cal_done"])

    def handle_esc_key(self):
        if self.calibration_active:
            self._safe_gui_call(lambda: self.finish_calibration(cancelled=True))

    def setup_hotkeys(self):
        try:
            keyboard.add_hotkey("f1", lambda: self._safe_gui_call(self.start_full_calibration))
            keyboard.add_hotkey("f2", lambda: threading.Thread(target=self.test_price_recognition, daemon=True).start())
            keyboard.add_hotkey("f3", lambda: threading.Thread(target=self.test_average_price_recognition, daemon=True).start())
            keyboard.add_hotkey("f4", lambda: self._safe_gui_call(self.toggle_main_loop))
            keyboard.add_hotkey("f5", self.skip_current_item)
            keyboard.add_hotkey("esc", self.handle_esc_key)
        except Exception as e:
            self.log_message("ERROR", f"Hotkey setup error: {e}")

    def skip_current_item(self):
        if self.main_loop_running:
            self.skip_iteration_event.set()
            self.log_message("SKIP", self.strings["log_cycle_skip"])

    def test_price_recognition(self):
        if self.main_loop_running or self.calibration_active:
            return
        number = self._recognize_number("price_value")
        if number is not None:
            self.log_message("TEST", self.strings["log_test_price"].format(number))
        else:
            self.log_message("TEST", self.strings["log_test_price_fail"])

    def test_average_price_recognition(self):
        if self.main_loop_running or self.calibration_active:
            return
        number = self._recognize_number("average_price")
        if number is not None:
            self.log_message("TEST", self.strings["log_test_avg_price"].format(number))
        else:
            self.log_message("TEST", self.strings["log_test_avg_price_fail"])

    def start_input_listeners(self):
        def on_move(x, y):
            if not self.calibration_active:
                return
            if self.calibration_step >= len(self.calibration_regions):
                return
            current_region_key = self.calibration_regions[self.calibration_step]
            is_area = "1" in list(self.config["regions"][current_region_key].keys())[0]

            if is_area and keyboard.is_pressed("shift"):
                if self.drag_start_point is None:
                    self.drag_start_point = (x, y)
                    self.is_dragging = True
                    self._safe_gui_call(self._create_selection_overlay)
                self.current_drag_box = (x, y)
                self._safe_gui_call(self._update_selection_rectangle)
            elif self.is_dragging and not keyboard.is_pressed("shift"):
                self.is_dragging = False

        self.mouse_listener = mouse.Listener(on_click=self.handle_calibration_click, on_move=on_move)
        self.mouse_listener.daemon = True
        self.mouse_listener.start()

    def _create_selection_overlay(self):
        if self.selection_overlay:
            return
        self.selection_overlay = tk.Toplevel(self.root)
        self.selection_overlay.attributes("-alpha", 0.35)
        self.selection_overlay.attributes("-topmost", True)
        self.selection_overlay.overrideredirect(True)
        self.selection_overlay.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.selection_canvas = tk.Canvas(self.selection_overlay, bg="white", highlightthickness=0)
        self.selection_canvas.pack(fill=tk.BOTH, expand=True)
        self.selection_overlay.wm_attributes("-transparentcolor", "white")

    def _update_selection_rectangle(self):
        if not self.selection_canvas or not self.drag_start_point or not self.current_drag_box:
            return
        self.selection_canvas.delete("selection_rect")
        x1, y1 = self.drag_start_point
        x2, y2 = self.current_drag_box
        self.selection_canvas.create_rectangle(
            x1, y1, x2, y2, fill="#ff3333", outline="#ff0000", width=2, tag="selection_rect"
        )

    def _destroy_selection_overlay(self):
        if self.selection_overlay:
            try:
                self.selection_overlay.destroy()
            except Exception:
                pass
            self.selection_overlay = None
            self.selection_canvas = None

    def toggle_main_loop(self):
        with self.state_lock:
            if self.calibration_active:
                return

            if self.main_loop_running:
                self.stop_worker_event.set()
                self.log_message("STOP", self.strings["log_main_stop"])
            else:
                uncalibrated = [
                    k for k, v in self.config["regions"].items()
                    if ("x" in v and v["x"] == 0 and v["y"] == 0) or
                       ("x1" in v and v["x1"] == 0 and v["x2"] == 0)
                ]
                if uncalibrated:
                    messagebox.showwarning("Calibration Needed", "Please calibrate the interface (F1) before starting the cycle!")
                    return

                self.main_loop_running = True
                self.stop_worker_event.clear()
                self.skip_iteration_event.clear()
                self.main_loop_thread = threading.Thread(target=self.run_main_loop, daemon=True)
                self.main_loop_thread.start()
                self.log_message("START", self.strings["log_main_start"])
                if hasattr(self, "start_stop_btn"):
                    self.start_stop_btn.configure(text=self.strings["button_stop"], fg_color="#e74c3c", hover_color="#c0392b")
                self.update_status_label("status_running", "#2ecc71")

    def interruptible_sleep(self, duration):
        end_time = time.time() + duration
        while time.time() < end_time:
            if self.stop_worker_event.is_set() or self.skip_iteration_event.is_set():
                return True
            time.sleep(0.01)
        return False

    def _get_absolute_coords(self, region_name):
        region = self.config["regions"][region_name]
        if "x2" in region:
            x1 = int(self.screen_width * region["x1"] / 100.0)
            y1 = int(self.screen_height * region["y1"] / 100.0)
            x2 = int(self.screen_width * region["x2"] / 100.0)
            y2 = int(self.screen_height * region["y2"] / 100.0)
            return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        else:
            return (
                int(self.screen_width * region["x"] / 100.0),
                int(self.screen_height * region["y"] / 100.0),
            )

    def _resolve_target_coords(self, region_name: str) -> tuple[int, int]:
        """Resolves target coords using Template Matching if enabled, otherwise relative coords."""
        if self.config.get("auto_template", True):
            tpl_path = os.path.join(TEMPLATES_DIR, f"{region_name}.png")
            if os.path.isfile(tpl_path):
                center, conf = TemplateMatcher.match_template_on_screen(tpl_path, threshold=0.75)
                if center is not None:
                    return center

        coords = self._get_absolute_coords(region_name)
        if len(coords) == 4:
            return ((coords[0] + coords[2]) // 2, (coords[1] + coords[3]) // 2)
        return coords

    def _click_target(self, region_name):
        x, y = self._resolve_target_coords(region_name)
        human_enabled = self.config.get("human_mouse", True)
        human_move_to(x, y, enabled=human_enabled)
        pyautogui.click(x, y)

    def _preprocess_variants(self, pil_image):
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
        variants.append(thresh_adapt)
        variants.append(cv2.bitwise_not(thresh_adapt))

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(resized)
        _, thresh_otsu = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(thresh_otsu)
        variants.append(cv2.bitwise_not(thresh_otsu))

        return [Image.fromarray(v) for v in variants]

    def _recognize_number(self, region_name):
        return self._robust_recognize_number(region_name)

    def _robust_recognize_number(self, region_name):
        results = []
        attempts = self.config["logic"]["robust_attempts"]
        psm_configs = ["--psm 7", "--psm 8", "--psm 6"]
        whitelist = self.config["ocr"]["whitelist_digits"]

        try:
            x1, y1, x2, y2 = self._get_absolute_coords(region_name)
            if x2 <= x1 or y2 <= y1:
                return None
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            variants = self._preprocess_variants(img)
        except Exception as e:
            self.log_message("ERROR", f"Screen grab error: {e}")
            return None

        for i in range(attempts):
            if self.stop_worker_event.is_set() or self.skip_iteration_event.is_set():
                break

            processed_img = variants[i % len(variants)]
            psm = psm_configs[(i // len(variants)) % len(psm_configs)]
            tess_config = f"{psm} -c tessedit_char_whitelist={whitelist}"

            try:
                raw_text = pytesseract.image_to_string(processed_img, config=tess_config).strip()
                parsed = parse_albion_number(raw_text)
                if parsed is not None:
                    results.append(parsed)
            except Exception:
                pass

            sleep_time = get_gaussian_delay(0.015, 0.035)
            if self.interruptible_sleep(sleep_time):
                break

        if not results:
            return None

        counter = Counter(results)
        most_common, count = counter.most_common(1)[0]
        min_count = self.config["logic"]["min_majority_count"]

        if count >= min_count or (len(results) >= 2 and count == len(results)):
            return most_common
        return most_common if count >= 2 else None

    # --- MAIN AUTOMATION LOOP ---
    def run_main_loop(self):
        while not self.stop_worker_event.is_set():
            self.skip_iteration_event.clear()
            try:
                # 1. Click Sell Tab
                self._click_target("sell_button")
                if self.interruptible_sleep(get_gaussian_delay(0.05, 0.08)):
                    if self.stop_worker_event.is_set():
                        break
                    continue

                # 2. Click Sell Order Tab
                self._click_target("order_button")
                if self.interruptible_sleep(get_gaussian_delay(0.05, 0.08)):
                    if self.stop_worker_event.is_set():
                        break
                    continue

                # 3. Recognize Current Lowest Price
                number1 = self._robust_recognize_number("price_value")
                if self.stop_worker_event.is_set():
                    break
                if self.skip_iteration_event.is_set():
                    continue

                if number1:
                    self.log_message("INFO", self.strings["main_num1_ok"].format(number1))
                else:
                    self.log_message("WARNING", self.strings["main_num1_fail"])

                # 4. Recognize Average Market Price
                number2 = self._robust_recognize_number("average_price")
                if self.stop_worker_event.is_set():
                    break
                if self.skip_iteration_event.is_set():
                    continue

                if not number2 and not number1:
                    self.log_message("ERROR", self.strings["main_num2_fail"])
                    if self.interruptible_sleep(get_gaussian_delay(0.3, 0.5)):
                        if self.stop_worker_event.is_set():
                            break
                    continue

                if number2:
                    self.log_message("INFO", self.strings["main_num2_ok"].format(number2))

                # Strategy calculation
                strategy = self.config.get("strategy", "undercut_1")
                fallback_ratio = self.fallback_ratio_var.get() / 100.0
                max_diff_percent = float(self.max_diff_var.get())
                floor_price = self.config.get("floor_price", 0)

                result, reason, diff = calculate_sell_price(
                    number1,
                    number2,
                    fallback_ratio=fallback_ratio,
                    max_diff_percent=max_diff_percent,
                    strategy=strategy,
                    floor_price=floor_price,
                )

                if result <= 0:
                    result = 1

                # 5. Clear and Type New Price
                self._click_target("price_input")
                if self.interruptible_sleep(get_gaussian_delay(0.04, 0.07)):
                    if self.stop_worker_event.is_set():
                        break
                    continue

                # Clear previous input
                pyautogui.hotkey("ctrl", "a")
                pyautogui.press("backspace")
                time.sleep(0.03)

                # Type sanitized price
                human_typing_enabled = self.config.get("human_typing", True)
                human_type(str(result), enabled=human_typing_enabled)

                if self.interruptible_sleep(get_gaussian_delay(0.04, 0.08)):
                    if self.stop_worker_event.is_set():
                        break
                    continue

                # 6. Click Submit Order
                self._click_target("submit_button")
                if self.interruptible_sleep(get_gaussian_delay(0.12, 0.18)):
                    if self.stop_worker_event.is_set():
                        break
                    continue

                # Record statistics
                self.stats.record_sale(price=result, strategy=strategy, reason=reason, diff_percent=diff)
                self.log_message("ACTION", self.strings["main_value_entered"].format(result, strategy))

            except pyautogui.FailSafeException:
                self.log_message("WARNING", self.strings["main_failsafe"])
                break
            except Exception as e:
                self.log_message("ERROR", self.strings["main_critical_error"].format(e))

            if self.interruptible_sleep(get_gaussian_delay(0.4, 0.6)):
                if self.stop_worker_event.is_set():
                    break

        with self.state_lock:
            self.main_loop_running = False

        self._safe_gui_call(lambda: [
            self.start_stop_btn.configure(text=self.strings["button_start"], fg_color="#2ecc71", hover_color="#27ae60") if hasattr(self, "start_stop_btn") else None,
            self.update_status_label("status_ready", "#2ecc71"),
        ])

    def on_closing(self):
        with self.state_lock:
            self.stop_worker_event.set()
            self.skip_iteration_event.set()
            self.calibration_active = False
            self.main_loop_running = False

        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception:
                pass

        try:
            keyboard.unhook_all()
        except Exception:
            pass

        try:
            self.root.destroy()
        except Exception:
            pass

        sys.exit(0)


# --- TESSERACT DETECTION & PORTABLE BUNDLING ---
def detect_tesseract_binary(custom_config_path: str = "") -> str:
    meipass = getattr(sys, "_MEIPASS", "")
    candidate_paths = [
        # 1. PyInstaller bundled directory
        os.path.join(meipass, "tesseract", "tesseract.exe") if meipass else "",
        os.path.join(meipass, "tesseract.exe") if meipass else "",
        # 2. Project-local portable directory
        os.path.join(BASE_DIR, "tesseract", "tesseract.exe"),
        os.path.join(BASE_DIR, "tesseract-portable", "tesseract.exe"),
        os.path.join(BASE_DIR, "tesseract.exe"),
        # 3. User custom configured path
        custom_config_path,
        # 4. Standard Windows install paths
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


if __name__ == "__main__":
    cfg_file = os.path.join(BASE_DIR, "auto_config.json")
    saved_tesseract_path = ""
    if os.path.exists(cfg_file):
        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                c = json.load(f)
                saved_tesseract_path = c.get("tesseract_path", "")
        except Exception:
            pass

    tesseract_path = detect_tesseract_binary(saved_tesseract_path)
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    if USE_CUSTOMTKINTER:
        root = ctk.CTk()
    else:
        root = tk.Tk()

    app = AutoMarketSeller(root)
    root.mainloop()