import asyncio
import subprocess
import os
import requests
import json
from telethon import TelegramClient, events

# Константы
CONFIG_FILE = 'config.json'
GITHUB_RAW_URL = 'https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py'
SCRIPT_VERSION = 0.0
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = u'\u2588'

# Функции для отмены локальных изменений в git, проверки обновлений, настройки автозапуска
# ...

# Функции для анимации текста
async def animate_typewriter(event, text, speed, cursor):
    """Анимация типографа."""
    typed_text = ""
    for char in text:
        typed_text += char
        await event.edit(typed_text + cursor)
        await asyncio.sleep(speed)
    await event.edit(typed_text)

async def animate_fade_in(event, text, speed):
    """Анимация плавного появления текста."""
    for i in range(1, len(text) + 1):
        await event.edit(text[:i])
        await asyncio.sleep(speed)

async def animate_blinking_cursor(event, text, speed):
    """Анимация мигающего курсора."""
    typed_text = ""
    for char in text:
        typed_text += char
        await event.edit(typed_text + '_')
        await asyncio.sleep(speed)
        await event.edit(typed_text)
        await asyncio.sleep(speed)

async def animate_rainbow(event, text, speed):
    """Анимация текста с эффектом радуги."""
    colors = ['#FF0000', '#FF7F00', '#FFFF00', '#00FF00', '#0000FF', '#4B0082', '#9400D3']
    typed_text = ""
    for i, char in enumerate(text):
        typed_text += char
        color = colors[i % len(colors)]
        await event.edit(f"<font color='{color}'>{typed_text}</font>")
        await asyncio.sleep(speed)

# Команда для изменения анимации
@client.on(events.NewMessage(pattern=r'смена'))
async def change_animation(event):
    await event.respond("Выберите анимацию текста:\n1. Типограф\n2. Плавное появление\n3. Мигающий курсор\n4. Радуга\nВведите цифру от 1 до 4.")

    # Ожидание выбора пользователя
    choice_event = await client.wait_for(events.NewMessage(from_users=event.sender_id))
    choice = choice_event.text.strip()

    if choice == "1":
        await event.respond("Вы выбрали анимацию 'Типограф'.")
        await animate_typewriter(event, "Пример текста", DEFAULT_TYPING_SPEED, DEFAULT_CURSOR)
    elif choice == "2":
        await event.respond("Вы выбрали анимацию 'Плавное появление'.")
        await animate_fade_in(event, "Пример текста", DEFAULT_TYPING_SPEED)
    elif choice == "3":
        await event.respond("Вы выбрали анимацию 'Мигающий курсор'.")
        await animate_blinking_cursor(event, "Пример текста", DEFAULT_TYPING_SPEED)
    elif choice == "4":
        await event.respond("Вы выбрали анимацию 'Радуга'.")
        await animate_rainbow(event, "Пример текста", DEFAULT_TYPING_SPEED)
    else:
        await event.respond("Неверный выбор! Пожалуйста, выберите цифру от 1 до 4.")

    # Удаляем меню выбора анимации и выбранную цифру
    await asyncio.sleep(1)  # Задержка перед удалением
    await event.delete()

# Инициализация клиента и запуск
async def main():
    print(f"Запуск main()... Версия скрипта {SCRIPT_VERSION}")
    
    setup_autostart()
    check_for_updates()
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Вы авторизованы в Telegram.")
    
    print_autostart_instructions()
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    check_for_updates()
    asyncio.run(main())
