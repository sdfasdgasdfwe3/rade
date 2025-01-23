import os
import json
import subprocess
import sys
import requests
import importlib
from telethon import TelegramClient, events
import asyncio

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

# Функция для установки модуля
def install_module(file_path):
    """
    Устанавливает Python-модуль из .py файла.
    """
    try:
        module_name = os.path.basename(file_path).replace('.py', '')
        destination = os.path.join(os.getcwd(), module_name + '.py')
        
        if os.path.exists(destination):
            os.remove(destination)

        os.rename(file_path, destination)
        sys.path.append(os.getcwd())
        importlib.import_module(module_name)
        print(f"Модуль {module_name} успешно установлен.")
        return True
    except Exception as e:
        print(f"Ошибка установки модуля: {e}")
        return False

# Функция для проверки и обновления главного файла
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
                # Перезапуск бота после обновления главного файла
                restart_bot()
            else:
                print("Игнорируем обновление для не-основного файла.")
        else:
            print(f"Ошибка при скачивании обновления: {response.status_code}")
    except Exception as e:
        print(f"Ошибка обновления файла: {e}")

# Функция для перезапуска бота
def restart_bot():
    print("Перезапуск бота после обновления...")
    os.execv(sys.executable, ['python'] + sys.argv)

# Обработчик реакций на сообщения
@client.on(events.Reaction)
async def reaction_handler(event):
    # Определяем, на какую реакцию реагировать, например на 👍
    if event.emoji == "👍":
        # Путь к файлу модуля
        file_name = "your_module.py"  # Название модуля
        file_path = os.path.join(DOWNLOADS_FOLDER, file_name)

        # Проверяем, существует ли файл в папке загрузок
        if os.path.exists(file_path):
            print(f"Модуль найден: {file_path}")
            
            # Устанавливаем модуль
            if install_module(file_path):
                await event.reply("Модуль установлен и активирован!")
            else:
                await event.reply("Не удалось установить модуль.")
        else:
            await event.reply("Модуль не найден в папке загрузок.")

# Основная логика бота
async def main():
    # Обновляем главный файл перед запуском бота
    update_main_file()

    # Начинаем авторизацию
    await client.start(PHONE_NUMBER)
    print("Бот авторизован и запущен!")

    # Запуск бота
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
