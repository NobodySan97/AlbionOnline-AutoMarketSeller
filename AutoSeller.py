import ctypes
import datetime
import json
import os
import random
import re
import shutil
import sys
import threading
import time
from collections import Counter
import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox, scrolledtext

import cv2
import keyboard
import numpy as np
from PIL import Image, ImageGrab
import pyautogui
from pynput import mouse
import pytesseract

# --- WINDOWS DPI AWARENESS INITIALIZATION ---
if sys.platform == "win32":
    try:
        # Per-Monitor DPI Aware v2 (Windows 10 1703+)
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            # Per-Monitor DPI Aware (Windows 8.1+)
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                # System DPI Aware (Windows Vista+)
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

# PyAutoGUI settings
pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = True

# Script base directory for reliable configuration saving
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# MULTILINGUAL LOCALIZATION STRINGS
STRINGS = {
    "en": {
        "app_title": "🤖 Auto Market Seller v1.4",
        "log_title": "📋 Algorithm Work Log",
        "status_ready": "Status: Ready",
        "status_running": "Status: Running",
        "status_paused": "Status: Paused",
        "status_calibrating": "Status: Calibrating...",
        "author_label": "Author: NobodySan97",
        "resolution_label": "Resolution: {}x{}",
        "menu_file": "File",
        "menu_cal_full": "Start Full Calibration (F1)",
        "menu_cal_single": "Calibrate Element",
        "menu_save_config": "Save Configuration",
        "menu_select_tesseract": "Set Tesseract Path...",
        "menu_exit": "Exit",
        "menu_help": "Help",
        "menu_guide": "Guide",
        "menu_language": "Language",
        "controls_title": " Control Panel ",
        "logic_title": " Logic Settings ",
        "button_start": "▶ Start (F4)",
        "button_stop": "■ Stop (F4)",
        "label_fallback_ratio": "Discount Ratio (% of price):",
        "label_max_diff": "Maximum Price Difference (%):",
        "info_config_loaded": "✅ Configuration loaded from file.",
        "info_config_saved": "💾 Configuration saved.",
        "info_no_config": "ℹ️ Configuration file not found. Created with default values.",
        "error_load_config": "❌ Error loading configuration: {}",
        "error_save_config": "❌ Could not save configuration: {}",
        "log_ready": "🎯 Ready for use.",
        "log_cal_start": "🔧 Calibration mode started.",
        "log_cal_hint": "ℹ️ Follow instructions in the overlay window. Press 'Esc' to cancel.",
        "log_cal_done": "✅ Calibration complete! Configuration saved.",
        "log_cal_cancel": "❌ Calibration cancelled by user.",
        "log_cal_point_saved": "📍 {} saved: ({:.2f}%, {:.2f}%)",
        "log_cal_area_saved": "✅ {} saved: {:.2f}%, {:.2f}% -> {:.2f}%, {:.2f}%",
        "log_main_start": "🚀 Sales cycle started. Press F4 to stop.",
        "log_main_stop_user": "🛑 Sales cycle stopped by user (F4).",
        "log_cycle_skip_user": "⏩ Current item skipped by user (F5).",
        "log_test_price": "Test 'Price': {:,}",
        "log_test_price_fail": "❌ Test 'Price': Recognition failed.",
        "log_test_avg_price": "Test 'Average Price': {:,}",
        "log_test_avg_price_fail": "❌ Test 'Average Price': Recognition failed.",
        "cal_window_title": "Calibration Instructions",
        "cal_step_info": "[Step {}/{}]",
        "cal_instruction_point": "{}\nRIGHT-CLICK on:\n'{}'",
        "cal_instruction_area": "{}\nHold SHIFT and drag to select the area of:\n'{}'\n\n(Release and RIGHT-CLICK to confirm)",
        "ocr_robust_start": "🔍 Starting robust recognition ({} attempts)...",
        "ocr_robust_attempt": "OCR attempt {} [{}]: '{}' -> {}",
        "ocr_no_valid_results": "❌ All recognition attempts failed.",
        "ocr_majority_found": "✅ Consensus price found: {:,} (agreed {} times)",
        "ocr_majority_fail": "⚠️ Insufficient matches: {:,} ({} times), required ≥ {}",
        "main_num1_ok": "Current lowest price: {:,}",
        "main_num1_fail": "❌ Unable to recognize current price.",
        "main_num2_fail": "❌ Unable to recognize average price. Skipping iteration.",
        "main_num2_ok": "Average price: {:,}",
        "main_fallback": "→ Fallback: {:.0f}% of average price ({:,}) = {:,}",
        "main_fallback_num1": "→ Fallback: {:.0f}% of current price ({:,}) = {:,}",
        "main_diff_check": "⚠️ Current price differs >{}% from average ({:.1f}% diff). Undercut trap protected: using average price fallback.",
        "main_result_from_refined": "→ Protected result: {:.0f}% of average price = {:,}",
        "main_result_from_close": "→ Consistent prices ({:.1f}% diff). Result: {:.0f}% of lowest order = {:,}",
        "main_value_entered": "✅ Value entered: {:,}",
        "main_critical_error": "Critical error in the main loop: {}",
        "main_failsafe": "⚠️ PyAutoGUI Failsafe triggered (mouse moved to corner). Main loop stopped.",
        "tesseract_select_prompt": "Please locate tesseract.exe on your computer",
        "tesseract_configured": "✅ Tesseract configured at: {}",
        "help_text": (
            "Keyboard Shortcuts:\n"
            "• F1: Start Full Calibration\n"
            "• F2: Test Current Price Recognition\n"
            "• F3: Test Average Price Recognition\n"
            "• F4: Start / Stop Main Loop\n"
            "• F5: Skip Current Item / Iteration\n"
            "• Esc: Cancel Calibration (when calibrating)\n\n"
            "Calibration Steps:\n"
            "1. Click 'Sell' tab\n"
            "2. Click 'Sell Order' button\n"
            "3. Click 'Price' input box\n"
            "4. Click 'Create Order' button\n"
            "5. Select current price area (Shift + Drag, then Right-Click)\n"
            "6. Select average price area (Shift + Drag, then Right-Click)"
        ),
        "region_map": {
            "sell_button": "Sell Button",
            "order_button": "Sell Order Button",
            "price_input": "Price Input Field",
            "submit_button": "Create Order Button",
            "price_value": "Current Price Area",
            "average_price": "Average Price Area",
        },
    },
    "it": {
        "app_title": "🤖 Auto Market Seller v1.4",
        "log_title": "📋 Log di Lavoro dell'Algoritmo",
        "status_ready": "Stato: Pronto",
        "status_running": "Stato: In Esecuzione",
        "status_paused": "Stato: In Pausa",
        "status_calibrating": "Stato: Calibrazione...",
        "author_label": "Autore: NobodySan97",
        "resolution_label": "Risoluzione: {}x{}",
        "menu_file": "File",
        "menu_cal_full": "Avvia Calibrazione Completa (F1)",
        "menu_cal_single": "Calibra Elemento",
        "menu_save_config": "Salva Configurazione",
        "menu_select_tesseract": "Imposta Percorso Tesseract...",
        "menu_exit": "Esci",
        "menu_help": "Aiuto",
        "menu_guide": "Guida",
        "menu_language": "Lingua",
        "controls_title": " Pannello di Controllo ",
        "logic_title": " Impostazioni Logiche ",
        "button_start": "▶ Avvia (F4)",
        "button_stop": "■ Ferma (F4)",
        "label_fallback_ratio": "Rapporto di Sconto (% del prezzo):",
        "label_max_diff": "Differenza Massima Prezzi (%):",
        "info_config_loaded": "✅ Configurazione caricata dal file.",
        "info_config_saved": "💾 Configurazione salvata.",
        "info_no_config": "ℹ️ File di configurazione non trovato. Creato con i valori predefiniti.",
        "error_load_config": "❌ Errore nel caricamento della configurazione: {}",
        "error_save_config": "❌ Impossibile salvare la configurazione: {}",
        "log_ready": "🎯 Pronto per l'uso.",
        "log_cal_start": "🔧 Modalità di calibrazione avviata.",
        "log_cal_hint": "ℹ️ Segui le istruzioni nella finestra in sovrimpressione. Premi 'Esc' per annullare.",
        "log_cal_done": "✅ Calibrazione completata! Configurazione salvata.",
        "log_cal_cancel": "❌ Calibrazione annullata dall'utente.",
        "log_cal_point_saved": "📍 {} salvato: ({:.2f}%, {:.2f}%)",
        "log_cal_area_saved": "✅ {} salvata: {:.2f}%, {:.2f}% -> {:.2f}%, {:.2f}%",
        "log_main_start": "🚀 Ciclo di vendita avviato. Premi F4 per fermare.",
        "log_main_stop_user": "🛑 Ciclo di vendita fermato dall'utente (F4).",
        "log_cycle_skip_user": "⏩ Oggetto corrente saltato dall'utente (F5).",
        "log_test_price": "Test 'Prezzo': {:,}",
        "log_test_price_fail": "❌ Test 'Prezzo': Riconoscimento fallito.",
        "log_test_avg_price": "Test 'Prezzo Medio': {:,}",
        "log_test_avg_price_fail": "❌ Test 'Prezzo Medio': Riconoscimento fallito.",
        "cal_window_title": "Istruzioni di Calibrazione",
        "cal_step_info": "[Passo {}/{}]",
        "cal_instruction_point": "{}\nFai clic con il TASTO DESTRO su:\n'{}'",
        "cal_instruction_area": "{}\nTieni premuto MAIUSC e trascina per selezionare l'area di:\n'{}'\n\n(Rilascia e fai clic con il TASTO DESTRO per confermare)",
        "ocr_robust_start": "🔍 Avvio riconoscimento robusto ({} tentativi)...",
        "ocr_robust_attempt": "Tentativo OCR {} [{}]: '{}' -> {}",
        "ocr_no_valid_results": "❌ Tutti i tentativi di riconoscimento sono falliti.",
        "ocr_majority_found": "✅ Prezzo di consenso trovato: {:,} (confermato {} volte)",
        "ocr_majority_fail": "⚠️ Corrispondenze insufficienti: {:,} ({} volte), necessarie ≥ {}",
        "main_num1_ok": "Prezzo minimo attuale: {:,}",
        "main_num1_fail": "❌ Impossibile riconoscere il prezzo attuale.",
        "main_num2_fail": "❌ Impossibile riconoscere il prezzo medio. Salto l'iterazione.",
        "main_num2_ok": "Prezzo medio: {:,}",
        "main_fallback": "→ Fallback: {:.0f}% del prezzo medio ({:,}) = {:,}",
        "main_fallback_num1": "→ Fallback: {:.0f}% del prezzo attuale ({:,}) = {:,}",
        "main_diff_check": "⚠️ Il prezzo differisce >{}% dalla media ({:.1f}% diff). Protezione undercut attiva: uso fallback prezzo medio.",
        "main_result_from_refined": "→ Risultato protetto: {:.0f}% del prezzo medio = {:,}",
        "main_result_from_close": "→ Prezzi coerenti ({:.1f}% diff). Risultato: {:.0f}% del prezzo minimo = {:,}",
        "main_value_entered": "✅ Valore inserito: {:,}",
        "main_critical_error": "Errore critico nel ciclo principale: {}",
        "main_failsafe": "⚠️ PyAutoGUI Failsafe attivato (mouse spostato all'angolo dello schermo). Ciclo fermato.",
        "tesseract_select_prompt": "Seleziona il file tesseract.exe sul tuo computer",
        "tesseract_configured": "✅ Tesseract configurato su: {}",
        "help_text": (
            "Scorciatoie da tastiera:\n"
            "• F1: Avvia Calibrazione Completa\n"
            "• F2: Test Riconoscimento Prezzo Attuale\n"
            "• F3: Test Riconoscimento Prezzo Medio\n"
            "• F4: Avvia / Ferma Ciclo Principale\n"
            "• F5: Salta Oggetto / Iterazione Corrente\n"
            "• Esc: Annulla Calibrazione (durante la calibrazione)\n\n"
            "Passi di Calibrazione:\n"
            "1. Clicca sul pulsante 'Vendi'\n"
            "2. Clicca sul pulsante 'Ordine di vendita'\n"
            "3. Clicca sul campo 'Prezzo'\n"
            "4. Clicca sul pulsante 'Crea ordine'\n"
            "5. Seleziona l'area del prezzo attuale (Shift + Trascina, poi Click Destro)\n"
            "6. Seleziona l'area del prezzo medio (Shift + Trascina, poi Click Destro)"
        ),
        "region_map": {
            "sell_button": "Pulsante 'Vendi'",
            "order_button": "Pulsante 'Ordine di vendita'",
            "price_input": "Campo di input 'Prezzo'",
            "submit_button": "Pulsante 'Crea ordine'",
            "price_value": "Area 'Prezzo Attuale'",
            "average_price": "Area 'Prezzo Medio'",
        },
    },
}


def deep_merge_config(default_cfg: dict, user_cfg: dict) -> dict:
    """Recursively merges user_cfg into default_cfg preserving default keys."""
    merged = default_cfg.copy()
    for k, v in user_cfg.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = deep_merge_config(merged[k], v)
        else:
            merged[k] = v
    return merged


def parse_albion_number(text: str) -> int | None:
    """
    Robust number parser for Albion Online market UI text.
    Handles US format (1,500,000), EU format (1.500.000), decimals with suffixes (1.5M, 10.5k),
    and strips noise or common OCR letter confusions.
    """
    if not text:
        return None

    text = text.strip()
    text = re.sub(r"[^\w.,]", "", text)

    # Normalize common OCR character confusions in digits
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


def calculate_sell_price(
    number1: int | None,
    number2: int | None,
    fallback_ratio: float,
    max_diff_percent: float,
) -> tuple[int, str, float]:
    """
    Calculates target sell order price with safety protections.
    Returns (price, reason_key, diff_percent).
    """
    if number1 is None and number2 is None:
        return (0, "none", 0.0)

    if number1 is None:
        return (max(1, int(round(number2 * fallback_ratio))), "fallback_avg", 0.0)

    if number2 is None:
        return (max(1, int(round(number1 * fallback_ratio))), "fallback_num1", 0.0)

    diff_percent = abs(number1 - number2) / max(1, number2) * 100.0

    if diff_percent > max_diff_percent:
        # If current lowest order is heavily undercut / trap price (< average - diff%)
        if number1 < number2 * (1.0 - max_diff_percent / 100.0):
            return (max(1, int(round(number2 * fallback_ratio))), "diff_protected", diff_percent)
        else:
            return (max(1, int(round(number1 * fallback_ratio))), "close", diff_percent)
    else:
        return (max(1, int(round(number1 * fallback_ratio))), "close", diff_percent)


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

        self.log_queue = []
        self.log_lock = threading.Lock()

        self.selection_overlay = None
        self.selection_canvas = None
        self.instruction_window = None
        self.instruction_label = None

        self.lang = "en"
        self.strings = STRINGS[self.lang]

        self.CONFIG_FILE = os.path.join(BASE_DIR, "auto_config.json")
        self.screen_width, self.screen_height = pyautogui.size()
        self.config = self._get_default_config()
        self.load_config()

        self.lang = self.config.get("language", "en")
        self.strings = STRINGS.get(self.lang, STRINGS["en"])

        self.setup_gui()
        self.update_gui_from_config()

        self.mouse_listener = None
        self.setup_hotkeys()
        self.start_input_listeners()

        # Single recurring timer for UI log draining
        self.root.after(200, self.update_log_area)
        self.log_message("INFO", self.strings["log_ready"])

    def _safe_gui_call(self, func, *args, **kwargs):
        """Dispatches a GUI function onto the Tkinter main thread."""
        try:
            self.root.after(0, lambda: func(*args, **kwargs))
        except Exception:
            pass

    def set_language(self, lang_code, save=False):
        self.lang = lang_code
        self.strings = STRINGS.get(lang_code, STRINGS["en"])

        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_gui()
        self.update_gui_from_config()

        if save:
            self.config["language"] = lang_code
            self.save_config()

    def _get_default_config(self):
        return {
            "language": "en",
            "tesseract_path": "",
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
                "robust_attempts": 12,
                "min_majority_count": 4,
            },
            "ocr": {
                "whitelist_digits": "0123456789.,MTKmtk",
            },
            "sleep": {
                "between_clicks": {"min": 0.04, "max": 0.06},
                "after_recognition": {"min": 0.04, "max": 0.06},
                "before_input": {"min": 0.04, "max": 0.06},
                "after_input": {"min": 0.14, "max": 0.16},
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
                self.log_message("ERROR", self.strings["error_load_config"].format(e))
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
            self.log_message("ERROR", self.strings["error_save_config"].format(e))

    def setup_gui(self):
        self.root.title(self.strings["app_title"])
        self.root.geometry("760x560")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#2d2d2d")

        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family="Segoe UI", size=10)

        # Menu bar
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(
            label=self.strings["menu_cal_full"],
            command=self.start_full_calibration,
        )

        cal_single_menu = tk.Menu(file_menu, tearoff=0)
        for region_key, region_name in self.strings["region_map"].items():
            cal_single_menu.add_command(
                label=region_name,
                command=lambda r=region_key: self.start_single_calibration(r),
            )
        file_menu.add_cascade(
            label=self.strings["menu_cal_single"],
            menu=cal_single_menu,
        )
        file_menu.add_command(
            label=self.strings["menu_select_tesseract"],
            command=self.prompt_select_tesseract,
        )
        file_menu.add_command(
            label=self.strings["menu_save_config"],
            command=self.save_config,
        )
        file_menu.add_separator()
        file_menu.add_command(
            label=self.strings["menu_exit"],
            command=self.on_closing,
        )
        menu_bar.add_cascade(label=self.strings["menu_file"], menu=file_menu)

        lang_menu = tk.Menu(menu_bar, tearoff=0)
        for lang_code, lang_name in {"en": "English", "it": "Italiano"}.items():
            lang_menu.add_command(
                label=lang_name,
                command=lambda lc=lang_code: self.set_language(lc, save=True),
            )
        menu_bar.add_cascade(label=self.strings["menu_language"], menu=lang_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(
            label=self.strings["menu_guide"],
            command=self.show_help,
        )
        menu_bar.add_cascade(label=self.strings["menu_help"], menu=help_menu)

        self.root.config(menu=menu_bar)

        # Main Layout frames
        main_frame = tk.Frame(self.root, bg="#2d2d2d")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)

        # Log Section
        log_frame = tk.LabelFrame(
            main_frame,
            text=self.strings["log_title"],
            bg="#2d2d2d",
            fg="white",
            padx=5,
            pady=5,
        )
        log_frame.grid(row=0, column=0, sticky="nsew", rowspan=2)

        self.text_area = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#dcdcdc",
            insertbackground="white",
            bd=0,
            highlightthickness=0,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Controls Section
        controls_frame = tk.LabelFrame(
            main_frame,
            text=self.strings["controls_title"],
            bg="#2d2d2d",
            fg="white",
            padx=10,
            pady=10,
        )
        controls_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        btn_text = self.strings["button_stop"] if self.main_loop_running else self.strings["button_start"]
        btn_bg = "#f44336" if self.main_loop_running else "#4CAF50"
        self.start_stop_button = tk.Button(
            controls_frame,
            text=btn_text,
            command=self.toggle_main_loop,
            bg=btn_bg,
            fg="white",
            font=("Segoe UI", 10, "bold"),
        )
        self.start_stop_button.pack(fill=tk.X, pady=5)

        # Logic Settings Section
        logic_frame = tk.LabelFrame(
            main_frame,
            text=self.strings["logic_title"],
            bg="#2d2d2d",
            fg="white",
            padx=10,
            pady=10,
        )
        logic_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(10, 0))

        self.fallback_ratio_var = tk.DoubleVar()
        tk.Label(
            logic_frame,
            text=self.strings["label_fallback_ratio"],
            bg="#2d2d2d",
            fg="white",
        ).pack(anchor="w")

        self.fallback_slider_label = tk.Label(
            logic_frame,
            text="",
            bg="#2d2d2d",
            fg="cyan",
        )
        self.fallback_slider_label.pack(anchor="w")

        tk.Scale(
            logic_frame,
            from_=50,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.fallback_ratio_var,
            showvalue=0,
            bg="#2d2d2d",
            fg="white",
            troughcolor="#555",
            highlightthickness=0,
            command=lambda v: self.fallback_slider_label.config(text=f"{int(float(v))}%"),
        ).pack(fill=tk.X, pady=(0, 10))

        self.max_diff_var = tk.IntVar()
        tk.Label(
            logic_frame,
            text=self.strings["label_max_diff"],
            bg="#2d2d2d",
            fg="white",
        ).pack(anchor="w")

        self.max_diff_label = tk.Label(
            logic_frame,
            text="",
            bg="#2d2d2d",
            fg="cyan",
        )
        self.max_diff_label.pack(anchor="w")

        tk.Scale(
            logic_frame,
            from_=5,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.max_diff_var,
            showvalue=0,
            bg="#2d2d2d",
            fg="white",
            troughcolor="#555",
            highlightthickness=0,
            command=lambda v: self.max_diff_label.config(text=f"{int(float(v))}%"),
        ).pack(fill=tk.X, pady=(0, 10))

        # Status Bar
        status_frame = tk.Frame(self.root, bg="#1e1e1e", height=25)
        status_frame.pack(fill=tk.X)

        self.status_label = tk.Label(
            status_frame,
            text=self.strings["status_ready"],
            bg="#1e1e1e",
            fg="white",
        )
        self.status_label.pack(side=tk.LEFT, padx=10)

        tk.Label(
            status_frame,
            text=self.strings["author_label"],
            bg="#1e1e1e",
            fg="#888",
        ).pack(side=tk.RIGHT, padx=10)

        tk.Label(
            status_frame,
            text=self.strings["resolution_label"].format(self.screen_width, self.screen_height),
            bg="#1e1e1e",
            fg="#888",
        ).pack(side=tk.RIGHT, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_gui_from_config(self):
        try:
            self.fallback_ratio_var.set(self.config["logic"]["fallback_ratio"] * 100)
            self.max_diff_var.set(self.config["logic"]["max_difference_percent"])
            self.fallback_slider_label.config(text=f"{self.fallback_ratio_var.get():.0f}%")
            self.max_diff_label.config(text=f"{self.max_diff_var.get()}%")
        except Exception:
            pass

    def update_config_from_gui(self):
        try:
            self.config["logic"]["fallback_ratio"] = self.fallback_ratio_var.get() / 100.0
            self.config["logic"]["max_difference_percent"] = self.max_diff_var.get()
        except Exception:
            pass

    def update_status_label(self, text_key, color):
        self._safe_gui_call(lambda: self.status_label.config(text=self.strings.get(text_key, text_key), fg=color))

    def show_help(self):
        messagebox.showinfo(self.strings["menu_guide"], self.strings["help_text"])

    def prompt_select_tesseract(self):
        path = filedialog.askopenfilename(
            title=self.strings["tesseract_select_prompt"],
            filetypes=[("Tesseract Executable", "tesseract.exe"), ("All Executables", "*.exe")],
        )
        if path and os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            self.config["tesseract_path"] = path
            self.save_config()
            self.log_message("CONFIG", self.strings["tesseract_configured"].format(path))

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
                    self.text_area.insert(tk.END, item + "\n")
                self.text_area.see(tk.END)
            except Exception:
                pass
        self.root.after(200, self.update_log_area)

    def start_full_calibration(self):
        self._start_calibration_process(list(self.strings["region_map"].keys()))

    def start_single_calibration(self, region_key):
        self._start_calibration_process([region_key])

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

        self.update_status_label("status_calibrating", "orange")
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
            self.log_message(
                "CALIBRATE",
                self.strings["log_cal_area_saved"].format(
                    self.strings["region_map"][current_region],
                    rel_x1,
                    rel_y1,
                    rel_x2,
                    rel_y2,
                ),
            )
        else:
            rel_x, rel_y = (x / self.screen_width * 100), (y / self.screen_height * 100)
            self.config["regions"][current_region] = {"x": rel_x, "y": rel_y}
            self.log_message(
                "CALIBRATE",
                self.strings["log_cal_point_saved"].format(
                    self.strings["region_map"][current_region],
                    rel_x,
                    rel_y,
                ),
            )

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

        self.update_status_label("status_ready", "white")
        if cancelled:
            self.log_message("CALIBRATE", self.strings["log_cal_cancel"])
        else:
            self.save_config()
            self.log_message("CALIBRATE", self.strings["log_cal_done"])

    def handle_esc_key(self):
        # Only cancel calibration when calibration mode is active (avoids global Esc hijacking)
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
            self.log_message("SKIP", self.strings["log_cycle_skip_user"])

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
                # Retain drag coordinates so user can right-click confirm after releasing Shift
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
            x1, y1, x2, y2,
            fill="#ff3333",
            outline="#ff0000",
            width=2,
            tag="selection_rect",
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
                self.log_message("STOP", self.strings["log_main_stop_user"])
            else:
                # Validation check: ensure regions are calibrated before starting
                uncalibrated = [
                    k for k, v in self.config["regions"].items()
                    if ("x" in v and v["x"] == 0 and v["y"] == 0) or
                       ("x1" in v and v["x1"] == 0 and v["x2"] == 0)
                ]
                if uncalibrated:
                    msg = "Please calibrate the interface (F1) before starting the cycle!\nMissing regions: " + ", ".join(uncalibrated)
                    messagebox.showwarning("Calibration Needed", msg)
                    return

                self.main_loop_running = True
                self.stop_worker_event.clear()
                self.skip_iteration_event.clear()
                self.main_loop_thread = threading.Thread(target=self.run_main_loop, daemon=True)
                self.main_loop_thread.start()
                self.log_message("START", self.strings["log_main_start"])
                self.start_stop_button.config(text=self.strings["button_stop"], bg="#f44336")
                self.update_status_label("status_running", "#4CAF50")

    def interruptible_sleep(self, duration):
        """Sleep that wakes up immediately if stop or skip is requested."""
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

    def _get_random_sleep(self, action):
        sleep_config = self.config["sleep"].get(action, {"min": 0.05, "max": 0.05})
        return random.uniform(sleep_config["min"], sleep_config["max"])

    def _preprocess_variants(self, pil_image):
        """Generates multiple high-quality binarized variants optimized for OCR."""
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

        # Variant 1: Adaptive Gaussian threshold with proportional block size
        block_size = max(15, (resized.shape[0] // 4) * 2 + 1)
        blurred = cv2.GaussianBlur(resized, (3, 3), 0)
        thresh_adapt = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, 3
        )
        variants.append(thresh_adapt)

        # Variant 2: Inverted adaptive threshold (for light gold/white text on dark background)
        variants.append(cv2.bitwise_not(thresh_adapt))

        # Variant 3: Otsu thresholding with CLAHE contrast boost
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(resized)
        _, thresh_otsu = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(thresh_otsu)

        # Variant 4: Inverted Otsu
        variants.append(cv2.bitwise_not(thresh_otsu))

        return [Image.fromarray(v) for v in variants]

    def _parse_number(self, text):
        return parse_albion_number(text)

    def _recognize_number(self, region_name):
        return self._robust_recognize_number(region_name)

    def _robust_recognize_number(self, region_name):
        results = []
        attempts = self.config["logic"]["robust_attempts"]
        psm_configs = ["--psm 7", "--psm 8", "--psm 6", "--psm 11"]
        whitelist = self.config["ocr"]["whitelist_digits"]

        self.log_message("INFO", self.strings["ocr_robust_start"].format(attempts))

        try:
            x1, y1, x2, y2 = self._get_absolute_coords(region_name)
            if x2 <= x1 or y2 <= y1:
                self.log_message("ERROR", f"Invalid coordinates for {region_name}")
                return None
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            variants = self._preprocess_variants(img)
        except Exception as e:
            self.log_message("ERROR", f"Screen grab failed: {e}")
            return None

        for i in range(attempts):
            if self.stop_worker_event.is_set() or self.skip_iteration_event.is_set():
                break

            processed_img = variants[i % len(variants)]
            psm = psm_configs[(i // len(variants)) % len(psm_configs)]
            tess_config = f"{psm} -c tessedit_char_whitelist={whitelist}"

            try:
                raw_text = pytesseract.image_to_string(processed_img, config=tess_config).strip()
                parsed = self._parse_number(raw_text)
                self.log_message(
                    "DEBUG",
                    self.strings["ocr_robust_attempt"].format(i + 1, psm, raw_text, parsed),
                )
                if parsed is not None:
                    results.append(parsed)
            except Exception as e:
                self.log_message("ERROR", f"OCR attempt failed: {e}")

            if self.interruptible_sleep(self._get_random_sleep("robust_recognition")):
                break

        if not results:
            self.log_message("ERROR", self.strings["ocr_no_valid_results"])
            return None

        counter = Counter(results)
        most_common, count = counter.most_common(1)[0]
        min_count = self.config["logic"]["min_majority_count"]

        # Accept if count meets threshold or if there are strong consistent matches
        if count >= min_count or (len(results) >= 2 and count == len(results)):
            self.log_message("SUCCESS", self.strings["ocr_majority_found"].format(most_common, count))
            return most_common
        else:
            self.log_message("WARNING", self.strings["ocr_majority_fail"].format(most_common, count, min_count))
            return None

    def run_main_loop(self):
        while not self.stop_worker_event.is_set():
            self.skip_iteration_event.clear()
            try:
                # 1. Click Sell Tab
                pyautogui.click(self._get_absolute_coords("sell_button"))
                if self.interruptible_sleep(self._get_random_sleep("between_clicks")):
                    if self.stop_worker_event.is_set():
                        break
                    continue

                # 2. Click Sell Order Tab
                pyautogui.click(self._get_absolute_coords("order_button"))
                if self.interruptible_sleep(self._get_random_sleep("between_clicks")):
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
                    self.log_message("SUCCESS", self.strings["main_num1_ok"].format(number1))
                else:
                    self.log_message("WARNING", self.strings["main_num1_fail"])

                # 4. Recognize Average Market Price
                number2 = self._robust_recognize_number("average_price")
                if self.stop_worker_event.is_set():
                    break
                if self.skip_iteration_event.is_set():
                    continue

                if not number2:
                    self.log_message("ERROR", self.strings["main_num2_fail"])
                    if self.interruptible_sleep(self._get_random_sleep("between_cycles")):
                        if self.stop_worker_event.is_set():
                            break
                    continue

                self.log_message("INFO", self.strings["main_num2_ok"].format(number2))

                # Read logic values safely
                fallback_ratio = self.fallback_ratio_var.get() / 100.0
                max_diff_percent = float(self.max_diff_var.get())

                result, reason, diff = calculate_sell_price(
                    number1, number2, fallback_ratio, max_diff_percent
                )

                if reason == "fallback_avg":
                    self.log_message("FALLBACK", self.strings["main_fallback"].format(fallback_ratio * 100, number2, result))
                elif reason == "fallback_num1":
                    self.log_message("FALLBACK", self.strings["main_fallback_num1"].format(fallback_ratio * 100, number1, result))
                elif reason == "diff_protected":
                    self.log_message("INFO", self.strings["main_diff_check"].format(max_diff_percent, diff))
                    self.log_message("SUCCESS", self.strings["main_result_from_refined"].format(fallback_ratio * 100, result))
                else:
                    self.log_message("SUCCESS", self.strings["main_result_from_close"].format(diff, fallback_ratio * 100, result))

                if result <= 0:
                    result = 1

                # 5. Focus Price Input Field and Clear Existing Text
                pyautogui.click(self._get_absolute_coords("price_input"))
                if self.interruptible_sleep(self._get_random_sleep("before_input")):
                    if self.stop_worker_event.is_set():
                        break
                    continue

                # Clear previous number completely before typing
                pyautogui.hotkey("ctrl", "a")
                pyautogui.press("backspace")
                time.sleep(0.04)

                # Type new price
                pyautogui.write(str(result))
                if self.interruptible_sleep(self._get_random_sleep("between_clicks")):
                    if self.stop_worker_event.is_set():
                        break
                    continue

                # 6. Click Create Order Button
                pyautogui.click(self._get_absolute_coords("submit_button"))
                if self.interruptible_sleep(self._get_random_sleep("after_input")):
                    if self.stop_worker_event.is_set():
                        break
                    continue

                self.log_message("ACTION", self.strings["main_value_entered"].format(result))

            except pyautogui.FailSafeException:
                self.log_message("WARNING", self.strings["main_failsafe"])
                break
            except Exception as e:
                self.log_message("ERROR", self.strings["main_critical_error"].format(e))

            if self.interruptible_sleep(self._get_random_sleep("between_cycles")):
                if self.stop_worker_event.is_set():
                    break

        # Reset loop state when finished
        with self.state_lock:
            self.main_loop_running = False

        self._safe_gui_call(lambda: [
            self.start_stop_button.config(text=self.strings["button_start"], bg="#4CAF50"),
            self.update_status_label("status_ready", "white"),
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


def detect_tesseract_binary(custom_config_path: str = "") -> str:
    """Finds the Tesseract executable across known Windows paths and PATH."""
    candidate_paths = [
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
            return p

    return ""


if __name__ == "__main__":
    # Load config early to inspect saved tesseract_path if available
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

    if not tesseract_path:
        root_temp = tk.Tk()
        root_temp.withdraw()
        ask_user = messagebox.askyesno(
            "Tesseract OCR Not Found",
            "Tesseract OCR executable was not found in standard paths.\n\n"
            "Would you like to manually browse for tesseract.exe?",
        )
        if ask_user:
            chosen_path = filedialog.askopenfilename(
                title="Select tesseract.exe",
                filetypes=[("Tesseract Executable", "tesseract.exe"), ("All Executables", "*.exe")],
            )
            if chosen_path and os.path.isfile(chosen_path):
                tesseract_path = chosen_path
            else:
                messagebox.showerror(
                    "Tesseract OCR Required",
                    "AutoMarketSeller requires Tesseract OCR to recognize market prices.\n"
                    "Please install Tesseract OCR and relaunch the application.",
                )
                sys.exit(1)
        else:
            sys.exit(1)
        root_temp.destroy()

    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    root = tk.Tk()
    app = AutoMarketSeller(root)
    root.mainloop()