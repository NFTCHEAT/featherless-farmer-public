"""
bot.py — Telegram-бот-триггер для фарма ключей featherless НА ЛЕТУ.
"""
import os
import random
import string
import threading
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

import telebot
from telebot import types

from mail_providers import pick_provider
from register import run_registration

# ========== ДАННЫЕ БЕРУТСЯ ИЗ .env ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
# ============================================

KEYS_FILE = "keys.txt"
HEADLESS = True

bot = telebot.TeleBot(BOT_TOKEN)

_busy = threading.Lock()


def _random_password(n=14):
    chars = string.ascii_letters + string.digits
    return "Aa1" + "".join(random.choices(chars, k=n - 3))


def _save_key(email, key, provider_name):
    # Считаем сколько уже ключей
    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            count = sum(1 for _ in f) + 1
    except FileNotFoundError:
        count = 1
    line = f"{count:03d}\t{datetime.now().isoformat(timespec='seconds')}\t{email}\t{key}\n"
    with open(KEYS_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    return count


def farm_one_key():
    _log("Создаю временную почту...")
    provider = pick_provider()
    email, ctx = provider.create()
    _log(f"Почта: {email}")
    pw = _random_password()
    _log(f"Пароль: {pw}")
    _log("=== Запуск регистрации ===")
    key = run_registration(email, pw, ctx, provider, headless=HEADLESS)
    if key:
        num = _save_key(email, key, provider.name)
        _log(f"=== КЛЮЧ #{num} ПОЛУЧЕН: {key} ===")
        _log(f"=== Сохранён в {KEYS_FILE} ===")
    else:
        _log("=== НЕ УДАЛОСЬ ПОЛУЧИТЬ КЛЮЧ ===")
    return key, email


def _keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🔑 Новый ключ")
    return kb


def _log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def _is_owner(message):
    return OWNER_ID == 0 or message.chat.id == OWNER_ID


def _run_and_reply(chat_id):
    _log("Запрос от Telegram — запускаю фарм...")
    try:
        key, email = farm_one_key()
        if key:
            _log("Отправляю ключ в Telegram...")
            bot.send_message(chat_id, "✅ Готово! Твой ключ:")
            bot.send_message(chat_id, f"Email: `{email}`", parse_mode="Markdown")
            bot.send_message(chat_id, f"`{key}`", parse_mode="Markdown", reply_markup=_keyboard())
            _log("Ключ отправлен")
        else:
            bot.send_message(
                chat_id,
                "❌ Не получилось на этом прогоне.\n"
                "Проверь логи или жми ещё раз.",
                reply_markup=_keyboard(),
            )
    except Exception as e:
        _log(f"ОШИБКА: {type(e).__name__}: {e}")
        bot.send_message(chat_id, f"⚠️ {type(e).__name__}: {e}", reply_markup=_keyboard())
    finally:
        _busy.release()


@bot.message_handler(commands=["start"])
def start(message):
    if not _is_owner(message):
        bot.reply_to(message, "Доступ только у владельца.")
        return
    bot.send_message(
        message.chat.id,
        "Привет! Я запускаю фарм ключа featherless по кнопке 🐸\n"
        f"Твой chat_id: {message.chat.id}\n\n"
        "Жми «🔑 Новый ключ» — я зарегаю акк и пришлю свежий ключ (~2-3 мин).",
        reply_markup=_keyboard(),
    )


@bot.message_handler(func=lambda m: m.text == "🔑 Новый ключ")
def new_key(message):
    if not _is_owner(message):
        return
    if not _busy.acquire(blocking=False):
        bot.send_message(message.chat.id, "⏳ Уже фармлю ключ, подожди немного...", reply_markup=_keyboard())
        return
    bot.send_message(message.chat.id, "⏳ Запускаю фарм... жди 2-3 мин, пришлю ключ сюда.")
    threading.Thread(target=_run_and_reply, args=(message.chat.id,), daemon=True).start()


if __name__ == "__main__":
    if not BOT_TOKEN:
        raise SystemExit("[!] Заполни .env: впиши BOT_TOKEN, OWNER_ID, CAPZY_KEY")
    print("[bot] запущен, слушаю Telegram... (Ctrl+C чтобы остановить)")
    bot.infinity_polling(skip_pending=True)
