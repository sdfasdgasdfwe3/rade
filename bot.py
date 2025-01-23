import os
import subprocess
import time
import json
import asyncio
import requests  # Добавим импорт библиотеки requests
from telethon import TelegramClient, events

# Конфигурация
CONFIG_FILE = "config.json"  # Файл конфигурации
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"  # URL для скачивания главного файла
DOWNLOADS_FOLDER = "/storage/emulated/0/Download/Telegram/"  # Папка загрузок на Android

# Получаем данные конфигурации
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    API_ID = config.get("API_ID")
    API_HASH = config.get("API_HASH")
    PHONE_NUMBER = config.get("PHONE_NUMBER")
else:
    API_ID = input("Введите API_ID: ")
    API_HASH = input("Введите API_HASH: ")
    PHONE_NUMBER = input("Введите номер телефона: ")
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({"API_ID": API_ID, "API_HASH": API_HASH, "PHONE_NUMBER": PHONE_NUMBER}, f)

# Путь для сессии
SESSION_FILE = f"session_{PHONE_NUMBER.replace('+', '').replace('-', '')}"

# Устанавливаем клиента Telegram
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Функция для обновления главного файла
def update_main_file():
    """
    Обновляет главный файл bot.py из репозитория GitHub.
    """
    try:
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            main_file_path = os.path.abspath(__file__)
            # Скачиваем новый файл bot.py только если это основной файл
            if os.path.basename(main_file_path) == 'bot.py':
                with open(main_file_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("Главный файл bot.py обновлен.")
            else:
                print("Игнорируем обновление для не-основного файла.")
        else:
            print(f"Ошибка при скачивании обновления: {response.status_code}")
    except Exception as e:
        print(f"Ошибка обновления файла: {e}")

# Функция для авторизации
async def authorize():
    """
    Авторизует бота через Telegram.
    """
    try:
        # Пытаемся авторизовать клиента
        await client.start(PHONE_NUMBER)
        print("Авторизация прошла успешно.")
    except Exception as e:
        print(f"Ошибка при авторизации: {e}")
        return False
    return True

# Функция для перемещения файлов с проверкой
def move_telegram_files():
    """
    Перемещает файлы из папки Telegram в папку Termux и проверяет успешность перемещения.
    """
    try:
        # Указываем исходную и целевую директории
        SOURCE_DIR = "/storage/emulated/0/Android/data/org.telegram.messenger/files/"
        DEST_DIR = "~/storage/downloads/"

        # Сканируем папку с загрузками Telegram
        for file in os.listdir(SOURCE_DIR):
            file_path = os.path.join(SOURCE_DIR, file)
            dest_path = os.path.join(DEST_DIR, file)

            # Перемещаем файл
            if os.path.isfile(file_path):
                os.rename(file_path, dest_path)

                # Проверяем, был ли файл перемещен
                if os.path.exists(dest_path) and not os.path.exists(file_path):
                    print(f"Файл {file} успешно перемещен.")
                else:
                    print(f"Ошибка при перемещении файла {file}.")
    except Exception as e:
        print(f"Ошибка при перемещении файлов: {e}")

# Основная логика бота
async def main():
    # Обновляем главный файл
    update_main_file()

    # Авторизация в Telegram
    if not await authorize():
        return  # Если авторизация не удалась, выходим

    print("Бот авторизован и запущен!")

    # Запуск перемещения файлов с проверкой
    move_telegram_files()

    # Запуск бота
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
