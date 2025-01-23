import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument

# Конфигурация
API_ID = 'your_api_id'  # Ваш API_ID
API_HASH = 'your_api_hash'  # Ваш API_HASH
PHONE_NUMBER = 'your_phone_number'  # Ваш номер телефона

# Папка для загрузки файлов
DOWNLOADS_FOLDER = "/storage/emulated/0/Download/Telegram/"

# Путь для сессии
SESSION_FILE = 'session'

# Устанавливаем клиента Telegram
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Обработчик реакции на сообщение
@client.on(events.MessageReactions)
async def reaction_handler(event):
    """
    Реагируем на реакции, например, на реакцию 👍 на сообщение с файлом.
    """
    if event.emoji == "👍":  # Проверка на нужную реакцию
        print(f"Реакция {event.emoji} на сообщение от {event.sender_id}")
        
        # Получаем информацию о сообщении, на которое поставлена реакция
        message = event.message
        print(f"Реакция поставлена под сообщением ID {message.id} от {message.sender_id}")

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
            else:
                print("Сообщение не содержит файл.")
        else:
            print("Сообщение не содержит файла.")

# Основная логика бота
async def main():
    # Начинаем авторизацию
    await client.start(PHONE_NUMBER)
    print("Бот авторизован и запущен!")

    # Запуск бота
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
