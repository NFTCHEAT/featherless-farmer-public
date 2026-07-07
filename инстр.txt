# Featherless Key Farmer

Автоматическая регистрация аккаунтов на featherless.ai и получение API-ключей через Telegram-бота.

---

## ⚡ Для знающих (кратко)

```bash
# 1. Распаковать
unzip featherless-farmer.zip && cd featherless-farmer

# 2. Зависимости
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium

# 3. Вписать токены в bot.py (строки 16-17):
#    BOT_TOKEN = "от @BotFather"
#    OWNER_ID = твой ID

# 4. Запустить
python3 bot.py
```

Что нужно: **BOT_TOKEN** (от @BotFather), **OWNER_ID** (от @userinfobot), **CAPZY_KEY** (от capzy.ai — начальный баланс дают при регистрации, ~60+ решений).

Без Telegram: `python3 main.py --count 1`

---

## 👶 Для новичков (пошаговая)

### Шаг 1. Установи Python

Проверь, есть ли Python на компьютере:

**Windows:** Открой Пуск → напиши `cmd` → запусти. Введи:
```
python --version
```
Если ошибка — скачай Python с https://python.org (галочку "Add Python to PATH" обязательно поставь).

**Mac:** Открой Terminal (Cmd+Пробел → Terminal). Введи:
```bash
python3 --version
```
Если нет — скачай с https://python.org.

**Linux (Ubuntu/Debian):**
```bash
python3 --version
sudo apt install python3 python3-pip
```

### Шаг 2. Распакуй архив

Найди файл `featherless-farmer.zip`, кликни правой кнопкой → "Извлечь всё". Или в терминале:

```bash
unzip featherless-farmer.zip
cd featherless-farmer
```

### Шаг 3. Установи зависимости

Открой терминал в папке `featherless-farmer` и выполни:

```bash
pip install -r requirements.txt
```

Если на Linux/Mac выходит ошибка про `pip`, попробуй:
```bash
pip3 install -r requirements.txt
```

### Шаг 4. Установи браузер

```bash
playwright install chromium
```

На Linux после этого выполни (ставит системные библиотеки для браузера):
```bash
playwright install-deps chromium
```

### Шаг 5. Получи BOT_TOKEN

1. Открой Telegram, найди @BotFather
2. Напиши `/newbot`
3. Придумай имя боту (например `My Key Farmer`)
4. Придумай username (обязательно заканчивается на `bot`, например `my_key_farmer_bot`)
5. @BotFather пришлёт токен — скопируй его (выглядит как `1234567890:ABCdefGHIjkl...`)

### Шаг 6. Получи свой Telegram ID

1. В Telegram найди @userinfobot
2. Напиши `/start`
3. Он покажет твой ID — запиши его (это число, например `123456789`)

### Шаг 7. Получи Capzy ключ

1. Зайди на https://capzy.ai
2. Зарегистрируйся (почта + пароль)
3. Подтверди почту
4. Зайди в Dashboard → API Keys → Create Key
5. Скопируй ключ (начинается с `capzy_`)
6. **При регистрации дают стартовый баланс** — хватит на ~60 решений капчи, ничего платить не нужно

### Шаг 8. Настрой бота

Открой файл `bot.py` в любом текстовом редакторе (Блокнот, Notepad++, VS Code). Найди строки 16-17 и впиши свои данные:

```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"   # твой токен от @BotFather
OWNER_ID = 123456789                                     # твой ID от @userinfobot
```

Потом открой `capzy_solver.py` (строка 6) и замени ключ на свой, если там стоит не твой:

```python
CAPZY_KEY = "capzy_твой_ключ_сюда"
```

### Шаг 9. Запусти бота

В терминале (в папке `featherless-farmer`):

```bash
python3 bot.py
```

Должно появиться: `[bot] запущен, слушаю Telegram...`

### Шаг 10. Пользуйся

1. Открой Telegram, найди своего бота (которого создал через @BotFather)
2. Напиши `/start`
3. Нажми кнопку **🔑 Новый ключ**
4. Жди 2-3 минуты — бот пришлёт готовый API-ключ

---

## 🖥 Запуск на сервере 24/7 (VPS)

Чтобы бот висел и работал даже когда ты закроешь терминал:

```bash
nohup python3 bot.py > bot.log 2>&1 &
```

**Проверить что работает:**
```bash
ps aux | grep bot.py
```

**Посмотреть логи:**
```bash
tail -f bot.log
```

**Остановить:**
```bash
kill $(pgrep -f bot.py)
```

---

## 🛠 Фарм без Telegram (CLI)

```bash
python3 main.py --count 5
```

Создаст 5 ключей подряд, сохранит в `keys.txt`.

Флаги:
- `--count N` — сколько ключей создать
- `--show` — показать окно браузера (для отладки)
- `--delay 30` — пауза между аккаунтами в секундах

---

## 📁 Файлы в архиве

| Файл | Зачем нужен |
|------|-------------|
| `bot.py` | Телеграм-бот. Запускаешь его → работает |
| `register.py` | Сама регистрация: открывает браузер, регает акк, верифицирует почту, создаёт ключ |
| `mail_providers.py` | Создаёт временные @gmail.com адреса (через emailnator.com) |
| `capzy_solver.py` | Решает Turnstile-капчу через Capzy |
| `main.py` | Запуск регистрации без Telegram (из консоли) |
| `requirements.txt` | Список библиотек (устанавливаются через `pip`) |
| `.env.example` | Пример настроек (необязательно, можно вписать напрямую в bot.py) |
| `keys.txt` | Сюда сохраняются полученные ключи (создаётся после первого запуска) |

## ❓ Частые вопросы

**Капча решается?** Да, через Capzy. При регистрации дают стартовый баланс — хватает на ~60+ ключей.

**Почта @gmail.com — как?** Через emailnator.com — там пул реальных Gmail-аккаунтов, бот использует dot-алиасы (`user.name+tag@gmail.com`). Бесплатно, без регистрации.

**Бот не запускается — "chromium not found"?** Забудь `playwright install chromium` и `playwright install-deps chromium`.

**Где взять API-ключ Capzy?** https://capzy.ai → регистрация → Dashboard → API Keys → Create Key.

**Ошибка "no X display"?** Ты на сервере без графики. Playwright работает headless, но нужны системные библиотеки: `playwright install-deps chromium`. Если не помогло, ставь `apt install libatk-bridge2.0-0 libgtk-3-0 libgbm1` (для Ubuntu/Debian).

**Ключи сохраняются?** Да, в файл `keys.txt` в папке с ботом.

