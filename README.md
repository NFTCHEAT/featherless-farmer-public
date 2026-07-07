╔══════════════════════════════════════════════╗
║       Featherless Key Farmer Бот             ║
║  
Публичная версия                       ║
╚══════════════════════════════════════════════╝

Всё что нужно — заполнить .env и запустить.
Скрипты (.py) трогать НЕ НАДО — данные подтянутся из .env автоматом.

━━━ 1. ПОЛУЧИТЬ ДАННЫЕ ━━━

BOT_TOKEN → @BotFather → /newbot → создай → скопируй токен
OWNER_ID  → @userinfobot → напиши /start → покажет твой ID
CAPZY_KEY → capzy.app → зарегайся → API → создай ключ

━━━ 2. ЗАПОЛНИТЬ .env ━━━

Открой файл .env и впиши:

BOT_TOKEN=123456789:AbCdEfGhIjKlMnOpQrStUvWxYz
OWNER_ID=123456789
CAPZY_KEY=capzy_твой_ключ_сюда

━━━ 3. ЗАПУСК ━━━

bash install.sh    (установит всё: pip + playwright + либы)
bash run.sh        (запустит бота, перезапустит при падении)

Или руками:
  pip install -r requirements.txt
  playwright install chromium
  playwright install-deps chromium
  python3 bot.py

━━━ ГОТОВО ━━━

Пиши боту в Telegram /start → жми "Новый ключ"
Через 2-3 минуты придёт ключ. Сохраняются в keys.txt.

