import os
import asyncio
import json
from telethon import TelegramClient, errors

# Автоматически обновляем репозиторий (но не трогаем сессию)
os.system('git pull')

CONFIG_FILE = "config.json"
SESSION_FILE = "session"

def load_config():
    """Загружает API-данные из файла или запрашивает у пользователя."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    # Запрашиваем данные у пользователя
    config = {
        "api_id": int(input('Введите api_id: ')),
        "api_hash": input('Введите api_hash: '),
        "phone_number": input('Введите номер телефона: ')
    }

    # Сохраняем конфиг
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

    return config

# Загружаем API-данные
config = load_config()

# Создаем клиент с использованием файла сессии
client = TelegramClient(SESSION_FILE, config["api_id"], config["api_hash"])

async def authorize():
    """Функция авторизации в Telegram."""
    await client.connect()

    # Проверяем, есть ли активная сессия
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
            await client.run_until_disconnected()  # Бесконечный режим работы
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
