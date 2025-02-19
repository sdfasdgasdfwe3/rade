import os
import asyncio
import json
import sqlite3
from telethon import TelegramClient, errors

# Автообновление репозитория (не трогает сессию)
os.system('git pull')

CONFIG_FILE = "config.json"
SESSION_FILE = "session.session"

def load_or_create_config():
    """Загружает API-данные из файла или запрашивает у пользователя и создает файл."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    print("Файл config.json не найден. Создаю новый...")

    config = {
        "api_id": int(input('Введите api_id: ')),
        "api_hash": input('Введите api_hash: '),
        "phone_number": input('Введите номер телефона: ')
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

    print("Конфигурация сохранена в config.json.")
    return config

def unlock_sqlite_session():
    """Проверяет, заблокирована ли база данных сессии, и снимает блокировку без удаления файла."""
    if os.path.exists(SESSION_FILE):
        try:
            conn = sqlite3.connect(SESSION_FILE)
            conn.execute("PRAGMA journal_mode=WAL;")  # Переключаем в WAL-режим
            conn.execute("PRAGMA busy_timeout = 5000;")  # Устанавливаем таймаут ожидания
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"Ошибка при разблокировке сессии: {e}")

# Загружаем API-данные
config = load_or_create_config()

# Снимаем блокировку сессии перед запуском бота
unlock_sqlite_session()

# Создаем клиент
client = TelegramClient("session", config["api_id"], config["api_hash"])

async def authorize():
    """Функция авторизации в Telegram."""
    await client.connect()

    if await client.is_user_authorized():
        print("Вы уже авторизованы. Запускаем бота...")
        return True

    print("Вы не авторизованы. Начинаем процесс авторизации...")

    try:
        await client.send_code_request(config["phone_number"])
        code = input('Введите код из Telegram: ')
        await client.sign_in(config["phone_number"], code)

    except errors.SessionPasswordNeededError:
        password = input('Введите пароль 2FA: ')
        await client.sign_in(password=password)

    except errors.AuthRestartError:
        print("Telegram требует перезапуска авторизации. Повторяем попытку...")
        await client.send_code_request(config["phone_number"])
        code = input('Введите код из Telegram: ')
        await client.sign_in(config["phone_number"], code)

    except Exception as e:
        print(f'Ошибка авторизации: {e}')
        return False

    print("Успешная авторизация!")
    return True

async def main():
    if await authorize():
        print("Бот работает...")
        try:
            await client.run_until_disconnected()
        except Exception as e:
            print(f"Ошибка в работе бота: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Бот остановлен пользователем.")
    finally:
        client.disconnect()
        loop.close()
