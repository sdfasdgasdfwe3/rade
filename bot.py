import os
import json
import subprocess
import sys
import requests
import importlib
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument
import asyncio

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

# Модуль для установки модуля
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

# Обработчик реакции на сообщение
@client.on(events.MessageReactions)
async def reaction_handler(event):
    """
    Реагируем на реакции, например, на реакцию 👍 на сообщение с файлом.
    """
    # Проверяем, что реакция соответствует нужной
    if event.emoji == "👍":  # Проверка на нужную реакцию
        print(f"Реакция {event.emoji} на сообщение от {event.sender_id}")

        # Получаем информацию о сообщении, на которое поставлена реакция
        message = event.message  # Объект сообщения, на которое поставили реакцию
        print(f"Реакция поставлена под сообщением ID {message.id} от {message.sender_id}")

        # Получаем текст сообщения
        print(f"Текст сообщения: {message.text}")

        # Проверяем, есть ли файл в сообщении
        if message.media:
            if isinstance(message.media, MessageMediaDocument):
                # Если это файл, то получаем его
                file = message.media.document
                file_name = file.attributes[0].file_name  # Получаем имя файла
                print(f"Имя файла: {file_name}")
                
                # Скачиваем файл в папку загрузок
                file_path = await event.download_media(DOWNLOADS_FOLDER)
                print(f"Файл {file_name} скачан в папку {DOWNLOADS_FOLDER}")

                # Устанавливаем модуль, если это python файл
                if file_name.endswith('.py'):
                    if install_module(file_path):
                        await event.reply("Модуль установлен и активирован!")
                    else:
                        await event.reply("Не удалось установить модуль.")
                else:
                    await event.reply(f"Файл {file_name} не является Python-модулем.")
            else:
                await event.reply("Сообщение не содержит файла.")
        else:
            await event.reply("Сообщение не содержит файла.")

# Основная логика бота
async def main():
    # Обновляем главный файл
    update_main_file()
    
    # Начинаем авторизацию
    await client.start(PHONE_NUMBER)
    print("Бот авторизован и запущен!")
    
    # Запуск бота
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
