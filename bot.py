import asyncio
import subprocess
import os
import requests
import json
from telethon import TelegramClient
from telethon.events import NewMessage

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
SCRIPT_VERSION = "0.0.9"
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = u"\u2588"
MAGIC_PHRASES = ['magic']

# Функция для отмены локальных изменений в git
def discard_local_changes():
    try:
        print("Отмена локальных изменений в файле bot.py...")
        subprocess.run(["git", "checkout", "--", "bot.py"], check=True)
        print("Локальные изменения в файле bot.py были отменены.")
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
        print(f"Папка {boot_directory} создана.")
    
    script_path = os.path.join(boot_directory, "start_bot.sh")
    bot_script_path = "/data/data/com.termux/files/home/radebot.py"
    
    with open(script_path, "w") as f:
        f.write(f"#!/data/data/com.termux/files/usr/bin/bash\n")
        f.write(f"cd /data/data/com.termux/files/home/radebot\n")
        f.write(f"python3 {bot_script_path}\n")
    
    os.chmod(script_path, 0o755)
    print(f"Автозапуск настроен. Скрипт сохранен в {script_path}.")

# Функция для удаления автозапуска
def remove_autostart():
    boot_directory = os.path.expanduser("~/.termux/boot")
    script_path = os.path.join(boot_directory, "start_bot.sh")
    
    if os.path.exists(script_path):
        os.remove(script_path)
        print(f"Автозапуск удален. Скрипт {script_path} больше не будет запускаться при старте.")
    else:
        print("Скрипт автозапуска не найден.")

# Выводим инструкцию по отключению автозапуска
def print_autostart_instructions():
    print("\nДля отключения автозапуска скрипта бота выполните следующую команду в Termux")
    print("Удаление автозапуска:")
    print("  python3 путь_к_скриптуbot.py --remove-autostart")
    print("Чтобы отключить автозапуск вручную, просто удалите файл:")
    print("  rm ~/.termux/boot/start_bot.sh")

# Проверяем наличие файла конфигурации
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
        print(f"Ошибка чтения конфигурации {e}. Попробуем запросить данные заново.")
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None
else:
    API_ID = None
    API_HASH = None
    PHONE_NUMBER = None

if not API_ID or not API_HASH or not PHONE_NUMBER:
    try:
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
        print(f"Ошибка сохранения конфигурации {e}")
        exit(1)

# Инициализируем клиента Telegram
client = TelegramClient('tg-account', API_ID, API_HASH)

# Функция для выполнения внешнего скрипта
async def execute_other_script():
    result = subprocess.run(['python', 'other_script.py'], capture_output=True, text=True)
    return result.stdout

# Анимация текста
async def animate_text(event, text, delay=0.1):
    for i in range(len(text) + 1):
        await client.edit_message(event.peer_id.user_id, event.message.id, text[:i])
        await asyncio.sleep(delay)

# Основной обработчик для сообщений
@client.on(NewMessage(outgoing=True))
async def handle_message(event: NewMessage.Event):
    if event.message.text in MAGIC_PHRASES:  # Проверка на команду "magic"
        print("[*] Команда 'magic' обнаружена. Выполнение скрипта...")
        await execute_other_script()  # Выполнение внешнего скрипта
        
        # Запуск анимации текста
        await animate_text(event, "Выполнение магической команды...", delay=0.05)

    await client.send_message(event.peer_id, "Бот работает!")

    # Настроим автозапуск
    setup_autostart()
    check_for_updates()

    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Вы авторизованы в Telegram.")
    print("Для использования анимации текста используйте команду p ваш текст.")
    print_autostart_instructions()

    await client.run_until_disconnected()

# Функция main()
async def main():
    setup_autostart()
    check_for_updates()
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Вы авторизованы в Telegram.")
    print("Для использования анимации текста используйте команду p ваш текст.")
    print_autostart_instructions()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
