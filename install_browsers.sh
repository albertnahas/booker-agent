#!/bin/bash
set -e

# Install playwright browsers (particularly chromium)
python -m playwright install chromium

echo "Playwright browsers installed successfully!"
