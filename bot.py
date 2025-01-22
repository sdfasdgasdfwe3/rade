import os
import json
import subprocess
import sys
import requests
from telethon import TelegramClient, events
import asyncio
import shutil

# Папка для модулей в Termux
MODULES_PATH = "/data/data/com.termux/files/home/modules"

# Имя файла конфигурации
CONFIG_FILE = "config.json"

# Имя файла сессии будет формироваться на основе номера телефона
SESSION_FILE = None

# Значения по умолчанию для дополнительных параметров
DEFAULT_TYPING_SPEED = 0.1
DEFAULT_CURSOR = "|"

# Текущая версия скрипта
SCRIPT_VERSION = "1.0.0"

# GitHub URL для загрузки последней версии bot.py
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"

# Функция для установки зависимостей
def install_dependencies():
    print("Проверяем зависимости...")
    DEPENDENCIES = ["telethon", "requests"]
    for package in DEPENDENCIES:
        try:
            __import__(package)
            print(f"Библиотека '{package}' уже установлена.")
        except ImportError:
            print(f"Устанавливаем библиотеку '{package}'...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("Все зависимости установлены.")

# Проверяем наличие файла конфигурации
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        API_ID = config.get("API_ID")
        API_HASH = config.get("API_HASH")
        PHONE_NUMBER = config.get("PHONE_NUMBER")
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
                "PHONE_NUMBER": PHONE_NUMBER
            }, f)
        print("Данные успешно сохранены в конфигурации.")
    except Exception as e:
        print(f"Ошибка сохранения конфигурации: {e}")
        exit(1)

# Уникальное имя файла для сессии
SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}'

# Создаем клиента Telegram
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Функция для принудительного обновления скрипта из GitHub
def update_script():
    """Принудительно загружаем файл bot.py из GitHub и перезаписываем локальный файл."""
    try:
        print("Обновление скрипта из GitHub...")
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            # Получаем текст скрипта с GitHub
            remote_script = response.text
            current_file = os.path.abspath(__file__)

            # Перезаписываем файл bot.py
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(remote_script)
            print("Скрипт успешно обновлен из GitHub.")
        else:
            print(f"Не удалось скачать скрипт. Код ответа сервера: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при обновлении скрипта: {e}")

# Основная логика
async def main():
    print("Запуск бота...")
    try:
        # Устанавливаем зависимости
        print("Установка зависимостей...")
        install_dependencies()

        # Принудительное обновление скрипта
        print("Обновление скрипта...")
        update_script()

        # Если сессия не существует, проходим авторизацию
        print("Авторизация в Telegram...")
        await client.start(PHONE_NUMBER)
        print("Авторизация завершена!")

        print("Запуск бота...")
        await client.run_until_disconnected()

    except Exception as e:
        print(f"Произошла ошибка в main: {e}")
        # Логируем ошибку, чтобы она была видна

if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
