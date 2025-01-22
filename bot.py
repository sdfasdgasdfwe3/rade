import os
import json
import importlib
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

def update_script():
    """Принудительно загружаем файл bot.py из GitHub и перезаписываем локальный файл."""
    try:
        print("Обновление скрипта из GitHub...")

        # Получаем текущий путь скрипта
        current_file = os.path.abspath(__file__)

        # Проверка, что обновляем именно bot.py, а не другие файлы
        if not current_file.endswith("bot.py"):
            print("Этот файл не является bot.py, обновление не выполнено.")
            return

        # Загрузка последней версии скрипта с GitHub
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            remote_script = response.text

            # Перезаписываем файл bot.py
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(remote_script)
            print("Скрипт успешно обновлен из GitHub.")
        else:
            print(f"Не удалось скачать скрипт. Код ответа сервера: {response.status_code}")

    except Exception as e:
        print(f"Ошибка при обновлении скрипта: {e}")

# Обрабатываем событие загрузки файла
@client.on(events.NewMessage(pattern='/upload_module'))
async def handle_file(event):
    if event.file:
        # Получаем путь к загруженному файлу
        file_name = event.file.name
        file_path = f'/tmp/{file_name}'

        # Скачиваем файл
        await event.download(file_path)
        print(f"Файл {file_name} загружен.")

        # Перемещаем файл в папку с модулями
        target_path = os.path.join(MODULES_PATH, file_name)
        shutil.move(file_path, target_path)
        print(f"Модуль {file_name} перемещен в {MODULES_PATH}.")

        # Перезагружаем бота
        await client.send_message(event.chat_id, "Модуль установлен. Бот перезагружается...")
        os.execv(sys.executable, ['python'] + sys.argv)

# Отображение списка установленных модулей
@client.on(events.NewMessage(pattern='/list_modules'))
async def list_modules(event):
    try:
        modules = os.listdir(MODULES_PATH)
        if modules:
            await event.reply("Установленные модули:\n" + "\n".join(modules))
        else:
            await event.reply("Нет установленных модулей.")
    except Exception as e:
        await event.reply(f"Ошибка при получении списка модулей: {e}")

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

    # Если сессия не существует, проходим авторизацию
    await client.start(PHONE_NUMBER)
    print("Бот запущен и авторизация завершена!")

    # Запуск бота и ожидание новых сообщений
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
