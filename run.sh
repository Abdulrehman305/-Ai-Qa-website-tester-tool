#!/usr/bin/env bash
set -e
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m playwright install
echo "Setup complete. Run tests with: pytest"