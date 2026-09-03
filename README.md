[![Build Windows Executable](https://github.com/NobodySan97/AlbionOnline-AutoMarketSeller/actions/workflows/main.yml/badge.svg)](https://github.com/NobodySan97/AlbionOnline-AutoMarketSeller/actions/workflows/main.yml) ![Downloads](https://img.shields.io/github/downloads/NobodySan97/AlbionOnline-AutoMarketSeller/total?style=for-the-badge&logo=github&color=green)

# **Albion Online - Auto Market Seller v2.0 Pro**

Strumento desktop avanzato per l'automazione delle vendite sul mercato di Albion Online. Riconosce i prezzi e le medie di mercato tramite OCR, applica strategie di undercut intelligenti ed emula gli input umani con curve di Bézier e ritardi gaussiani per la massima affidabilità e naturalezza.

---

## 🎯 Nuove Funzionalità & Miglioramenti v2.0

### 💰 1. Strategie di Prezzo Avanzate
- **Undercut 1 Silver (`-1 Silver`)**: Imposta il prezzo a `prezzo_minimo - 1` silver per essere in testa all'ordine senza tagliare inutilmente il margine di profitto.
- **Sconto Percentuale (`%`)**: Applica una percentuale di sconto configurabile (es. 90% del prezzo o della media).
- **Fasce Dinamiche (`Tiered`)**:
  - *Oggetti di alto valore (> 1.000.000 Silver)*: Undercut di 1 Silver.
  - *Oggetti medi (100.000 - 1.000.000 Silver)*: Sconto del 5%.
  - *Oggetti economici (< 100.000 Silver)*: Sconto standard configurabile (es. 10%).
- **Prezzo Minimo di Sicurezza (`Floor Price`)**: Soglia minima al di sotto della quale nessun oggetto verrà mai piazzato.
- **Protezione Undercut Troll / OCR Anomaly**: Riconosce prezzi anomali (es. 1 silver listing o letture errate) e ricorre automaticamente al prezzo medio di mercato.

---

### 🛡️ 2. Umanizzazione Input & Anti-Pattern
- **Movimenti del Mouse con Curve di Bézier**: Il cursore non si muove in linea retta o istantaneamente, ma segue curve fluide con accelerazione e decelerazione naturale.
- **Ritardi a Distribuzione Gaussiana**: Tempi di reazione tra click e azioni modellati secondo distribuzioni normali.
- **Digitazione Naturale**: Intervalli variabili e micro-pause realistiche durante la digitazione dei numeri.

---

### 📊 3. Dashboard Statistiche & Esportazione CSV
- **Metriche in Tempo Reale**:
  - 🏷️ **Ordini Creati**: Conteggio totale ordini inseriti.
  - 💰 **Totale Silver Piazzato**: Valore stimato totale a mercato (in K, M o intero).
  - 📈 **Prezzo Medio per Ordine**: Media valore singolo ordine.
  - ⏱️ **Tempo Attivo**: Timer della sessione corrente.
- **Esportazione CSV**: Salva un report completo di tutte le vendite piazzate con timestamp, prezzo rilevato, strategia e prezzo finale.

---

### 🎨 4. Interfaccia Grafica Moderna (CustomTkinter)
- Look dark in stile Windows 11 con schede dedicate: **Dashboard**, **Prezzo & Strategia**, **Anti-Bot & Input**, **Log Attività**.
- Supporto multilingua completo (**Italiano** ed **Inglese**).
- Gestione DPI automatica per schermi ad alta risoluzione (1080p, 1440p, 4K).

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
