#!/bin/bash

# Устанавливаем необходимые зависимости
pkg update && pkg upgrade -y
pkg install python -y
pkg install git -y
pkg install python-pip -y

# Устанавливаем telethon для работы с Telegram
pip install telethon

# Переходим в директорию для бота
mkdir -p /data/data/com.termux/files/home/rade
cd /data/data/com.termux/files/home/rade

# Скачиваем последние файлы с репозитория
git clone https://raw.githubusercontent.com/sdfasdgasdfwe3/rade .

# Создаем конфигурационный файл с API-данными
echo "API_ID=your_api_id_here" > config.txt
echo "API_HASH=your_api_hash_here" >> config.txt
echo "PHONE_NUMBER=your_phone_number_here" >> config.txt

# Создаем Python-скрипт для бота (если он не был склонирован)
cat > bot.py << EOL
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
EOL

# Делаем скрипт запуска исполнимым
echo "python3 bot.py" > start.sh
chmod +x start.sh

# Запуск бота сразу после установки
./start.sh
