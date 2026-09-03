[![Build Windows Executable](https://github.com/NobodySan97/AlbionOnline-AutoMarketSeller/actions/workflows/main.yml/badge.svg)](https://github.com/NobodySan97/AlbionOnline-AutoMarketSeller/actions/workflows/main.yml) ![Downloads](https://img.shields.io/github/downloads/NobodySan97/AlbionOnline-AutoMarketSeller/total?style=for-the-badge&logo=github&color=green)

# **Albion Online - Auto Market Seller v1.4**

This script automates the process of selling items on the Albion Online market. It automatically recognizes current prices and average values on screen, compares them, applies undercut/discount calculations, and enters your desired selling price (e.g., 10% lower) with anti-undercut trap protections.

---

## 🎯 Key Features & Improvements

- ✅ **Robust Multi-Strategy OCR**: Supports multi-filter adaptive and Otsu preprocessing for high accuracy on game fonts.
- ✅ **Universal Number Support**: Handles both European (`1.500.000` / `1.500`) and US formats (`1,500,000`), decimals, and suffixes: `k`, `K`, `m`, `M`, `t`, `T` (e.g. `686k` = 686,000).
- ✅ **Smart Anomaly & Undercut Protection**: Protects against 1-silver troll listings and OCR glitches by automatically falling back to average market price when abnormal divergence occurs.
- ✅ **Safe Input Emulation**: Clears text fields completely before writing to prevent number concatenation errors.
- ✅ **High-DPI Awareness**: Full native resolution support on Windows 10/11 with display scaling (125%, 150%, 200%).
- ✅ **Thread-Safe GUI**: Instant Start/Stop/Skip handling with real-time log streaming.
- ✅ **Dynamic Calibration**: Easily calibrate clickable regions and price areas (via F1).
- ✅ **Automatic Tesseract Detection & Browser**: Discovers Tesseract in standard folders, LocalAppData, and PATH, or lets you choose it via file dialog.

---

> ⚠️ **Important**: This is **not a cheat** and does not interact with the game's internal memory or API. The script only **emulates mouse clicks and keyboard input**, exactly as if you were manually trading.

---

## 🚀 Installation and Setup

1. Download the executable file from the [Releases](https://github.com/NobodySan97/AlbionOnline-AutoMarketSeller/releases) section.
2. Install [Tesseract OCR](https://sourceforge.net/projects/tesseract-ocr.mirror/files/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe/download) (or via `winget install UB-Mannheim.TesseractOCR`).
3. Run `AutoMarketSeller.exe`.
4. Press **F1** to calibrate UI coordinates on your screen.
5. Press **F4** to start the automatic selling cycle.

---

### 🎮 Controls

| Key | Action |
| :--- | :--- |
| **F1** | **Calibration Mode** (Right-click on interface elements) |
| **F2** | Test: Recognize "Price" area |
| **F3** | Test: Recognize "Average Price" area |
| **F4** | **Start / Stop** the main selling loop |
| **F5** | **Skip** the current item / cycle iteration without stopping |
| **Esc** | Cancel active calibration |

---

### 🔧 Configuration Parameters (`auto_config.json`)

* **fallback_ratio**: The discount coefficient (e.g., `0.90` sets prices to 90% of lowest sell order / average price).
* **max_difference_percent**: Maximum divergence allowed between current lowest price and average price before anomaly protections activate.
* **robust_attempts**: Number of OCR filter and PSM attempts for voting consensus.
* **min_majority_count**: Minimum consensus matches needed for high confidence.
* **sleep**: Randomized delays to ensure natural input timing.

---

### ⚙️ How to Calibrate (First Launch)

1. Open Albion Online and open the Market interface.
2. Press **F1** to start calibration.
3. Move your cursor over the **"Sell"** tab and **Right-Click**.
4. Move your cursor over the **"Sell Order"** button and **Right-Click**.
5. Move your cursor over the **"Price"** input field and **Right-Click**.
6. Move your cursor over the **"Create Order"** button and **Right-Click**.
7. Hold **SHIFT** and drag over the **Current Price** text area, then release and **Right-Click** to confirm.
8. Hold **SHIFT** and drag over the **Average Price** text area, then release and **Right-Click** to confirm.

Configuration is saved automatically.

---

### 🧰 Tech Stack

- Python 3.10+
- `pyautogui`, `pytesseract`, `Pillow`, `OpenCV (cv2)`, `pynput`, `keyboard`, `tkinter`
- Multi-threaded architecture with thread-safe UI scheduling and DPI awareness

---

### 💬 Author

Developed by: **NobodySan97**  
Refactored & Optimized (2025/2026)
