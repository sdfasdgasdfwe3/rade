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
    # Проверим, что скрипт существует
    script_path = 'other_script.py'  # Убедитесь, что путь правильный
    if not os.path.exists(script_path):
        print(f"[!] Скрипт не найден: {script_path}")
        return

    try:
        print("[*] Попытка выполнить другой скрипт...")
        # Используем subprocess.run для запуска внешнего скрипта
        result = subprocess.run(
            ['python3', script_path], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("[*] Скрипт выполнен успешно")
            print(result.stdout)
        else:
            print("[*] Ошибка при выполнении скрипта")
            print(result.stderr)
    except Exception as e:
        print(f"[!] Ошибка при запуске скрипта: {e}")

# Обработчик для команды "magic"
@client.on(NewMessage(outgoing=True))
async def handle_message(event: NewMessage.Event):
    if event.message.text in MAGIC_PHRASES:  # Проверка на команду "magic"
        print("[*] Команда 'magic' обнаружена. Выполнение скрипта...")
        await execute_other_script()  # Выполнение внешнего скрипта

# Подключение клиента и управление сессией
async def main():
    print('[*] Подключение к Telegram...')
    await client.start()  # Теперь start() автоматически выполняет авторизацию
    print("Клиент Telegram успешно подключен!")
    await client.run_until_disconnected()  # Это запускает клиента и слушает сообщения

if __name__ == '__main__':
    asyncio.run(main())
