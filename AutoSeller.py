import pyautogui
import pytesseract
from PIL import Image, ImageEnhance, ImageGrab
import time
import keyboard
from pynput import mouse
import numpy as np
import cv2
import re
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, font as tkfont
import datetime
import json
import os
import random
from collections import Counter

# STRUTTURA DATI MULTILINGUA
STRINGS = {
    "it": {
        "app_title": "🤖 Auto Market Seller v1.0",
        "log_title": "📋 Log di Lavoro dell'Algoritmo",
        "status_ready": "Stato: Pronto",
        "status_running": "Stato: In Esecuzione",
        "status_paused": "Stato: In Pausa",
        "status_calibrating": "Stato: Calibrazione...",
        "author_label": "Autore: NobodySan Credit To Vortales",
        "resolution_label": "Risoluzione: {}x{}",
        "menu_file": "File",
        "menu_cal_full": "Avvia Calibrazione Completa (F1)",
        "menu_cal_single": "Calibra Elemento",
        "menu_save_config": "Salva Configurazione",
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
        "info_no_config": "ℹ️ File di configurazione non trovato. Verrà creato con i valori predefiniti.",
        "error_load_config": "❌ Errore nel caricamento della configurazione: {}",
        "error_save_config": "❌ Impossibile salvare la configurazione: {}",
        "log_ready": "🎯 Pronto per l'uso.",
        "log_cal_start": "🔧 Modalità di calibrazione avviata.",
        "log_cal_hint": "ℹ️ Segui le istruzioni nella finestra in alto. Premi 'Esc' per annullare.",
        "log_cal_done": "✅ Calibrazione completata! Configurazione salvata.",
        "log_cal_cancel": "❌ Calibrazione annullata dall'utente.",
        "log_cal_point_saved": "📍 {} salvato: ({:.2f}%, {:.2f}%)",
        "log_cal_area_saved": "✅ {} salvata: {:.2f}%, {:.2f}% -> {:.2f}%, {:.2f}%",
        "log_main_start": "🚀 Ciclo di vendita avviato. Premi F4 per fermare.",
        "log_main_stop_user": "🛑 Ciclo di vendita fermato dall'utente (F4).",
        "log_cycle_stop_user": "🛑 Ciclo corrente fermato dall'utente (F5).",
        "log_test_price": "Test 'Prezzo': {:,}",
        "log_test_price_fail": "❌ Test 'Prezzo': Riconoscimento fallito.",
        "log_test_avg_price": "Test 'Prezzo Medio': {:,}",
        "log_test_avg_price_fail": "❌ Test 'Prezzo Medio': Riconoscimento fallito.",
        "cal_instruction_point": "Fai clic con il TASTO DESTRO su:\n'{}'",
        "cal_instruction_area": "Tieni premuto MAIUSC e trascina per selezionare l'area di:\n'{}'\n\n(Rilascia e fai clic con il TASTO DESTRO per confermare)",
        "ocr_raw_result": "Raw OCR result from {}: '{}'",
        "ocr_robust_attempt": "Robust OCR attempt {}: '{}'",
        "ocr_no_valid_results": "❌ Tutti i tentativi di riconoscimento sono falliti.",
        "ocr_majority_found": "✅ Corrispondenze sufficienti: {:,} (trovato {} volte)",
        "ocr_majority_fail": "⚠️ Corrispondenze insufficienti: {:,} ({} volte), necessarie ≥ {}",
        "main_num1_ok": "Primo numero: {:,}",
        "main_num1_fail": "❌ Impossibile riconoscere il primo numero.",
        "main_num2_fail": "❌ Impossibile riconoscere il secondo numero. Salto l'iterazione.",
        "main_num2_ok": "Secondo numero: {:,}",
        "main_fallback": "→ Fallback: {:.0f}% del secondo numero → {:,}",
        "main_diff_check": "I numeri differiscono >{}%. Avvio del raffinamento preciso...",
        "main_refined1_ok": "🔍 Primo numero raffinato: {:,}",
        "main_refined1_fail": "⚠️ Impossibile raffinare il primo numero. Uso quello originale.",
        "main_refined2_ok": "🔍 Secondo numero raffinato: {:,}",
        "main_result_from_refined": "→ Risultato: {:.0f}% del primo numero scelto = {:,}",
        "main_result_from_close": "→ I numeri sono simili. Risultato: {:.0f}% del primo = {:,}",
        "main_value_entered": "✅ Valore inserito: {:,}",
        "main_critical_error": "Errore critico nel ciclo principale: {}",
        "region_map": {
            "sell_button": "Pulsante 'Vendi'",
            "order_button": "Pulsante 'Ordine di vendita'",
            "price_input": "Campo di input 'Prezzo'",
            "submit_button": "Pulsante 'Crea ordine'",
            "price_value": "Area 'Prezzo Attuale'",
            "average_price": "Area 'Prezzo Medio'"
        }
    },
    "en": {
        "app_title": "🤖 Auto Market Seller v1.0",
        "log_title": "📋 Algorithm Work Log",
        "status_ready": "Status: Ready",
        "status_running": "Status: Running",
        "status_paused": "Status: Paused",
        "status_calibrating": "Status: Calibrating...",
        "author_label": "Author: Vortales",
        "resolution_label": "Resolution: {}x{}",
        "menu_file": "File",
        "menu_cal_full": "Start Full Calibration (F1)",
        "menu_cal_single": "Calibrate Element",
        "menu_save_config": "Save Configuration",
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
        "info_no_config": "ℹ️ Configuration file not found. It will be created with default values.",
        "error_load_config": "❌ Error loading configuration: {}",
        "error_save_config": "❌ Could not save configuration: {}",
        "log_ready": "🎯 Ready for use.",
        "log_cal_start": "🔧 Calibration mode started.",
        "log_cal_hint": "ℹ️ Follow the instructions in the top window. Press 'Esc' to cancel.",
        "log_cal_done": "✅ Calibration complete! Configuration saved.",
        "log_cal_cancel": "❌ Calibration cancelled by user.",
        "log_cal_point_saved": "📍 {} saved: ({:.2f}%, {:.2f}%)",
        "log_cal_area_saved": "✅ {} saved: {:.2f}%, {:.2f}% -> {:.2f}%, {:.2f}%",
        "log_main_start": "🚀 Sales cycle started. Press F4 to stop.",
        "log_main_stop_user": "🛑 Sales cycle stopped by user (F4).",
        "log_cycle_stop_user": "🛑 Current cycle stopped by user (F5).",
        "log_test_price": "Test 'Price': {:,}",
        "log_test_price_fail": "❌ Test 'Price': Recognition failed.",
        "log_test_avg_price": "Test 'Average Price': {:,}",
        "log_test_avg_price_fail": "❌ Test 'Average Price': Recognition failed.",
        "cal_instruction_point": "RIGHT-CLICK on:\n'{}'",
        "cal_instruction_area": "Hold SHIFT and drag to select the area of:\n'{}'\n\n(Release and RIGHT-CLICK to confirm)",
        "ocr_raw_result": "Raw OCR result from {}: '{}'",
        "ocr_robust_attempt": "Robust OCR attempt {}: '{}'",
        "ocr_no_valid_results": "❌ All recognition attempts failed.",
        "ocr_majority_found": "✅ Sufficient matches: {:,} (found {} times)",
        "ocr_majority_fail": "⚠️ Insufficient matches: {:,} ({} times), required ≥ {}",
        "main_num1_ok": "First number: {:,}",
        "main_num1_fail": "❌ Unable to recognize the first number.",
        "main_num2_fail": "❌ Unable to recognize the second number. Skipping iteration.",
        "main_num2_ok": "Second number: {:,}",
        "main_fallback": "→ Fallback: {:.0f}% of the second number → {:,}",
        "main_diff_check": "Numbers differ >{}%. Starting precise refinement...",
        "main_refined1_ok": "🔍 Refined first number: {:,}",
        "main_refined1_fail": "⚠️ Unable to refine the first number. Using the original one.",
        "main_refined2_ok": "🔍 Refined second number: {:,}",
        "main_result_from_refined": "→ Result: {:.0f}% of the chosen first number = {:,}",
        "main_result_from_close": "→ Numbers are similar. Result: {:.0f}% of the first = {:,}",
        "main_value_entered": "✅ Value entered: {:,}",
        "main_critical_error": "Critical error in the main loop: {}",
        "region_map": {
            "sell_button": "Sell Button",
            "order_button": "Sell Order Button",
            "price_input": "Price Input Field",
            "submit_button": "Create Order Button",
            "price_value": "Current Price Area",
            "average_price": "Average Price Area"
        }
    }
}


class AutoMarketSeller:
    def __init__(self, root):
        self.root = root
        self.calibration_active = False
        self.main_loop_running = False
        self.drag_start_point = None
        self.current_drag_box = None
        self.calibration_step = 0
        self.main_loop_thread = None
        self.current_loop_stop_flag = threading.Event()
        self.log_queue = []
        self.log_lock = threading.Lock()
        
        # Variabili per la visualizzazione della selezione
        self.selection_overlay = None
        self.selection_canvas = None
        
        # Imposta una lingua di default per i log iniziali
        self.lang = "en"
        self.strings = STRINGS[self.lang]

        self.CONFIG_FILE = "auto_config.json"
        self.screen_width, self.screen_height = pyautogui.size()
        self.config = self._get_default_config()
        self.load_config()

        # Imposta la lingua finale dalla configurazione e costruisce la GUI
        self.set_language(self.config.get("language", "en"), save=False)

        self.mouse_listener = None
        self.setup_hotkeys()
        self.start_input_listeners()
        self.log_message("INFO", self.strings["log_ready"])

    def set_language(self, lang_code, save=False):
        self.lang = lang_code
        self.strings = STRINGS.get(lang_code, STRINGS["it"]) # Fallback a IT se la lingua non esiste

        # Ricostruisce l'interfaccia utente con la nuova lingua
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_gui() 
        self.update_gui_from_config()

        # Salva la configurazione solo se l'azione è stata avviata dall'utente (es. menu)
        if save:
            self.config["language"] = lang_code
            self.save_config()

    def _get_default_config(self):
        return {
            "language": "en",
            "regions": { "sell_button": {"x": 0, "y": 0}, "order_button": {"x": 0, "y": 0}, "price_input": {"x": 0, "y": 0}, "submit_button": {"x": 0, "y": 0}, "price_value": {"x1": 0, "y1": 0, "x2": 0, "y2": 0}, "average_price": {"x1": 0, "y1": 0, "x2": 0, "y2": 0}},
            "logic": {"fallback_ratio": 0.90, "max_difference_percent": 30, "robust_attempts": 12, "min_majority_count": 4},
            "ocr": {"whitelist_digits": "0123456789.,MTKmtk"},
            "sleep": {"between_clicks": {"min": 0.04, "max": 0.06}, "after_recognition": {"min": 0.04, "max": 0.06}, "before_input": {"min": 0.04, "max": 0.06}, "after_input": {"min": 0.14, "max": 0.16}, "between_cycles": {"min": 0.4, "max": 0.6}, "robust_recognition": {"min": 0.02, "max": 0.03}}
        }

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    # Unisce la configurazione caricata a quella di default in modo robusto
                    for key, value in loaded_config.items():
                        if key in self.config and isinstance(self.config[key], dict) and isinstance(value, dict):
                            self.config[key].update(value)
                        else:
                            self.config[key] = value
                self.log_message("CONFIG", self.strings["info_config_loaded"])
            except Exception as e:
                self.log_message("ERROR", self.strings["error_load_config"].format(e))
        else:
            self.log_message("INFO", self.strings["info_no_config"])

    def save_config(self):
        try:
            self.update_config_from_gui()
            with open(self.CONFIG_FILE, 'w') as f: json.dump(self.config, f, indent=4)
            self.log_message("CONFIG", self.strings["info_config_saved"])
        except Exception as e:
            self.log_message("ERROR", self.strings["error_save_config"].format(e))

    def setup_gui(self):
        self.root.title(self.strings["app_title"])
        self.root.geometry("750x550"); self.root.attributes("-topmost", True); self.root.configure(bg="#2d2d2d")
        default_font = tkfont.nametofont("TkDefaultFont"); default_font.configure(family="Segoe UI", size=10)
        
        menu_bar = tk.Menu(self.root)
        
        # --- File Menu ---
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label=self.strings["menu_cal_full"], command=self.start_full_calibration)
        cal_single_menu = tk.Menu(file_menu, tearoff=0)
        for region_key, region_name in self.strings["region_map"].items():
            cal_single_menu.add_command(label=region_name, command=lambda r=region_key: self.start_single_calibration(r))
        file_menu.add_cascade(label=self.strings["menu_cal_single"], menu=cal_single_menu)
        file_menu.add_command(label=self.strings["menu_save_config"], command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label=self.strings["menu_exit"], command=self.on_closing)
        menu_bar.add_cascade(label=self.strings["menu_file"], menu=file_menu)
        
        # --- Language Menu ---
        lang_menu = tk.Menu(menu_bar, tearoff=0)
        for lang_code, lang_name in {"it": "Italiano", "en": "English"}.items():
            lang_menu.add_command(label=lang_name, command=lambda lc=lang_code: self.set_language(lc, save=True))
        menu_bar.add_cascade(label=self.strings["menu_language"], menu=lang_menu)

        # --- Help Menu ---
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label=self.strings["menu_guide"], command=self.show_help)
        menu_bar.add_cascade(label=self.strings["menu_help"], menu=help_menu)
        
        self.root.config(menu=menu_bar)

        main_frame = tk.Frame(self.root, bg="#2d2d2d"); main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10); main_frame.grid_rowconfigure(0, weight=1); main_frame.grid_columnconfigure(0, weight=3); main_frame.grid_columnconfigure(1, weight=1)
        log_frame = tk.LabelFrame(main_frame, text=self.strings["log_title"], bg="#2d2d2d", fg="white", padx=5, pady=5); log_frame.grid(row=0, column=0, sticky="nsew", rowspan=2); self.text_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=("Consolas", 9), bg="#1e1e1e", fg="#dcdcdc", insertbackground="white", bd=0, highlightthickness=0); self.text_area.pack(fill=tk.BOTH, expand=True)
        controls_frame = tk.LabelFrame(main_frame, text=self.strings["controls_title"], bg="#2d2d2d", fg="white", padx=10, pady=10); controls_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0)); self.start_stop_button = tk.Button(controls_frame, text=self.strings["button_start"], command=self.toggle_main_loop, bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold")); self.start_stop_button.pack(fill=tk.X, pady=5)
        logic_frame = tk.LabelFrame(main_frame, text=self.strings["logic_title"], bg="#2d2d2d", fg="white", padx=10, pady=10); logic_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(10, 0)); self.fallback_ratio_var = tk.DoubleVar(); tk.Label(logic_frame, text=self.strings["label_fallback_ratio"], bg="#2d2d2d", fg="white").pack(anchor="w"); self.fallback_slider_label = tk.Label(logic_frame, text="", bg="#2d2d2d", fg="cyan"); self.fallback_slider_label.pack(anchor="w"); tk.Scale(logic_frame, from_=50, to=100, orient=tk.HORIZONTAL, variable=self.fallback_ratio_var, showvalue=0, bg="#2d2d2d", fg="white", troughcolor="#555", highlightthickness=0, command=lambda v: self.fallback_slider_label.config(text=f"{int(float(v))}%")).pack(fill=tk.X, pady=(0, 10)); self.max_diff_var = tk.IntVar(); tk.Label(logic_frame, text=self.strings["label_max_diff"], bg="#2d2d2d", fg="white").pack(anchor="w"); self.max_diff_label = tk.Label(logic_frame, text="", bg="#2d2d2d", fg="cyan"); self.max_diff_label.pack(anchor="w"); tk.Scale(logic_frame, from_=5, to=100, orient=tk.HORIZONTAL, variable=self.max_diff_var, showvalue=0, bg="#2d2d2d", fg="white", troughcolor="#555", highlightthickness=0, command=lambda v: self.max_diff_label.config(text=f"{int(float(v))}%")).pack(fill=tk.X, pady=(0, 10))
        status_frame = tk.Frame(self.root, bg="#1e1e1e", height=25); status_frame.pack(fill=tk.X); self.status_label = tk.Label(status_frame, text=self.strings["status_ready"], bg="#1e1e1e", fg="white"); self.status_label.pack(side=tk.LEFT, padx=10); tk.Label(status_frame, text=self.strings["author_label"], bg="#1e1e1e", fg="#888").pack(side=tk.RIGHT, padx=10); tk.Label(status_frame, text=self.strings["resolution_label"].format(self.screen_width, self.screen_height), bg="#1e1e1e", fg="#888").pack(side=tk.RIGHT, padx=10)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.after(200, self.update_log_area)

    def update_gui_from_config(self):
        self.fallback_ratio_var.set(self.config["logic"]["fallback_ratio"] * 100)
        self.max_diff_var.set(self.config["logic"]["max_difference_percent"])
        self.fallback_slider_label.config(text=f"{self.fallback_ratio_var.get():.0f}%")
        self.max_diff_label.config(text=f"{self.max_diff_var.get()}%")

    def update_config_from_gui(self):
        self.config["logic"]["fallback_ratio"] = self.fallback_ratio_var.get() / 100.0
        self.config["logic"]["max_difference_percent"] = self.max_diff_var.get()
        
    def update_status_label(self, text_key, color):
        self.status_label.config(text=self.strings[text_key], fg=color)

    def show_help(self): messagebox.showinfo(self.strings["menu_guide"], "F1: Start Full Calibration\nF2: Test Current Price\nF3: Test Average Price\nF4: Start/Stop cycle\nF5: Stop current cycle\nEsc: Cancel calibration")
    
    def log_message(self, level, message):
        with self.log_lock: self.log_queue.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {level.upper()}: {message}")

    def update_log_area(self):
        with self.log_lock:
            while self.log_queue: self.text_area.insert(tk.END, self.log_queue.pop(0) + "\n")
        self.text_area.see(tk.END); self.root.after(200, self.update_log_area)

    def start_full_calibration(self):
        self._start_calibration_process(list(self.strings["region_map"].keys()))

    def start_single_calibration(self, region_key):
        self._start_calibration_process([region_key])
        
    def _start_calibration_process(self, region_list):
        if self.calibration_active or self.main_loop_running: return
        self.calibration_active = True; self.calibration_step = 0
        self.calibration_regions = region_list
        self.update_status_label("status_calibrating", "orange")
        self.log_message("CALIBRATE", self.strings["log_cal_start"])
        self.log_message("HINT", self.strings["log_cal_hint"])
        self.create_instruction_window()

    def create_instruction_window(self):
        self.instruction_window = tk.Toplevel(self.root)
        self.instruction_window.title("Calibration Instructions")
        self.instruction_window.geometry("500x150")
        self.instruction_window.attributes("-topmost", True)
        self.instruction_window.configure(bg="black")
        self.instruction_label = tk.Label(self.instruction_window, text="", font=("Segoe UI", 16, "bold"), fg="white", bg="black", wraplength=480)
        self.instruction_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.update_instruction_window()

    def update_instruction_window(self):
        if not self.calibration_active or self.calibration_step >= len(self.calibration_regions):
            if hasattr(self, 'instruction_window'): self.instruction_window.destroy()
            return
        current_region_key = self.calibration_regions[self.calibration_step]
        region_name = self.strings["region_map"][current_region_key]
        is_area = "1" in list(self.config["regions"][current_region_key].keys())[0]
        instruction_text = self.strings["cal_instruction_area" if is_area else "cal_instruction_point"].format(region_name)
        self.instruction_label.config(text=instruction_text)

    def handle_calibration_click(self, x, y, button, pressed):
        if not self.calibration_active or not pressed or button != mouse.Button.right: return
        self._destroy_selection_overlay()
        current_region = self.calibration_regions[self.calibration_step]
        is_area = "1" in list(self.config["regions"][current_region].keys())[0]
        if is_area:
            if not self.drag_start_point or not self.current_drag_box: return
            x1, y1 = self.drag_start_point; x2, y2 = self.current_drag_box
            x1, x2 = min(x1, x2), max(x1, x2); y1, y2 = min(y1, y2), max(y1, y2)
            rel_x1, rel_y1, rel_x2, rel_y2 = (x1/self.screen_width*100), (y1/self.screen_height*100), (x2/self.screen_width*100), (y2/self.screen_height*100)
            self.config["regions"][current_region] = {"x1": rel_x1, "y1": rel_y1, "x2": rel_x2, "y2": rel_y2}
            self.log_message("CALIBRATE", self.strings["log_cal_area_saved"].format(self.strings["region_map"][current_region], rel_x1, rel_y1, rel_x2, rel_y2))
        else:
            rel_x, rel_y = (x/self.screen_width*100), (y/self.screen_height*100)
            self.config["regions"][current_region] = {"x": rel_x, "y": rel_y}
            self.log_message("CALIBRATE", self.strings["log_cal_point_saved"].format(self.strings["region_map"][current_region], rel_x, rel_y))
        
        self.drag_start_point = None; self.current_drag_box = None
        self.calibration_step += 1
        if self.calibration_step >= len(self.calibration_regions): self.finish_calibration()
        else: self.update_instruction_window()
            
    def finish_calibration(self, cancelled=False):
        if not self.calibration_active: return
        self.calibration_active = False; self.drag_start_point = None; self.current_drag_box = None
        self._destroy_selection_overlay()
        if hasattr(self, 'instruction_window'): self.instruction_window.destroy()
        self.update_status_label("status_ready", "white")
        if cancelled: self.log_message("CALIBRATE", self.strings["log_cal_cancel"])
        else: self.save_config(); self.log_message("CALIBRATE", self.strings["log_cal_done"])

    def setup_hotkeys(self):
        keyboard.add_hotkey('f1', self.start_full_calibration)
        keyboard.add_hotkey('f2', self.test_price_recognition)
        keyboard.add_hotkey('f3', self.test_average_price_recognition)
        keyboard.add_hotkey('f4', self.toggle_main_loop)
        keyboard.add_hotkey('f5', lambda: (self.current_loop_stop_flag.set(), self.log_message("STOP", self.strings["log_cycle_stop_user"])))
        keyboard.add_hotkey('esc', lambda: self.finish_calibration(cancelled=True) if self.calibration_active else None)

    def test_price_recognition(self):
        if self.main_loop_running or self.calibration_active: return
        number = self._recognize_number("price_value")
        if number is not None: self.log_message("TEST", self.strings["log_test_price"].format(number))
        else: self.log_message("TEST", self.strings["log_test_price_fail"])

    def test_average_price_recognition(self):
        if self.main_loop_running or self.calibration_active: return
        number = self._recognize_number("average_price")
        if number is not None: self.log_message("TEST", self.strings["log_test_avg_price"].format(number))
        else: self.log_message("TEST", self.strings["log_test_avg_price_fail"])

    def start_input_listeners(self):
        def on_move(x, y):
            if not self.calibration_active: return

            current_region_key = self.calibration_regions[self.calibration_step]
            is_area = "1" in list(self.config["regions"][current_region_key].keys())[0]

            if is_area and keyboard.is_pressed('shift'):
                if self.drag_start_point is None:
                    self.drag_start_point = (x, y)
                    self._create_selection_overlay()
                self.current_drag_box = (x, y)
                self._update_selection_rectangle()
            elif self.drag_start_point is not None:
                self._destroy_selection_overlay()
                self.drag_start_point = None

        self.mouse_listener = mouse.Listener(on_click=self.handle_calibration_click, on_move=on_move)
        self.mouse_listener.start()
    
    # --- NUOVE FUNZIONI PER LA VISUALIZZAZIONE DELLA SELEZIONE ---
    def _create_selection_overlay(self):
        if self.selection_overlay: return
        self.selection_overlay = tk.Toplevel(self.root)
        self.selection_overlay.attributes("-alpha", 0.3) # Opacità
        self.selection_overlay.attributes("-topmost", True)
        self.selection_overlay.overrideredirect(True) # Senza bordi
        self.selection_overlay.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        self.selection_canvas = tk.Canvas(self.selection_overlay, bg="white", highlightthickness=0)
        self.selection_canvas.pack(fill=tk.BOTH, expand=True)
        self.selection_overlay.wm_attributes("-transparentcolor", "white")

    def _update_selection_rectangle(self):
        if not self.selection_canvas or not self.drag_start_point or not self.current_drag_box: return
        self.selection_canvas.delete("selection_rect")
        x1, y1 = self.drag_start_point
        x2, y2 = self.current_drag_box
        self.selection_canvas.create_rectangle(x1, y1, x2, y2, fill="red", outline="red", tag="selection_rect")

    def _destroy_selection_overlay(self):
        if self.selection_overlay:
            self.selection_overlay.destroy()
            self.selection_overlay = None
            self.selection_canvas = None
    # --- FINE NUOVE FUNZIONI ---

    def toggle_main_loop(self):
        if self.calibration_active: return
        if self.main_loop_running: self.current_loop_stop_flag.set(); self.log_message("STOP", self.strings["log_main_stop_user"])
        else:
            self.main_loop_running = True; self.current_loop_stop_flag.clear()
            self.main_loop_thread = threading.Thread(target=self.run_main_loop, daemon=True); self.main_loop_thread.start()
            self.log_message("START", self.strings["log_main_start"])
        self.start_stop_button.config(text=self.strings["button_stop" if self.main_loop_running else "button_start"], bg="#f44336" if self.main_loop_running else "#4CAF50")
        self.update_status_label("status_running" if self.main_loop_running else "status_ready", "#4CAF50" if self.main_loop_running else "white")

    def _get_absolute_coords(self, region_name):
        region = self.config["regions"][region_name]
        if "x2" in region: return (int(self.screen_width*region["x1"]/100), int(self.screen_height*region["y1"]/100), int(self.screen_width*region["x2"]/100), int(self.screen_height*region["y2"]/100))
        else: return (int(self.screen_width*region["x"]/100), int(self.screen_height*region["y"]/100))

    def _get_random_sleep(self, action):
        sleep_config = self.config["sleep"].get(action, {"min": 0.05, "max": 0.05})
        return random.uniform(sleep_config["min"], sleep_config["max"])

    def _preprocess_image(self, image):
        image = image.convert('L'); enhancer = ImageEnhance.Contrast(image); image = enhancer.enhance(2.0)
        image_np = np.array(image); _, image_np = cv2.threshold(image_np, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        width, height = int(image_np.shape[1]*2), int(image_np.shape[0]*2)
        image_np = cv2.resize(image_np, (width, height), interpolation=cv2.INTER_CUBIC); return Image.fromarray(image_np)

    def _parse_number(self, text):
        if not text: return None
        text = re.sub(r'[а-яА-Я\s]', '', text).upper().rstrip('.')
        match = re.search(r'([\d.,]+)([MTK])?', text)
        if not match: return None
        number_str, suffix = match.groups()
        
        try:
            if ',' in number_str and '.' in number_str:
                if number_str.rfind(',') < number_str.rfind('.'):
                    number_str = number_str.replace(',', '')
                else:
                    number_str = number_str.replace('.', '').replace(',', '.')
            elif ',' in number_str:
                if len(number_str.split(',')[-1]) == 3:
                     number_str = number_str.replace(',', '')
                else:
                     number_str = number_str.replace(',', '.')
            
            number = float(number_str)
            if suffix == 'M': number *= 1_000_000
            elif suffix in ['T', 'K']: number *= 1_000
            return int(number)
        except (ValueError, TypeError): 
            return None

    def _recognize_number(self, region_name, use_robust=False):
        if use_robust: return self._robust_recognize_number(region_name)
        try:
            x1, y1, x2, y2 = self._get_absolute_coords(region_name)
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            processed = self._preprocess_image(img)
            text = pytesseract.image_to_string(processed, config=f'--psm 7 -c tessedit_char_whitelist={self.config["ocr"]["whitelist_digits"]}').strip()
            self.log_message("DEBUG", self.strings["ocr_raw_result"].format(region_name, text))
            return self._parse_number(text)
        except Exception: return None

    def _robust_recognize_number(self, region_name):
        results = []; 
        for i in range(self.config["logic"]["robust_attempts"]):
            try:
                x1, y1, x2, y2 = self._get_absolute_coords(region_name); img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                text = pytesseract.image_to_string(self._preprocess_image(img), config=f'--psm 7 -c tessedit_char_whitelist={self.config["ocr"]["whitelist_digits"]}').strip()
                self.log_message("DEBUG", self.strings["ocr_robust_attempt"].format(i + 1, text))
                results.append(self._parse_number(text))
            except Exception: results.append(None)
            time.sleep(self._get_random_sleep("robust_recognition"))
        valid_results = [r for r in results if r is not None]
        if not valid_results: self.log_message("ERROR", self.strings["ocr_no_valid_results"]); return None
        counter = Counter(valid_results); most_common, count = counter.most_common(1)[0]
        min_count = self.config["logic"]["min_majority_count"]
        if count >= min_count: self.log_message("SUCCESS", self.strings["ocr_majority_found"].format(most_common, count)); return most_common
        else: self.log_message("WARNING", self.strings["ocr_majority_fail"].format(most_common, count, min_count)); return None

    def run_main_loop(self):
        while not self.current_loop_stop_flag.is_set():
            try:
                pyautogui.click(self._get_absolute_coords("sell_button")); time.sleep(self._get_random_sleep("between_clicks"))
                pyautogui.click(self._get_absolute_coords("order_button")); time.sleep(self._get_random_sleep("between_clicks"))
                number1 = self._recognize_number("price_value")
                if number1: self.log_message("SUCCESS", self.strings["main_num1_ok"].format(number1))
                else: self.log_message("WARNING", self.strings["main_num1_fail"])
                number2 = self._recognize_number("average_price")
                if not number2: self.log_message("ERROR", self.strings["main_num2_fail"]); time.sleep(self._get_random_sleep("between_cycles")); continue
                self.log_message("INFO", self.strings["main_num2_ok"].format(number2))
                self.update_config_from_gui() 
                fallback_ratio = self.config["logic"]["fallback_ratio"]; result = 0
                if not number1:
                    result = int(number2 * fallback_ratio)
                    self.log_message("FALLBACK", self.strings["main_fallback"].format(fallback_ratio * 100, result))
                else:
                    diff_percent = abs(number1 - number2) / max(number1, number2) * 100
                    if diff_percent > self.config["logic"]["max_difference_percent"]:
                        self.log_message("INFO", self.strings["main_diff_check"].format(self.config["logic"]["max_difference_percent"]))
                        refined_number1 = self._robust_recognize_number("price_value")
                        if refined_number1: self.log_message("INFO", self.strings["main_refined1_ok"].format(refined_number1)); number1 = refined_number1
                        else: self.log_message("WARNING", self.strings["main_refined1_fail"])
                        self._robust_recognize_number("average_price")
                        result = int(number1 * fallback_ratio)
                        self.log_message("SUCCESS", self.strings["main_result_from_refined"].format(fallback_ratio * 100, result))
                    else:
                        result = int(number1 * fallback_ratio)
                        self.log_message("SUCCESS", self.strings["main_result_from_close"].format(fallback_ratio * 100, result))
                pyautogui.click(self._get_absolute_coords("price_input")); time.sleep(self._get_random_sleep("before_input"))
                pyautogui.write(str(result)); time.sleep(self._get_random_sleep("between_clicks"))
                pyautogui.click(self._get_absolute_coords("submit_button")); time.sleep(self._get_random_sleep("after_input"))
                self.log_message("ACTION", self.strings["main_value_entered"].format(result))
            except Exception as e:
                self.log_message("ERROR", self.strings["main_critical_error"].format(e))
            time.sleep(self._get_random_sleep("between_cycles"))
        self.main_loop_running = False
        self.root.after(0, lambda: [
            self.start_stop_button.config(text=self.strings["button_start"], bg="#4CAF50"),
            self.update_status_label("status_ready", "white")
        ])

    def on_closing(self):
        if self.mouse_listener: self.mouse_listener.stop()
        keyboard.unhook_all()
        self.root.destroy()
        os._exit(0)

if __name__ == "__main__":
    try:
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if not os.path.exists(tesseract_path):
            tesseract_path = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            if not os.path.exists(tesseract_path):
                root = tk.Tk(); root.withdraw()
                messagebox.showerror("Tesseract OCR Error", f"Tesseract not found.\nMake sure it is installed and the path in the script is correct.")
                os._exit(1)
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    except Exception as e:
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Critical Error", f"An error occurred on startup: {e}")
        os._exit(1)
    
    root = tk.Tk()
    app = AutoMarketSeller(root)
    root.mainloop()