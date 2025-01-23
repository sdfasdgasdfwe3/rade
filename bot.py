import os
import subprocess
import time
import json
import asyncio
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

# Функция для запуска Bash-скрипта
def move_telegram_files():
    """
    Перемещает файлы из папки Telegram в папку Termux.
    """
    try:
        # Путь к Bash-скрипту
        script = """
        #!/bin/bash
        SOURCE_DIR="/storage/emulated/0/Android/data/org.telegram.messenger/files/"
        DEST_DIR="~/storage/downloads/"

        # Сканируем папку с загрузками Telegram
        for file in "$SOURCE_DIR"/*; do
          if [[ -f "$file" ]]; then
            mv "$file" "$DEST_DIR"
          fi
        done
        """
        
        # Создание временного скрипта для выполнения
        with open("/data/data/com.termux/files/home/move_telegram_files.sh", "w") as file:
            file.write(script)
        
        # Даем права на выполнение
        os.chmod("/data/data/com.termux/files/home/move_telegram_files.sh", 0o755)

        # Запускаем скрипт
        subprocess.run("/data/data/com.termux/files/home/move_telegram_files.sh", shell=True)
        print("Файлы из Telegram перемещены в папку Termux.")
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

    # Запуск перемещения файлов
    move_telegram_files()

    # Запуск бота
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
