import asyncio 
import subprocess
import os  # Добавлен импорт модуля os
import requests
import json
from telethon import TelegramClient, events

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"  # Исправленный URL
SCRIPT_VERSION = "0.0.9"
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = u"\u2588"  # Символ по умолчанию для анимации

# Функция для отмены локальных изменений в git
def discard_local_changes():
    try:
        subprocess.run(["git", "checkout", "--", "bot.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при отмене изменений {e}")

# Функция для проверки обновлений скрипта на GitHub
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
                    line for line in remote_script.splitlines() if SCRIPT_VERSION in line
                ]
                if remote_version_line:
                    remote_version = remote_version_line[0].split('=')[1].strip().strip('"')
                    if SCRIPT_VERSION != remote_version:
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
        print(f"Ошибка при проверке обновлений {e}")

# Функция для настройки автозапуска
def setup_autostart():
    boot_directory = os.path.expanduser("~/.termux/boot")
    
    if not os.path.exists(boot_directory):
        os.makedirs(boot_directory)
    
    script_path = os.path.join(boot_directory, "start_bot.sh")
    bot_script_path = os.path.abspath(__file__)

    with open(script_path, "w") as f:
        f.write(f"#!/data/data/com.termux/files/usr/bin/bash\n")
        f.write(f"cd {os.path.dirname(bot_script_path)}  # Путь к вашему боту\n")
        f.write(f"python3 {bot_script_path}  # Запуск бота\n")
    
    os.chmod(script_path, 0o755)

# Функция для удаления автозапуска
def remove_autostart():
    boot_directory = os.path.expanduser("~/.termux/boot")
    script_path = os.path.join(boot_directory, "start_bot.sh")
    
    if os.path.exists(script_path):
        os.remove(script_path)
        print(f"Автозапуск удален. Скрипт {script_path} больше не будет запускаться при старте.")
    else:
        print("Скрипт автозапуска не найден. Возможно, он уже был удален.")

# Выводим инструкцию по отключению автозапуска
def print_autostart_instructions():
    print("\nДля отключения автозапуска скрипта бота выполните следующую команду в Termux")
    print("Удаление автозапуска:")
    print("  python3 путь_к_скрипту/bot.py --remove-autostart")
    print("Чтобы отключить автозапуск вручную, просто удалите файл:")
    print("  rm ~/.termux/boot/start_bot.sh")

# Проверяем наличие файла конфигурации
try:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        API_ID = config.get("API_ID")
        API_HASH = config.get("API_HASH")
        PHONE_NUMBER = config.get("PHONE_NUMBER")
        typing_speed = config.get("typing_speed", DEFAULT_TYPING_SPEED)
        cursor_symbol = config.get("cursor_symbol", DEFAULT_CURSOR)
    else:
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None

    if not API_ID or not API_HASH or not PHONE_NUMBER:
        print("Пожалуйста, введите данные для авторизации в Telegram:")
        API_ID = int(input("Введите ваш API ID: "))
        API_HASH = input("Введите ваш API Hash: ").strip()
        PHONE_NUMBER = input("Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX): ").strip()
        
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
    print(f"Ошибка обработки конфигурации {e}")
    exit(1)

SESSION_FILE = f"session_{PHONE_NUMBER.replace('+', '').replace('-', '')}"
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

@client.on(events.NewMessage(pattern=r'p (.+)'))
async def animated_typing(event):
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
    check_for_updates()
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Вы авторизованы в Telegram.")
    print("Для использования анимации текста используйте команду p ваш текст.")
    print_autostart_instructions()
    await client.run_until_disconnected()

if __name__ == "__main__":
    check_for_updates()
    asyncio.run(main())
