import os
import json
import subprocess
import sys
import requests
import importlib
from telethon import TelegramClient, events
import asyncio
import importlib.util

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

# Функция для отмены локальных изменений
def reset_local_changes():
    """
    Отменяет все локальные изменения в репозитории.
    """
    try:
        print("Отмена локальных изменений...")
        subprocess.check_call(['git', 'checkout', '--', '.'])
        print("Локальные изменения отменены.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при отмене изменений: {e}")

# Функция для обновления репозитория
def update_repository():
    """
    Обновляет репозиторий, выполняет 'git pull'.
    """
    try:
        print("Обновление репозитория...")
        subprocess.check_call(['git', 'pull'])
        print("Репозиторий обновлен.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при обновлении репозитория: {e}")

# Функция для установки модулей из скачанных файлов
def install_module(file_path):
    """
    Устанавливает Python-модуль из .py файла.
    """
    try:
        module_name = os.path.basename(file_path).replace('.py', '')
        destination = os.path.join(os.getcwd(), module_name + '.py')
        os.rename(file_path, destination)
        sys.path.append(os.getcwd())
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

# Функция для перезапуска бота
def restart_bot():
    print("Перезапуск бота...")
    os.execv(sys.executable, ['python'] + sys.argv)

# Проверка установленных модулей
def get_installed_modules():
    installed_modules = []
    for dist in subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode().splitlines():
        installed_modules.append(dist.split('==')[0])
    return installed_modules

# Обработчик команд
@client.on(events.NewMessage(pattern="/modules"))
async def handler(event):
    installed_modules = get_installed_modules()
    response = "Установленные модули:\n" + "\n".join(installed_modules)
    await event.reply(response)

# Обработчик нового файла
@client.on(events.NewMessage)
async def file_handler(event):
    if event.file and event.file.name.endswith(".py"):
        # Скачиваем файл в папку загрузок
        print(f"Получен файл: {event.file.name}")
        
        # Путь для скачивания файла
        file_path = await event.download_media(DOWNLOADS_FOLDER)
        print(f"Файл скачан в папку: {file_path}")

        # Устанавливаем модуль
        if install_module(file_path):
            print(f"Модуль {file_path} успешно установлен.")
            # Перезапускаем бота после установки модуля
            restart_bot()
        else:
            print("Ошибка при установке модуля.")
            await event.reply("Ошибка при установке модуля.")

# Основная логика бота
async def main():
    # Отменяем локальные изменения
    reset_local_changes()
    
    # Обновляем репозиторий
    update_repository()
    
    # Обновляем главный файл
    update_main_file()

    # Начинаем авторизацию
    await client.start(PHONE_NUMBER)
    print("Бот авторизован и запущен!")
    
    # Запуск бота
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
