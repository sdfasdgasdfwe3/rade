import os
import json
import requests
from telethon import TelegramClient, events
import subprocess
import sys
import asyncio
import set  # Импортируем второй файл с функцией

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"  # Исправленный URL
SCRIPT_VERSION = "0.0.9"

# Глобальная переменная для управления анимацией
is_typing_enabled = True  # Флаг, включающий анимацию
typing_speed = 0.2  # Стандартная скорость печатания
cursor_symbol = "▮"  # Символ курсора для анимации текста

# Функция для отмены локальных изменений в git
def discard_local_changes():
    try:
        subprocess.run(["git", "checkout", "--", "bot.py"], check=True)
    except subprocess.CalledProcessError as e:
        pass

# Функция для проверки обновлений скрипта на GitHub
def check_for_updates():
    try:
        # Проверяем наличие обновлений скрипта на GitHub
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            remote_script = response.text
            current_file = os.path.abspath(__file__)

            with open(current_file, 'r', encoding='utf-8') as f:
                current_script = f.read()

            # Проверяем наличие строки SCRIPT_VERSION в обоих скриптах
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

# Проверка конфигурации
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        API_ID = config.get("API_ID")
        API_HASH = config.get("API_HASH")
        PHONE_NUMBER = config.get("PHONE_NUMBER")
    except (json.JSONDecodeError, KeyError) as e:
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None
else:
    API_ID = None
    API_HASH = None
    PHONE_NUMBER = None

# Если данные отсутствуют, запрашиваем их у пользователя
if not API_ID or not API_HASH or not PHONE_NUMBER:
    try:
        print("Пожалуйста, введите данные для авторизации в Telegram:")
        API_ID = int(input("Введите ваш API ID: "))
        API_HASH = input("Введите ваш API Hash: ").strip()
        PHONE_NUMBER = input("Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX): ").strip()

        # Сохраняем данные в файл конфигурации
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "API_ID": API_ID,
                "API_HASH": API_HASH,
                "PHONE_NUMBER": PHONE_NUMBER
            }, f)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")
        exit(1)

# Инициализация клиента
client = TelegramClient(f"session_{PHONE_NUMBER.replace('+', '').replace('-', '')}", API_ID, API_HASH)

# Функция текстовой анимации
async def animate_text(client, event, text):
    displayed_text = ""
    for char in text:
        displayed_text += char
        await client.edit_message(event.chat_id, event.message.id, displayed_text + cursor_symbol)
        await asyncio.sleep(typing_speed)
    # Убираем курсор после завершения анимации
    await client.edit_message(event.chat_id, event.message.id, displayed_text)

# Обработчик для команды /p
@client.on(events.NewMessage(pattern='/p'))
async def animate_handler(event):
    text_to_animate = "This is animated text!"  # Здесь можно заменить текст на любой другой
    await animate_text(client, event, text_to_animate)

# Новый обработчик для команды /magic
@client.on(events.NewMessage(pattern='/magic'))
async def magic_handler(event):
    # Переход в set.py и вызов функции magic_script
    await set.magic_script(client, event)

# Главная функция
async def main():
    # Авторизация и подключение
    await client.start(phone=PHONE_NUMBER)
    print(f"Успешно авторизованы как {PHONE_NUMBER}")

    # Запускаем цикл ожидания событий
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
