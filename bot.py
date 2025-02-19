import os
import asyncio
from telethon import TelegramClient, errors

# Автоматически обновляем репозиторий
os.system('git pull')

# Запрашиваем данные у пользователя
api_id = int(input('Введите api_id: '))
api_hash = input('Введите api_hash: ')
phone_number = input('Введите номер телефона: ')

# Создаем клиент с сохранением сессии
client = TelegramClient('session', api_id, api_hash)

async def authorize():
    """Функция авторизации в Telegram."""
    await client.connect()

    if await client.is_user_authorized():
        print("Вы уже авторизованы. Запускаем бота...")
        return True

    print("Вы не авторизованы. Начинаем процесс авторизации...")

    try:
        await client.send_code_request(phone_number)
        code = input('Введите код из Telegram: ')
        await client.sign_in(phone_number, code)

    except errors.SessionPasswordNeededError:
        password = input('Введите пароль 2FA: ')
        await client.sign_in(password=password)

    except errors.AuthRestartError:
        print("Telegram требует перезапуска авторизации. Повторяем попытку...")
        await client.send_code_request(phone_number)
        code = input('Введите код из Telegram: ')
        await client.sign_in(phone_number, code)

    except Exception as e:
        print(f'Ошибка авторизации: {e}')
        return False

    print("Успешная авторизация!")
    return True

async def main():
    if await authorize():
        print("Бот работает...")
        await asyncio.Future()  # Бот работает бесконечно

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Бот остановлен пользователем.")
    finally:
        loop.close()
