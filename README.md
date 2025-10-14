[![Build Windows Executable](https://github.com/NobodySan97/AlbionOnline-AutoMarketSeller/actions/workflows/main.yml/badge.svg)](https://github.com/NobodySan97/AlbionOnline-AutoMarketSeller/actions/workflows/main.yml) ![Downloads](https://img.shields.io/github/downloads/NobodySan97/AlbionOnline-AutoMarketSeller/total?style=for-the-badge&logo=github&color=green)

# **Albion Online - Auto Market Seller**

This script automates the process of selling items on the Albion Online market. It automatically recognizes prices and average values on the screen, compares them, and sets your price (e.g., 10% lower), saving you time while trading in the game.

---

![DEMO GIF](https://github.com/user-attachments/assets/15fd29a4-69f5-4ccb-aaad-f89a4522d874)

---

## 🎯 What does the script do?

- ✅ **Recognizes numbers from the screen** (price, average price) using OCR.
- ✅ Supports suffixes: `k`, `K`, `m`, `M`, `t`, `T` (e.g., `686k` = 686,000).
- ✅ Automatically **sets the price** (defaults to 90% of the first number or the average).
- ✅ **Calibration for any screen resolution** (via the F1 key).
- ✅ Flexible configuration through `auto_config.json`.
- ✅ Smart logic: if the numbers differ significantly, it runs a more accurate recognition to avoid errors.
- ✅ A complete GUI with real-time logs.

---

> ⚠️ **Important**: This is **not a cheat** and does not interact with the game's API. The script only **emulates mouse clicks and keyboard input**, just as if you were doing it yourself.

## 🚀 Installation and Setup

1.  Download the executable file from the [Releases](https://github.com/NobodySan97/AlbionOnline-AutoMarketSeller/releases) section.
2.  Download and install [Tesseract OCR](https://sourceforge.net/projects/tesseract-ocr.mirror/files/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe/download) with support for the English language.
3.  Unzip the archive and run `AutoMarketSeller.exe`.
4.  Press **F1** to calibrate.
5.  Press **F4** to start.

> ✅ It does not require Python and works on any Windows PC.

---

🔧 Make sure that Tesseract OCR is installed at the following path:
`C:\Program Files\Tesseract-OCR\tesseract.exe`

---

### 🔧 Explanation of `auto_config.json` Parameters

* **fallback_ratio**: The main coefficient the program uses to set the price. It's almost always applied. A value less than 1.0 means the program will sell at a discount (e.g., 10% off with a value of 0.9) to be competitive and sell items faster.
* **max_difference_percent**: Determines how much the two recognized prices (current and average) can differ to be considered "close". If the difference is greater, the program runs a more precise recognition to avoid errors.
* **robust_attempts**: The number of attempts to re-read a number when in doubt. A higher value means a more thorough check, but a slower process.
* **min_majority_count**: The minimum number of identical results among all recognition attempts required to consider a number valid.
* **sleep (various)**: The delays (sleep) between actions are randomized within a set range to simulate human behavior and reduce the risk of bot detection.

---

### 🎮 Controls

| Key | Action |
| :--- | :--- |
| **F1** | **Calibration Mode** (Right-click on interface elements) |
| **F2** | Test: Recognize "Price" |
| **F3** | Test: Recognize "Average Price" |
| **F4** | **Start / Stop** the main cycle |
| **F5** | Stop the current cycle only (not the whole program) |
| **Esc** | Exit the program completely |

---

### 🧰 Tech Stack

Python + pyautogui, pytesseract, PIL, OpenCV, pynput, tkinter.
OCR with image preprocessing (contrast, binarization, scaling).
Multi-threaded GUI with logging.
Dynamic calibration for any resolution.

---

### ⚙️ How to Calibrate (on first launch)

1.  Run the program and press the **F1** key.
2.  Open the market, move your cursor over the "Sell" tab, and **Right-Click**.
3.  Expand the "Sell Orders" and "Buy Orders" sections, move your cursor over "Sell Order", and **Right-Click**.
4.  Move your cursor over the "Price" input field and **Right-Click**.
5.  Move your cursor over the "Create Order" button and **Right-Click**.
6.  Reopen the item window, then press and hold **SHIFT** while dragging to select the price recognition area, then **Right-Click** to confirm.
7.  Press and hold **SHIFT** while dragging to select the average price area, then **Right-Click** to confirm.

**Note: Please restart the program after calibration!**
---

### 💬 Author

Developed by: **NobodySan97**
Year: 2025
