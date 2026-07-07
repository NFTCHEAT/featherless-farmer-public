#!/bin/bash
set -e
echo "=== Установка зависимостей ==="
pip install -r requirements.txt
echo "=== Установка Chromium ==="
playwright install chromium
echo "=== Системные зависимости Playwright ==="
playwright install-deps chromium 2>/dev/null || apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2
echo "=== Готово! Запусти: bash run.sh ==="
