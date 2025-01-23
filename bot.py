import os
import json
import requests
from telethon import TelegramClient, events
import subprocess
import shutil
import sys

# Константы
CONFIG_FILE = "config.json"
SCRIPT_VERSION = "0.0.10"
DEFAULT_TYPING_SPEED = 1.5
DEFAULT_CURSOR = "▮"

# Загрузка данных конфигурации
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        API_ID = config.get("API_ID")
        API_HASH = config.get("API_HASH")
        PHONE_NUMBER = config.get("PHONE_NUMBER")
    except (json.JSONDecodeError, KeyError):
        print("Ошибка чтения конфигурации. Удалите файл config.json и попробуйте снова.")
        exit(1)
else:
    try:
        API_ID = int(input("Введите ваш API ID: "))
        API_HASH = input("Введите ваш API Hash: ").strip()
        PHONE_NUMBER = input("Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX): ").strip()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "API_ID": API_ID,
                "API_HASH": API_HASH,
                "PHONE_NUMBER": PHONE_NUMBER,
            }, f)
    except Exception as e:
        print(f"Ошибка сохранения конфигурации: {e}")
        exit(1)

# Создание клиента Telegram
SESSION_FILE = f"session_{PHONE_NUMBER.replace('+', '').replace('-', '')}"
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Функция для установки модуля или обработки файла
def handle_file(file_path):
    try:
        file_extension = os.path.splitext(file_path)[-1].lower()
        if file_extension in ['.whl', '.tar.gz', '.zip']:
            # Устанавливаем модуль через pip
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', file_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode == 0:
                return f"Модуль из {os.path.basename(file_path)} успешно установлен."
            else:
                return f"Ошибка установки: {result.stderr}"
        elif file_extension == '.py':
            # Перемещаем скрипт в директорию проекта
            dest_path = os.path.join(os.getcwd(), os.path.basename(file_path))
            shutil.move(file_path, dest_path)
            return f"Файл {os.path.basename(file_path)} успешно скопирован в директорию проекта."
        else:
            return f"Файл с расширением {file_extension} не поддерживается."
    except Exception as e:
        return f"Не удалось обработать файл: {str(e)}"

# Обработчик команды /up
@client.on(events.NewMessage(pattern='/up'))
async def upload_handler(event):
    if event.reply_to_msg_id:
        replied_message = await event.get_reply_message()
        if replied_message.file:
            # Скачиваем файл
            file_path = await replied_message.download_media()
            await event.reply(f"Файл {os.path.basename(file_path)} загружен. Обрабатываю...")
            result = handle_file(file_path)
            await event.reply(result)
        else:
            await event.reply("Ответьте на сообщение с файлом Python-модуля или скрипта, чтобы установить его.")
    else:
        await event.reply("Ответьте на сообщение с файлом Python-модуля или скрипта, чтобы установить его.")

# Автоматическая обработка файла, отправленного в избранное
@client.on(events.NewMessage)
async def auto_install_handler(event):
    if event.is_channel and event.chat_id == event.sender_id and event.file:
        # Скачиваем файл
        file_path = await event.download_media()
        await event.reply(f"Обнаружен файл в избранном: {os.path.basename(file_path)}. Обрабатываю...")
        result = handle_file(file_path)
        await event.reply(result)

async def main():
    await client.start(phone=PHONE_NUMBER)
    print(f"Успешно авторизованы как {PHONE_NUMBER}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
