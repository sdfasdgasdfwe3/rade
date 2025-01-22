import os
import json
import importlib
import subprocess
import sys
import requests
from telethon import TelegramClient, events

# Имя файла конфигурации
CONFIG_FILE = "config.json"

# Имя файла сессии будет формироваться на основе номера телефона
SESSION_FILE = None

# Значения по умолчанию для дополнительных параметров
DEFAULT_TYPING_SPEED = 0.1
DEFAULT_CURSOR = "|"

# Проверяем наличие файла конфигурации
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        API_ID = config.get("API_ID")
        API_HASH = config.get("API_HASH")
        PHONE_NUMBER = config.get("PHONE_NUMBER")
        typing_speed = config.get("typing_speed", DEFAULT_TYPING_SPEED)
        cursor_symbol = config.get("cursor_symbol", DEFAULT_CURSOR)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Ошибка чтения конфигурации: {e}. Попробуем запросить данные заново.")
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None
else:
    # Если файл не существует, запрашиваем данные у пользователя
    API_ID = None
    API_HASH = None
    PHONE_NUMBER = None

# Если данные конфигурации не заданы, запрашиваем их у пользователя
if not API_ID or not API_HASH or not PHONE_NUMBER:
    try:
        print("Пожалуйста, введите данные для авторизации в Telegram.")
        API_ID = int(input("Введите ваш API ID: "))
        API_HASH = input("Введите ваш API Hash: ").strip()
        PHONE_NUMBER = input("Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX): ").strip()

        # Сохраняем данные в файл конфигурации
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "API_ID": API_ID,
                "API_HASH": API_HASH,
                "PHONE_NUMBER": PHONE_NUMBER,
                "typing_speed": DEFAULT_TYPING_SPEED,
                "cursor_symbol": DEFAULT_CURSOR
            }, f)
        print("Данные успешно сохранены в конфигурации.")
    except Exception as e:
        print(f"Ошибка сохранения конфигурации: {e}")
        exit(1)

# Уникальное имя файла для сессии
SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}'

# Создаем клиента Telegram
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Функция установки зависимостей
def install_dependencies():
    print("Проверяем зависимости...")
    DEPENDENCIES = ["telethon", "tinydb", "requests"]
    for package in DEPENDENCIES:
        try:
            __import__(package)
            print(f"Библиотека '{package}' уже установлена.")
        except ImportError:
            print(f"Устанавливаем библиотеку '{package}'...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("Все зависимости установлены.")

# Пример команды для анимированного ввода текста
@client.on(events.NewMessage(pattern=r'p (.+)'))
async def animated_typing(event):
    """
    Команда для печатания текста с анимацией.
    """
    global typing_speed, cursor_symbol
    try:
        if not event.out:
            return

        text = event.pattern_match.group(1)
        typed_text = ""

        for char in text:
            typed_text += char
            await event.edit(typed_text + cursor_symbol)
            await asyncio.sleep(typing_speed)
    except Exception as e:
        print(f"Ошибка в обработчике текста: {e}")

# Основная логика
async def main():
    install_dependencies()
    # Если сессия не существует, проходим авторизацию
    await client.start(PHONE_NUMBER)
    print("Бот запущен и авторизация завершена!")

    # Запуск бота и ожидание новых сообщений
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
