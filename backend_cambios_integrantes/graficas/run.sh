#!/usr/bin/env bash
# NUEVO: INICIA EL SERVICIO DE GRAFICAS CON EL AMBIENTE VIRTUAL (PUERTO 5000)
cd "$(dirname "$0")"
source .venv/bin/activate
python app.py
