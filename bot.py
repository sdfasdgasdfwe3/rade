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
DEFAULT_CURSOR = u'\u2588'  # Символ по умолчанию для анимации

# Функция для отмены локальных изменений в git
def discard_local_changes():
    print("Отменить локальные изменения в файле bot.py.")
    try:
        subprocess.run(['git', 'checkout', '--', 'bot.py'], check=True)
        print("Локальные изменения в файле bot.py были отменены.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при отмене изменений: {e}")

# Функция для анимации текста
@client.on(events.NewMessage(pattern=r'p (.+)'))
async def animated_typing(event):
    print("Команда для печатания текста с анимацией.")
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
        print(f"Ошибка анимации: {e}")

# Функция для анимации сердца
@client.on(events.NewMessage(pattern=r'h'))
async def heart_animation(event):
    heart_symbols = ['❤️', '💓', '💖', '💘', '💝', '💞', '💗']
    try:
        if not event.out:
            return
        
        # Анимация мигающего сердца
        for _ in range(10):  # 10 раз выводим анимацию
            for heart in heart_symbols:
                await event.edit(heart)
                await asyncio.sleep(0.5)  # Пауза между сменами
        await event.delete()  # Удалим сообщение после анимации
    except Exception as e:
        print(f"Ошибка анимации сердца: {e}")

async def main():
    print(f"Запуск main()... Версия скрипта {SCRIPT_VERSION}")
    
    # Настроим автозапуск
    setup_autostart()
    
    check_for_updates()
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Вы авторизованы в Telegram.")
    print("Для использования анимации текста используйте команду p ваш текст.")
    print("Для анимации сердца используйте команду h.")
    
    # Печатаем инструкции по отключению автозапуска после старта бота
    print_autostart_instructions()
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    check_for_updates()
    asyncio.run(main())  # Теперь asyncio импортирован и main() может быть вызван
