import asyncio
import subprocess
import os
from random import choice
from telethon import TelegramClient
from telethon.events import NewMessage

API_ID = 1252636  # Ваш API_ID
API_HASH = '4037e9f957f6f17d461b0c288ffa50f1'  # Ваш API_HASH

HEART = '🤍'
COLORED_HEARTS = ['💗', '💓', '💖', '💘', '❤️', '💞']
MAGIC_PHRASES = ['magic']  # Команда для выполнения другого скрипта
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

# Укажите файл для сессии, чтобы избежать повторной авторизации
session_file = 'tg-account.session'

client = TelegramClient(session_file, API_ID, API_HASH)

# Функция для генерации "парада" из сердец
def generate_parade_colored():
    output = ''
    for c in PARADE_MAP:  # Перебор каждого символа в PARADE_MAP
        if c == '0':
            output += HEART
        elif c == '1':
            output += choice(COLORED_HEARTS)
        else:
            output += c
    return output

# Функция для выполнения внешнего скрипта
async def execute_other_script():
    try:
        print("[*] Выполнение другого скрипта...")
        # Запуск основного скрипта
        new_script = "/data/data/com.termux/files/home/rade/bot.py"  # Укажите путь к другому скрипту
        process = subprocess.Popen(["python3", new_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()  # Ожидаем завершения и выводим ошибки
        print(stdout.decode())
        print(stderr.decode())

        # После завершения выполнения другого скрипта перезапускаем основной скрипт
        print("[*] Завершено выполнение другого скрипта. Перезапуск основного скрипта...")
        subprocess.Popen(["python3", __file__])  # Запуск текущего скрипта заново
        exit()

    except Exception as e:
        print(f"[!] Ошибка при запуске другого скрипта: {e}")

# Подключение клиента и управление сессией
async def main():
    print('[*] Подключение к Telegram...')
    await client.start()  # Теперь start() автоматически выполняет авторизацию
    print("Клиент Telegram успешно подключен!")

    # Запуск внешнего скрипта сразу при старте
    await execute_other_script()  # Выполнение внешнего скрипта сразу

    await client.run_until_disconnected()  # Это запускает клиента и слушает сообщения

if __name__ == '__main__':
    asyncio.run(main())
