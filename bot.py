import os
import json
import sys
import requests
import importlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from telethon import TelegramClient, events
import asyncio

# Конфигурация
CONFIG_FILE = "config.json"  # Файл конфигурации
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"  # URL для скачивания главного файла
DOWNLOADS_FOLDER = "/storage/emulated/0/Download/Telegram/"  # Папка загрузок на Android
MODULES_FOLDER = "/data/data/com.termux/files/home/rade/"  # Папка для модулей

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

# Модуль для установки модуля
def install_module(file_path):
    """
    Устанавливает Python-модуль из .py файла.
    """
    try:
        module_name = os.path.basename(file_path).replace('.py', '')
        destination = os.path.join(MODULES_FOLDER, module_name + '.py')

        # Перемещаем файл в папку для модулей
        os.rename(file_path, destination)

        # Загружаем модуль
        sys.path.append(MODULES_FOLDER)
        importlib.import_module(module_name)
        print(f"Модуль {module_name} установлен успешно.")
        return True
    except Exception as e:
        print(f"Ошибка установки модуля: {e}")
        return False

# Проверка и обновление главного файла
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

# Обработчик скачанных файлов
def download_and_install(file_path):
    """ Скачивает и устанавливает модуль из скачанного файла """
    if install_module(file_path):
        print(f"Модуль {file_path} успешно установлен.")
    else:
        print(f"Ошибка при установке модуля из {file_path}.")

# Обработчик событий для watchdog
class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        """ Когда появляется новый файл, скачиваем и устанавливаем его как модуль """
        if event.is_directory:
            return
        if event.src_path.endswith('.py'):
            print(f"Обнаружен новый файл: {event.src_path}")
            # Устанавливаем новый модуль
            download_and_install(event.src_path)

# Мониторим папку для скачанных файлов
def start_watching():
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS_FOLDER, recursive=False)
    observer.start()
    print(f"Мониторинг папки {DOWNLOADS_FOLDER} для новых файлов...")
    
    try:
        while True:
            # Бот будет работать и проверять изменения
            asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Основная логика бота
async def main():
    # Обновляем главный файл
    update_main_file()

    # Начинаем авторизацию
    await client.start(PHONE_NUMBER)
    print("Бот авторизован и запущен!")

    # Запускаем мониторинг папки загрузок
    start_watching()

if __name__ == "__main__":
    asyncio.run(main())
