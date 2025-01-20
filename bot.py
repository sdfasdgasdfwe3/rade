import asyncio
import subprocess
import os
import requests
import json
from telethon import TelegramClient, events
from random import choice

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"  # Исправленный URL
SCRIPT_VERSION = "0.0.9"
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = u"\u2588"  # Символ по умолчанию для анимации

HEART = '🤍'
COLORED_HEARTS = ['💗', '💓', '💖', '💘', '❤️', '💞']
MAGIC_PHRASES = ['magic']
EDIT_DELAY = 0.01
PARADE_MAP = '''
00000000000
00111011100
01111111110
01111111110
00111111100
00011111000
00001110000
00000100000
'''

# Инициализация клиента
client = TelegramClient('session_name', API_ID, API_HASH)

# Функции анимации
def generate_parade_colored():
    output = ''
    for c in PARADE_MAP:
        if c == '0':
            output += HEART
        elif c == '1':
            output += choice(COLORED_HEARTS)
        else:
            output += c
    return output

async def process_love_words(event):
    await event.edit('i')
    await asyncio.sleep(1)
    await event.edit('i love')
    await asyncio.sleep(1)
    await event.edit('i love you')
    await asyncio.sleep(1)
    await event.edit('i love you forever')
    await asyncio.sleep(1)
    await event.edit('i love you forever💗')

async def process_build_place(event):
    output = ''
    for i in range(8):
        output += '\n'
        for j in range(11):
            output += HEART
            await event.edit(output)
            await asyncio.sleep(EDIT_DELAY / 2)

async def process_colored_parade(event):
    for i in range(50):
        text = generate_parade_colored()
        await event.edit(text)
        await asyncio.sleep(EDIT_DELAY)

# Ваши функции, такие как обновления, автозапуск и другие, остаются неизменными

@client.on(events.NewMessage(pattern=r'(magic)'))
async def handle_magic_phrase(event):
    await process_build_place(event)
    await process_colored_parade(event)
    await process_love_words(event)

@client.on(events.NewMessage(pattern=r'p (.+)'))
async def animated_typing(event):
    global typing_speed, cursor_symbol
    try:
        if not event.out:
            return

        text = event.pattern_match.group(1)
        typed_text = ""

        for char in text:
            typed_text += char
            await event.edit(typed_text + cursor_symbol)
            await asyncio.sleep(typing_speed)

        await event.edit(typed_text)
    except Exception as e:
        print(f"Ошибка анимации {e}")

async def main():
    print(f"Запуск main()\nВерсия скрипта {SCRIPT_VERSION}")
    
    # Настроим автозапуск
    setup_autostart()
    
    check_for_updates()
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Вы авторизованы в Telegram.")
    print("Для использования анимации текста используйте команду p ваш текст.")
    
    # Печатаем инструкции по отключению автозапуска после старта бота
    print_autostart_instructions()
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    check_for_updates()
    asyncio.run(main())  # Теперь asyncio импортирован и main() может быть вызван
