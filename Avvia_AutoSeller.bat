@echo off
title Albion Auto Market Seller v2.0 Pro
cd /d "%~dp0"
python AutoSeller.py
if %errorlevel% neq 0 (
    echo.
    echo Si e' verificato un errore durante l'avvio.
    pause
)
