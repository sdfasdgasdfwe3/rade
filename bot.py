import asyncio
import subprocess
import os
import requests
import json
from telethon import TelegramClient, events

# Константы
CONFIG_FILE = 'config.json'
GITHUB_RAW_URL = 'https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py'  # Исправленный URL
SCRIPT_VERSION = 0.1
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = u'\u2588'  # Символ по умолчанию для анимации

# Список доступных анимаций
animations = {
    1: {'name': 'Стандартная анимация', 'symbol': u'\u2588', 'speed': DEFAULT_TYPING_SPEED},
    2: {'name': 'Текст с эффектом дождя', 'symbol': '.', 'speed': 0.15},
    3: {'name': 'Текст с эффектом пузырей', 'symbol': u'\u2588', 'speed': 0.05},
    4: {'name': 'Текст с эффектом "письма"', 'symbol': '*', 'speed': DEFAULT_TYPING_SPEED},
}

# Добавление функции для получения user_id
async def get_user_id(client):
    try:
        me = await client.get_me()
        print(f"Ваш user_id: {me.id}")  # Выводим user_id в консоль
    except Exception as e:
        print(f"Ошибка при получении user_id: {e}")

# Функция для настройки автозапуска
def setup_autostart():
    # (весь код без изменений)
    pass

# Все другие функции без изменений...

async def main():
    # Проверяем наличие файла конфигурации
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            API_ID = config.get("API_ID")
            API_HASH = config.get("API_HASH")
            PHONE_NUMBER = config.get("PHONE_NUMBER")
            typing_speed = config.get("typing_speed", DEFAULT_TYPING_SPEED)
            cursor_symbol = config.get("cursor_symbol", DEFAULT_CURSOR)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Ошибка чтения конфигурации {e}. Попробуем запросить данные заново.")
            API_ID = None
            API_HASH = None
            PHONE_NUMBER = None
    else:
        # Если файл не существует, запрашиваем данные у пользователя
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None

    if not API_ID or not API_HASH or not PHONE_NUMBER:
        try:
            print("Пожалуйста, введите данные для авторизации в Telegram.")
            API_ID = int(input("Введите ваш API ID: "))
            API_HASH = input("Введите ваш API Hash: ").strip()
            PHONE_NUMBER = input("Введите ваш номер телефона (в формате +7XXXXXXXXXX): ").strip()

            # Сохраняем данные в файл конфигурации
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "API_ID": API_ID,
                    "API_HASH": API_HASH,
                    "PHONE_NUMBER": PHONE_NUMBER,
                    "typing_speed": DEFAULT_TYPING_SPEED,
                    "cursor_symbol": DEFAULT_CURSOR
                }, f)
            print("Данные успешно сохранены в конфигурации.")
        except Exception as e:
            print(f"Ошибка сохранения конфигурации {e}")
            exit(1)

    # Инициализация клиента теперь после получения конфигурации
    client = TelegramClient('session', API_ID, API_HASH)

    # Настроим автозапуск
    setup_autostart()

    check_for_updates()
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Вы авторизованы в Telegram.")
    print("Для использования анимации текста используйте команду р ваш текст.")
    
    # Печатаем инструкции по отключению автозапуска после старта бота
    print_autostart_instructions()

    # Получаем user_id
    await get_user_id(client)
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    check_for_updates()
    asyncio.run(main())  # Теперь asyncio импортирован и main() может быть вызван
