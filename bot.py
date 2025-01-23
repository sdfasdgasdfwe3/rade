import os
import json
from telethon import TelegramClient, events
import subprocess
import sys
from animations import typewriter_effect, get_animations  # Импортируем анимации

# Константы
CONFIG_FILE = "config.json"
SCRIPT_VERSION = "0.0.10"

# Загрузка данных конфигурации
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        API_ID = config.get("API_ID")
        API_HASH = config.get("API_HASH")
        PHONE_NUMBER = config.get("PHONE_NUMBER")
    except (json.JSONDecodeError, KeyError):
        print("Ошибка чтения конфигурации. Удалите файл config.json и попробуйте снова.")
        exit(1)
else:
    try:
        API_ID = int(input("Введите ваш API ID: "))
        API_HASH = input("Введите ваш API Hash: ").strip()
        PHONE_NUMBER = input("Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX): ").strip()
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "API_ID": API_ID,
                "API_HASH": API_HASH,
                "PHONE_NUMBER": PHONE_NUMBER,
            }, f)
    except Exception as e:
        print(f"Ошибка сохранения конфигурации: {e}")
        exit(1)

# Создание клиента Telegram
SESSION_FILE = f"session_{PHONE_NUMBER.replace('+', '').replace('-', '')}"
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Команда /p для анимации текста
@client.on(events.NewMessage(pattern=r'/p\s+(.+)'))
async def text_animation_handler(event):
    """
    Обработчик команды /p для анимации текста (печатающая машинка).
    """
    text = event.pattern_match.group(1)  # Текст после команды
    result = typewriter_effect(text)  # Анимация текста
    message = await event.reply(result)  # Отправляем результат
    
    # Удаляем 3 последних сообщения бота (команда и результат)
    async for message in client.iter_messages(event.chat_id, limit=3):
        if message.sender_id == client.id:
            await message.delete()

# Команда /md для вывода списка установленных модулей
@client.on(events.NewMessage(pattern='/md'))
async def list_modules_handler(event):
    """
    Обработчик команды /md для вывода списка установленных модулей.
    """
    try:
        # Получаем список установленных модулей
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            modules_list = result.stdout  # Список модулей
            await event.reply(f"Установленные модули:\n```\n{modules_list}\n```", parse_mode='markdown')
        else:
            await event.reply(f"Ошибка при получении списка модулей:\n{result.stderr}")
    except Exception as e:
        await event.reply(f"Не удалось получить список модулей: {str(e)}")

async def main():
    await client.start(phone=PHONE_NUMBER)
    print(f"Успешно авторизованы как {PHONE_NUMBER}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
