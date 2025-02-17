import os
import time
from telethon import TelegramClient

# Чтение данных авторизации
with open("config.txt", "r") as config_file:
    config = config_file.readlines()

API_ID = config[0].strip().split('=')[1]
API_HASH = config[1].strip().split('=')[1]
PHONE_NUMBER = config[2].strip().split('=')[1]

# Создание клиента для авторизации
client = TelegramClient('session_name', API_ID, API_HASH)

# Функция для авторизации
async def authorize():
    await client.start(phone=PHONE_NUMBER)
    print("Авторизация успешна!")

# Основная функция бота
async def main():
    await authorize()

    # Ваши действия с ботом
    print("Бот работает и готов к использованию.")
    
    # Периодически проверяем, что Termux открыт
    while True:
        try:
            time.sleep(60)  # Проверяем раз в минуту
        except KeyboardInterrupt:
            print("Закрытие бота...")
            await client.disconnect()
            break

# Запуск клиента
client.loop.run_until_complete(main())
