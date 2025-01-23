import os
import sys
import json
import requests
import importlib
import time
import asyncio
from telethon import TelegramClient, events
from inotify.adapters import Inotify
from inotify.constants import IN_CLOSE_WRITE  # Импортируем правильную константу

# Конфигурация
CONFIG_FILE = "config.json"  # Файл конфигурации
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"  # URL для скачивания главного файла
DOWNLOADS_FOLDER = "/storage/emulated/0/Download/Telegram/Download/"  # Папка загрузок на Android

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
    Обновляет главный файл bot.py из репозитория GitHub
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

# Функция для установки модуля
def install_module(file_path):
    """
    Устанавливает Python-модуль из .py файла.
    """
    try:
        module_name = os.path.basename(file_path).replace('.py', '')
        destination = os.path.join(os.getcwd(), module_name + '.py')

        # Перемещаем файл из папки загрузок в рабочую директорию
        print(f"Перемещаем файл из {file_path} в {destination}")
        os.rename(file_path, destination)

        # Добавляем путь в sys.path
        sys.path.append(os.getcwd())

        # Попытка импорта модуля
        print(f"Пытаемся импортировать модуль {module_name}...")
        importlib.import_module(module_name)
        print(f"Модуль {module_name} установлен успешно.")
        return True
    except Exception as e:
        print(f"Ошибка установки модуля: {e}")
        return False

# Функция для мониторинга загрузок с использованием inotify
def monitor_downloads():
    """
    Периодически проверяет папку загрузок на наличие новых файлов .py
    """
    inotify = Inotify()
    print(f"Начат мониторинг папки: {DOWNLOADS_FOLDER}")
    inotify.add_watch(DOWNLOADS_FOLDER, mask=IN_CLOSE_WRITE)  # Используем правильную константу IN_CLOSE_WRITE

    print("Начат мониторинг загрузок...")

    for event in inotify.event_gen(yield_nones=False):
        (_, event_type, path, _) = event
        print(f"Обработано событие: {event_type}, файл: {path}")

        if event_type == 'IN_CLOSE_WRITE' and path.endswith('.py'):
            print(f"Найден новый файл: {path}")
            if install_module(path):
                print(f"Модуль {path} установлен успешно.")
                os.remove(path)  # Удаляем файл после установки
            else:
                print(f"Ошибка установки модуля {path}")
        else:
            print(f"Пропущен файл: {path}, не является .py или не IN_CLOSE_WRITE")

# Основная логика бота
async def main():
    # Обновляем главный файл
    update_main_file()

    # Начинаем авторизацию
    await client.start(PHONE_NUMBER)
    print("Бот авторизован и запущен!")

    # Запускаем мониторинг загрузок в отдельном потоке
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, monitor_downloads)

    # Запуск бота
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
