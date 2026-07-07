#!/bin/bash
cd "$(dirname "$0")"
while true; do
    echo "[run.sh] Запуск bot.py ..."
    python3 -u bot.py
    rc=$?
    echo "[run.sh] bot.py упал (exit=$rc), перезапуск через 2 сек..."
    sleep 2
done
