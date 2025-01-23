import os
import json
import requests
from telethon import TelegramClient, events
import subprocess
import shutil
import sys

# Константы
CONFIG_FILE = "config.json"
SCRIPT_VERSION = "0.0.10"
DEFAULT_TYPING_SPEED = 1.5
DEFAULT_CURSOR = "▮"

# Попробуем импортировать модуль animations, но если его нет — обработаем исключение
animations = None
try:
    from animations.animations import typewriter_effect, get_animations
    animations = True
except ImportError:
    animations = False
    print("Модуль animations не найден. Анимации не будут доступны.")

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

# Функция для обработки команды выбора анимации
@client.on(events.NewMessage(pattern='/choose_animation'))
async def choose_animation_handler(event):
    if not animations:
        await event.reply("Модуль animations не найден. Анимации недоступны.")
        return
    
    # Получаем список анимаций из модуля
    available_animations = get_animations()
    if not available_animations:
        await event.reply("Доступных анимаций нет.")
        return

    # Выводим список анимаций
    animation_list = "\n".join(f"{i + 1}. {name}" for i, name in enumerate(available_animations))
    message = await event.reply(f"Выберите анимацию (ответьте номером):\n\n{animation_list}")

    # Ждем ответа пользователя
    try:
        response = await client.wait_for(events.NewMessage(from_users=event.sender_id), timeout=30)
        selected_index = int(response.text.strip()) - 1

        # Проверяем, что выбор корректен
        if 0 <= selected_index < len(available_animations):
            selected_animation = available_animations[selected_index]
            await event.reply(f"Вы выбрали: {selected_animation}")
            await message.delete()
            await response.delete()

        else:
            await event.reply("Некорректный выбор. Попробуйте снова.")
    except (ValueError, TimeoutError):
        await event.reply("Вы не выбрали анимацию вовремя.")

# Команда для запуска анимации текста
@client.on(events.NewMessage(pattern='/p (.+)'))
async def text_animation_handler(event):
    if not animations:
        await event.reply("Модуль animations не найден. Анимации недоступны.")
        return

    # Получаем текст для анимации
    text = event.pattern_match.group(1)

    # Используем анимацию typewriter_effect
    animated_text = typewriter_effect(text, speed=0.1)
    await event.reply(f"```\n{animated_text}\n```", parse_mode="markdown")

# Команда для отображения списка установленных модулей
@client.on(events.NewMessage(pattern='/md'))
async def list_modules_handler(event):
    result = subprocess.run([sys.executable, '-m', 'pip', 'list'], stdout=subprocess.PIPE, text=True)
    installed_modules = result.stdout
    await event.reply(f"Установленные модули:\n\n```\n{installed_modules}\n```", parse_mode="markdown")

async def main():
    await client.start(phone=PHONE_NUMBER)
    print(f"Успешно авторизованы как {PHONE_NUMBER}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
