import os
from telethon import TelegramClient

# Автоматически обновляем репозиторий
os.system('git pull')

# Запрашиваем данные у пользователя
api_id = int(input('Введите api_id: '))
api_hash = input('Введите api_hash: ')
phone_number = input('Введите номер телефона: ')

# Создаем клиент с сохранением сессии
client = TelegramClient('session', api_id, api_hash)

async def main():
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Вы не авторизованы. Начинаем процесс авторизации...")
        await client.send_code_request(phone_number)
        code = input('Введите код из Telegram: ')
        
        try:
            await client.sign_in(phone_number, code)
        except Exception as e:
            if '2FA' in str(e):
                password = input('Введите пароль 2FA: ')
                await client.sign_in(password=password)
            else:
                print(f'Ошибка авторизации: {e}')
                return
        print("Успешная авторизация!")
    else:
        print("Вы уже авторизованы. Запускаем бота...")
    
    # Здесь можно добавить код для работы с Telegram

    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
