@echo off
REM NUEVO: INICIA EL SERVICIO DE GRAFICAS CON EL AMBIENTE VIRTUAL (PUERTO 5000)
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python app.py
