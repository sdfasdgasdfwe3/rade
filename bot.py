import asyncio
import subprocess
import os
import requests
import json
from telethon import TelegramClient, events

# Константы
CONFIG_FILE = 'config.json'
GITHUB_RAW_URL = 'https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py'  # Исправленный URL
SCRIPT_VERSION = 2
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = u'\u2588'

# Функция для отмены локальных изменений
def discard_local_changes():
    """Отменить локальные изменения в файле bot.py."""
    try:
        print("Отмена локальных изменений в bot.py...")
        # Можно использовать любую из команд, в зависимости от вашей версии Git:
        # subprocess.run(['git', 'checkout', '--', 'bot.py'], check=True)  # Для старых версий Git
        subprocess.run(['git', 'restore', '--staged', 'bot.py'], check=True)  # Для новых версий Git
        print("Локальные изменения в bot.py были отменены.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при отмене изменений: {e}")

# Функция для проверки обновлений
def check_for_updates():
    try:
        discard_local_changes()
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            remote_script = response.text
            current_file = os.path.abspath(__file__)

            with open(current_file, 'r', encoding='utf-8') as f:
                current_script = f.read()

            if SCRIPT_VERSION in remote_script and SCRIPT_VERSION in current_script:
                remote_version_line = [
                    line for line in remote_script.splitlines() if "SCRIPT_VERSION" in line
                ]
                if remote_version_line:
                    remote_version = remote_version_line[0].split('=')[1].strip().strip('"')
                    if SCRIPT_VERSION != remote_version:
                        print(f"Доступна новая версия {remote_version} (текущая {SCRIPT_VERSION})")
                        with open(current_file, 'w', encoding='utf-8') as f:
                            f.write(remote_script)
                        print("Скрипт обновлен. Перезапустите программу.")
                        exit()
                    else:
                        print("У вас последняя версия скрипта.")
                else:
                    print("Не удалось найти информацию о версии.")
            else:
                print("Не удалось определить версии.")
        else:
            print(f"Не удалось проверить обновления. Код ответа: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {e}")

# Функция настройки автозапуска
def setup_autostart():
    boot_directory = os.path.expanduser('~/.termux/boot')
    if not os.path.exists(boot_directory):
        os.makedirs(boot_directory)
        print(f"Папка {boot_directory} создана.")

    script_path = os.path.join(boot_directory, 'start_bot.sh')
    bot_script_path = '/data/data/com.termux/files/home/bot.py'
    
    with open(script_path, 'w') as f:
        f.write(f"#!/data/data/com.termux/files/usr/bin/bash\n")
        f.write(f"cd /data/data/com.termux/files/home/\n")
        f.write(f"python3 {bot_script_path}\n")
    
    os.chmod(script_path, 0o755)
    print(f"Автозапуск настроен: {script_path}")

def remove_autostart():
    boot_directory = os.path.expanduser('~/.termux/boot')
    script_path = os.path.join(boot_directory, 'start_bot.sh')
    
    if os.path.exists(script_path):
        os.remove(script_path)
        print(f"Автозапуск удалён: {script_path}")
    else:
        print("Скрипт автозапуска не найден.")

def print_autostart_instructions():
    print("\nДля отключения автозапуска выполните:")
    print("Удаление автозапуска:")
    print("  python3 путь_к_скрипту/bot.py --remove-autostart")
    print("Или вручную:")
    print("  rm ~/.termux/boot/start_bot.sh")

# Проверка конфигурации
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
        print(f"Ошибка чтения конфигурации: {e}. Запрашиваю данные.")
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None
else:
    API_ID = None
    API_HASH = None
    PHONE_NUMBER = None

if not API_ID or not API_HASH or not PHONE_NUMBER:
    try:
        print("Введите данные для авторизации в Telegram:")
        API_ID = int(input("Введите API ID: "))
        API_HASH = input("Введите API Hash: ").strip()
        PHONE_NUMBER = input("Введите номер телефона (+375XXXXXXXXX): ").strip()
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "API_ID": API_ID,
                "API_HASH": API_HASH,
                "PHONE_NUMBER": PHONE_NUMBER,
                "typing_speed": DEFAULT_TYPING_SPEED,
                "cursor_symbol": DEFAULT_CURSOR
            }, f)
        print("Данные сохранены.")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        exit(1)

SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}'
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

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
        print(f"Ошибка анимации: {e}")

async def main():
    print(f"Версия скрипта: {SCRIPT_VERSION}")
    setup_autostart()
    check_for_updates()
    await client.start(phone=PHONE_NUMBER)
    print("Бот запущен!")
    print_autostart_instructions()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
