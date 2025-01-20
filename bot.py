import asyncio
import subprocess
import os
import requests
import json
from telethon import TelegramClient, events
from pyrogram import Client as PyrogramClient, filters
from pyrogram.errors import FloodWait
from time import sleep
import emoji
from heart import heart_emoji  # Это предполагаемый файл с анимациями

# Константы
CONFIG_FILE = 'config.json'
GITHUB_RAW_URL = 'https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py'
SCRIPT_VERSION = 0.0
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = u'\u2588'

# Функция для отмены локальных изменений в git
def discard_local_changes():
    print("Отменить локальные изменения в файле bot.py.")
    try:
        print("Отмена локальных изменений в файле bot.py...")
        subprocess.run(['git', 'checkout', '--', 'bot.py'], check=True)
        print("Локальные изменения в файле bot.py были отменены.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при отмене изменений: {e}")

# Функция для проверки обновлений скрипта на GitHub
def check_for_updates():
    print("Проверка наличия обновлений скрипта на GitHub.")
    try:
        discard_local_changes()
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            remote_script = response.text
            current_file = os.path.abspath(__file__)

            with open(current_file, 'r', encoding='utf-8') as f:
                current_script = f.read()

            if str(SCRIPT_VERSION) in remote_script and str(SCRIPT_VERSION) in current_script:
                remote_version_line = [
                    line for line in remote_script.splitlines() if str(SCRIPT_VERSION) in line
                ]
                if remote_version_line:
                    remote_version = remote_version_line[0].split('=')[1].strip().strip('')
                    if str(SCRIPT_VERSION) != remote_version:
                        print(f"Доступна новая версия скрипта {remote_version} (текущая {SCRIPT_VERSION})")
                        with open(current_file, 'w', encoding='utf-8') as f:
                            f.write(remote_script)
                        print("Скрипт обновлен. Перезапустите программу.")
                        exit()
                    else:
                        print("У вас уже установлена последняя версия скрипта.")
                else:
                    print("Не удалось найти информацию о версии в загруженном скрипте.")
            else:
                print("Не удалось определить версии для сравнения.")
        else:
            print(f"Не удалось проверить обновления. Код ответа сервера {response.status_code}")
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {e}")

# Функция для настройки автозапуска
def setup_autostart():
    print("Функция для настройки автозапуска бота в Termux при старте устройства.")
    boot_directory = os.path.expanduser("~/.termux/boot")
    if not os.path.exists(boot_directory):
        os.makedirs(boot_directory)
        print(f"Папка {boot_directory} создана.")

    script_path = os.path.join(boot_directory, 'start_bot.sh')
    bot_script_path = '/data/data/com.termux/files/home/rade/bot.py'
    
    with open(script_path, 'w') as f:
        f.write(f"#!/data/data/com.termux/files/usr/bin/bash\n")
        f.write(f"cd /data/data/com.termux/files/home/rade\n")
        f.write(f"python3 {bot_script_path}\n")

    os.chmod(script_path, 0o755)
    print(f"Автозапуск настроен. Скрипт сохранен в {script_path}.")

# Функция для удаления автозапуска
def remove_autostart():
    print("Функция для удаления автозапуска бота в Termux.")
    boot_directory = os.path.expanduser("~/.termux/boot")
    script_path = os.path.join(boot_directory, 'start_bot.sh')
    
    if os.path.exists(script_path):
        os.remove(script_path)
        print(f"Автозапуск удален. Скрипт {script_path} больше не будет запускаться при старте.")
    else:
        print("Скрипт автозапуска не найден.")

# Обработка данных конфигурации
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
        print(f"Ошибка чтения конфигурации {e}.")
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None
else:
    API_ID = None
    API_HASH = None
    PHONE_NUMBER = None

if not API_ID or not API_HASH or not PHONE_NUMBER:
    print("Пожалуйста, введите данные для авторизации в Telegram.")
    API_ID = int(input("Введите ваш API ID: "))
    API_HASH = input("Введите ваш API Hash: ").strip()
    PHONE_NUMBER = input("Введите ваш номер телефона (в формате +7XXXXXXXXXX): ").strip()

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "API_ID": API_ID,
            "API_HASH": API_HASH,
            "PHONE_NUMBER": PHONE_NUMBER,
            "typing_speed": DEFAULT_TYPING_SPEED,
            "cursor_symbol": DEFAULT_CURSOR
        }, f)

SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}'

# Инициализация клиентов
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

app = PyrogramClient("my_account", api_id=API_ID, api_hash=API_HASH)

# Обработка анимации с heart в Pyrogram
@app.on_message(filters.command("heart", prefixes="") & filters.me)
def heart_f(_, message):
    end_message = "💛" + "__" + message.text.split("heart", maxsplit=1)[1] + "__"
    
    for i in range(len(heart_emoji)):
        try:
            message.edit(emoji.emojize(emoji.demojize(heart_emoji[i])))
            sleep(0.325)
        except FloodWait as e:
            print(f"Ожидание: {e.x} секунд")
            sleep(e.x)
        except Exception as e:
            print(f"Ошибка: {e}")
            break
    
    message.edit(end_message)

# Команда для анимации текста с Telethon
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

# Основной асинхронный запуск
async def main():
    print(f"Запуск main()... Версия скрипта {SCRIPT_VERSION}")
    setup_autostart()
    check_for_updates()
    await app.start()
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен!")
    
    # Печатаем инструкции по отключению автозапуска после старта
    print("Для отключения автозапуска выполните команду 'python3 bot.py --remove-autostart'.")
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    check_for_updates()
    asyncio.run(main())
