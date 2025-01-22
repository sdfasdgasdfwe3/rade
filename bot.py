import os
import importlib
import subprocess
import sys
import requests
from telethon import TelegramClient, events

# Данные авторизации
api_id = 123456  # Замените на свой API ID
api_hash = "your_api_hash"  # Замените на свой API Hash
phone = "your_phone_number"  # Замените на свой номер телефона

# Папка для хранения модулей
modules_path = "modules"

# Путь к файлу сессии
session_file = "user_session"  # Уникальное имя сессии (можно добавить номер телефона или имя пользователя)

# Путь к главному файлу (bot.py)
bot_file = "bot.py"

# GitHub URL для загрузки последней версии bot.py
GITHUB_RAW_URL = "https://raw.githubusercontent.com/yourusername/yourrepo/main/bot.py"  # Обновите URL

# Список зависимостей
DEPENDENCIES = ["telethon", "tinydb", "requests"]

# Создаем клиента с указанием имени сессии
client = TelegramClient(session_file, api_id, api_hash)

# Установка зависимостей
def install_dependencies():
    print("Проверяем зависимости...")
    for package in DEPENDENCIES:
        try:
            __import__(package)
            print(f"Библиотека '{package}' уже установлена.")
        except ImportError:
            print(f"Устанавливаем библиотеку '{package}'...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print("Все зависимости установлены.")

# Функция для обновления репозитория и перезаписи главного файла, но с сохранением сессии
def update_repository():
    try:
        print("Обновление репозитория...")

        # Обновляем репозиторий (git pull)
        subprocess.run(["git", "pull", "origin", "main"], check=True)

        # Убедимся, что файл сессии не будет перезаписан
        if os.path.exists(session_file):
            print("Сессия авторизации сохранена.")
        else:
            print("Ошибка: файл сессии не найден!")

        print("Репозиторий успешно обновлен!")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при обновлении репозитория: {e}")

# Функция для скачивания файла с GitHub и замены локальной копии
def update_bot_file_from_github():
    try:
        print(f"Загружаем {bot_file} из GitHub...")
        
        # Скачать файл с указанного URL
        response = requests.get(GITHUB_RAW_URL)
        
        # Проверка успешности загрузки
        if response.status_code == 200:
            with open(bot_file, "wb") as f:
                f.write(response.content)
            print(f"{bot_file} успешно обновлен из GitHub!")
        else:
            print(f"Ошибка загрузки файла: {response.status_code}")
    
    except Exception as e:
        print(f"Ошибка при обновлении файла с GitHub: {e}")

# Функция для загрузки доступных модулей
def load_modules():
    modules = []
    if not os.path.exists(modules_path):
        os.makedirs(modules_path)
    for file in os.listdir(modules_path):
        if file.endswith(".py"):
            module_name = file[:-3]  # Убираем .py
            modules.append(module_name)
    return modules

# Загрузка и выполнение команд
async def handle_message(event):
    text = event.raw_text
    modules = load_modules()

    for module_name in modules:
        module = importlib.import_module(f"{modules_path}.{module_name}")
        if hasattr(module, "handle_command"):
            await module.handle_command(client, event, text)

# Обработчик сообщений
@client.on(events.NewMessage)
async def on_new_message(event):
    await handle_message(event)

# Основная логика
async def main():
    # Устанавливаем зависимости
    install_dependencies()

    # Обновляем файл bot.py с GitHub
    update_bot_file_from_github()

    # Обновляем репозиторий и перезаписываем файлы
    update_repository()

    # Проверяем, что номер телефона указан
    if not phone or not isinstance(phone, str):
        print("Ошибка: номер телефона не указан или имеет неверный формат. Пожалуйста, укажите его в переменной 'phone'.")
        return

    # Если сессия не существует, нужно пройти авторизацию
    await client.start(phone)
    print("Бот запущен и авторизация завершена!")

    # Запуск бота и ожидание новых сообщений
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Запуск асинхронного метода
    client.loop.run_until_complete(main())
