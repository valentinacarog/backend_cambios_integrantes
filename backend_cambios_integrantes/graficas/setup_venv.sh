#!/usr/bin/env bash
# NUEVO: CREA EL AMBIENTE VIRTUAL E INSTALA LAS DEPENDENCIAS (LINUX / MAC)
set -e
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "LISTO. PARA INICIAR: ./run.sh"
