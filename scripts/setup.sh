#!/usr/bin/env bash
# TARGET-X Environment Setup Script (macOS / Linux)
set -e

echo "========================================================="
echo "   TARGET-X: ENVIRONMENT SETUP & DEPENDENCY INSTALLATION"
echo "========================================================="

# 1. Python virtual environment
echo -e "\n[*] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2. Frontend dependencies
echo -e "\n[*] Installing Frontend dependencies..."
npm --prefix frontend install

# 3. Model Training & Evaluation
echo -e "\n[*] Training authentic TARGET-X model from scratch..."
python3 training/train.py
python3 training/evaluate.py

echo -e "\n[+] TARGET-X setup completed successfully!"
echo "[+] Start backend:  ./scripts/start_backend.sh"
echo "[+] Start frontend: ./scripts/start_frontend.sh"
