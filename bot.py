import os
import json
import subprocess
import sys
import requests
import importlib
from telethon import TelegramClient, events
import asyncio
import time
import threading

# Конфигурация
CONFIG_FILE = "config.json"  # Файл конфигурации
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"  # URL для скачивания главного файла
DOWNLOADS_FOLDER = "/storage/emulated/0/Download/Telegram"  # Папка загрузок на Android

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
        # Получаем имя модуля и путь назначения
        module_name = os.path.basename(file_path).replace('.py', '')
        destination = os.path.join(os.getcwd(), module_name + '.py')

        # Если файл с таким именем уже существует, перезаписываем его
        if os.path.exists(destination):
            print(f"Модуль {module_name} уже существует, перезаписываем...")
            os.remove(destination)

        # Перемещаем файл в папку с ботом
        os.rename(file_path, destination)
        sys.path.append(os.getcwd())

        # Импортируем модуль
        importlib.import_module(module_name)
        print(f"Модуль {module_name} успешно установлен.")
        return True
    except Exception as e:
        print(f"Ошибка установки модуля: {e}")
        return False

# Функция для проверки новых файлов в папке загрузок
def check_for_new_modules():
    while True:
        # Получаем список файлов в папке загрузок
        files_in_downloads = os.listdir(DOWNLOADS_FOLDER)

        # Фильтруем только Python файлы
        py_files = [f for f in files_in_downloads if f.endswith('.py')]

        if py_files:
            for file_name in py_files:
                file_path = os.path.join(DOWNLOADS_FOLDER, file_name)
                print(f"Найден новый файл модуля: {file_path}")

                # Устанавливаем найденный модуль
                if install_module(file_path):
                    print(f"Модуль {file_name} успешно установлен.")
                else:
                    print(f"Не удалось установить модуль {file_name}.")

                # Удаляем файл после установки (если нужно)
                os.remove(file_path)
                print(f"Файл {file_name} удален после установки.")

        # Ожидаем 10 секунд перед следующей проверкой
        time.sleep(10)

# Основная логика бота
async def main():
    # Обновляем главный файл
    update_main_file()

    # Начинаем авторизацию
    await client.start(PHONE_NUMBER)
    print("Бот авторизован и запущен!")

    # Запуск бота
    await client.run_until_disconnected()

# Запускаем цикл проверки файлов в отдельном потоке
def start_file_checking():
    check_for_new_modules()

if __name__ == "__main__":
    # Запускаем проверку файлов в фоновом потоке
    threading.Thread(target=start_file_checking, daemon=True).start()

    # Запускаем асинхронную основную логику бота
    asyncio.run(main())
