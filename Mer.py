import os
import shutil
import subprocess
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Путь к файлу в Downloads
download_path = "/storage/emulated/0/Download/install_module.py"
# Путь к домашней папке Termux
termux_path = os.path.expanduser("~") + "/install_module.py"
# Путь для хранения данных авторизации
auth_file_path = os.path.expanduser("~") + "/telegram_auth.session"

# Ваши данные Telegram API (получите на https://my.telegram.org)
API_ID = "your_api_id"
API_HASH = "your_api_hash"

# Функция для перемещения файла
def move_file():
    try:
        # Проверяем, существует ли файл в папке Downloads
        if os.path.exists(download_path):
            # Перемещаем файл в папку Termux
            shutil.move(download_path, termux_path)
            print(f"File moved to {termux_path}")
        else:
            print(f"File not found at {download_path}")
    except Exception as e:
        print(f"Error moving file: {e}")

# Функция для установки модуля
def install_module():
    try:
        # Попытаться импортировать модуль
        import requests
        print(f"Module 'requests' is already installed.")
    except ImportError:
        # Если модуль не найден, установить его
        print(f"Module 'requests' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print(f"Module 'requests' installed successfully.")

# Функция для авторизации в Telegram
def telegram_auth():
    # Создаём TelegramClient
    client = TelegramClient(auth_file_path, API_ID, API_HASH)

    try:
        # Подключаемся к Telegram
        client.connect()

        # Если пользователь не авторизован
        if not client.is_user_authorized():
            print("You are not authorized in Telegram.")
            phone_number = input("Enter your phone number (with country code): ")

            # Отправляем код подтверждения
            client.send_code_request(phone_number)

            # Вводим код подтверждения
            code = input("Enter the code you received: ")

            # Входим в аккаунт
            try:
                client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                # Если Telegram запрашивает пароль 2FA
                password = input("Your 2FA password: ")
                client.sign_in(password=password)

            print("Authorization successful!")
        else:
            print("Already authorized in Telegram.")

        # Возвращаем клиента для дальнейшего использования
        return client
    except Exception as e:
        print(f"Error during Telegram authorization: {e}")
    finally:
        client.disconnect()

# Основная логика
def main():
    # Перемещаем файл в домашнюю папку Termux
    move_file()

    # Устанавливаем модуль
    install_module()

    # Авторизация в Telegram
    telegram_auth()

if __name__ == "__main__":
    main()
