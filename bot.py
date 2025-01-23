import os
import json
import sys
import importlib
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from telethon import TelegramClient, events
import asyncio

# Конфигурация
API_ID = 'YOUR_API_ID'  # Замените на ваш API_ID
API_HASH = 'YOUR_API_HASH'  # Замените на ваш API_HASH
PHONE_NUMBER = 'YOUR_PHONE_NUMBER'  # Замените на ваш номер телефона
DOWNLOADS_FOLDER = '/storage/emulated/0/Download/Telegram/'  # Папка для сохранения файлов
MODULES_FOLDER = '/data/data/com.termux/files/home/rade/'  # Папка для модулей, где будут храниться скачанные файлы

# Создаем сессию Telegram
SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}'
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Обработчик скачанных файлов
def install_module(file_path):
    """ Устанавливает Python-модуль из .py файла """
    try:
        module_name = os.path.basename(file_path).replace('.py', '')
        destination = os.path.join(MODULES_FOLDER, module_name + '.py')

        # Перемещаем файл в нужную папку
        os.rename(file_path, destination)

        # Загружаем модуль
        sys.path.append(MODULES_FOLDER)
        importlib.import_module(module_name)
        print(f"Модуль {module_name} установлен успешно.")
        return True
    except Exception as e:
        print(f"Ошибка установки модуля: {e}")
        return False

# Обработчик событий для watchdog
class DownloadHandler(FileSystemEventHandler):
    def on_created(self, event):
        """ Когда появляется новый файл, скачиваем и устанавливаем его как модуль """
        if event.is_directory:
            return
        if event.src_path.endswith('.py'):
            print(f"Обнаружен новый файл: {event.src_path}")
            # Устанавливаем новый модуль
            install_module(event.src_path)

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

# Основная логика
async def main():
    await client.start(PHONE_NUMBER)
    print("Бот авторизован и отслеживает новые файлы...")

    # Запускаем мониторинг папки загрузок
    start_watching()

if __name__ == "__main__":
    asyncio.run(main())
