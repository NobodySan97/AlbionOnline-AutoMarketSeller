[![Build Windows Executable](https://github.com/NobodySan97/AlbionOnline-AutoMarketSeller/actions/workflows/main.yml/badge.svg)](https://github.com/NobodySan97/AlbionOnline-AutoMarketSeller/actions/workflows/main.yml) ![Downloads](https://img.shields.io/github/downloads/NobodySan97/AlbionOnline-AutoMarketSeller/total?style=for-the-badge&logo=github&color=green)

# **Albion Online - Auto Market Seller v2.5 Pro (Dual-Mode)**

Strumento desktop avanzato per l'automazione delle vendite sul mercato di Albion Online. Supporta due modalità operative selezionabili direttamente dall'interfaccia:
1. **⚡ Modalità Veloce 3-Point**: replica il ciclo di click rapido dal video reference (`Sell` -> `[-] Sconto 1 Silver` -> `Create Order`) ad altissima velocità senza richiedere OCR.
2. **🧠 Modalità Smart OCR**: legge tramite computer vision e Tesseract OCR il prezzo minimo attuale, calcola lo sconto percentuale desiderato (es. -1%, -2%, -5%, -10% o -1 Silver), protegge con prezzo minimo di sicurezza (`Floor Price`) e digita in modo naturale il prezzo calcolato prima di confermare l'ordine.

---

## 🎯 Caratteristiche Principali

### ⚡ 1. Selezione Modalità Operativa (Dual-Engine)
- **Modalità 3-Point Veloce**: setup in 3 click con Wizard guidato, ideale per svuotare interi inventari in pochi secondi sfruttando il pulsante `[-]` di Albion.
- **Modalità Smart OCR & Sconto %**:
  - **Sconto Percentuale Personalizzabile**: slider fluido da 0.5% a 25.0%, input numerico e preset rapidi (`[ 1% ]`, `[ 2% ]`, `[ 5% ]`, `[ 10% ]`, `[ -1 Silver ]`).
  - **Prezzo Minimo di Sicurezza (`Floor Price`)**: impedisce svendite accidentali se il mercato è crollato o se l'OCR rileva troll order.
  - **Pulsante `Test OCR`**: legge l'area a video e mostra a log sia il prezzo rilevato che il prezzo calcolato con la percentuale scelta.
  - **Cattura Area Prezzo Intuitiva**: basta fare click su due angoli (in alto a sinistra e in basso a destra) per calibrare l'area OCR.

### ⌨️ 2. Tasto Rapido Hardware Globale (`GetAsyncKeyState`)
- **Ascolto a Livello Kernel Windows**: ignora blocchi da anti-cheat (Easy Anti-Cheat) o isolamento dei permessi (UIPI). Funziona anche quando Albion Online è in primo piano, a schermo intero o eseguito come amministratore.
- **Configurabile da Menu**: puoi selezionare `F10`, `F4`, `F6`, `F8`, `F9`, `F11`, `F12`, `PAUSE` o `INSERT` (perfetto per tastiere da gaming e laptop senza dover premere `Fn`).
- **Feedback Acustico Istantaneo**: emette un segnale acustico (bip) differente all'avvio e all'arresto per sapere subito che il comando è stato ricevuto.

### 🛡️ 3. Umanizzazione & Anti-Detection
- Movimento naturale del mouse tramite curve cubiche di Bézier con velocità variabile.
- Ritardi a distribuzione gaussiana casuale con jitter ±15%.
- Digitazione numerica umana con intervalli casuali tra i caratteri.
- Failsafe protetto da coordinate esterne.

---

## 🎮 Controlli Rapidi

| Tasto | Azione |
| :--- | :--- |
| **F1** | **Modalità Calibrazione Completa** (Click destro sugli elementi UI) |
| **F2** | Test: Riconoscimento "Prezzo Attuale" |
| **F3** | Test: Riconoscimento "Prezzo Medio" |
| **F4** | **Avvia / Ferma** il ciclo di vendita principale |
| **F5** | **Salta** solo l'oggetto corrente senza interrompere il ciclo |
| **Esc** | Annulla la calibrazione attiva |

---

## 🚀 Installazione e Avvio

1. Scarica l'eseguibile o clona il repository.
2. Assicurati che [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) sia installato.
3. Installa le dipendenze Python (se esegui da codice sorgente):
   ```bash
   pip install -r requirements.txt
   ```
4. Avvia l'applicazione:
   ```bash
   python AutoSeller.py
   ```
5. Premi **F1** per calibrare le coordinate sullo schermo, poi premi **F4** per avviare!

---

## 🧪 Test Suite

Per eseguire i test automatici:
```bash
pytest
============================= 19 passed in 0.33s ==============================
```

---

### 💬 Autore

Sviluppato da: **NobodySan97**  
Versione: **v2.0 Pro**
