import os
import json
import requests
from telethon import TelegramClient

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
SCRIPT_VERSION = "0.0.9"

# Функция для проверки обновлений скрипта на GitHub
def check_for_updates():
    try:
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
        print(f"Ошибка при проверке обновлений: {e}")

# Проверка и получение данных авторизации
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        API_ID = config.get("API_ID")
        API_HASH = config.get("API_HASH")
        PHONE_NUMBER = config.get("PHONE_NUMBER")
        typing_speed = config.get("typing_speed", DEFAULT_TYPING_SPEED)
        cursor_symbol = config.get("cursor_symbol", DEFAULT_CURSOR)

        if not all([API_ID, API_HASH, PHONE_NUMBER]):
            raise ValueError("Файл конфигурации содержит неполные данные.")
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Ошибка чтения конфигурации: {e}. Удалите {CONFIG_FILE} и попробуйте снова.")
        exit(1)
else:
    # Запрашиваем данные у пользователя
    try:
        API_ID = int(input("Введите ваш API ID: "))
        API_HASH = input("Введите ваш API Hash: ").strip()
        PHONE_NUMBER = input("Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX): ").strip()

        if not API_ID or not API_HASH or not PHONE_NUMBER.startswith('+'):
            raise ValueError("Некорректные данные. Проверьте ваш API ID, API Hash и номер телефона.")

        typing_speed = DEFAULT_TYPING_SPEED
        cursor_symbol = DEFAULT_CURSOR

        # Сохраняем данные в файл конфигурации
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "API_ID": API_ID,
                "API_HASH": API_HASH,
                "PHONE_NUMBER": PHONE_NUMBER
            }, f)
        print(f"Данные сохранены в {CONFIG_FILE}.")
    except ValueError as ve:
        print(f"Ошибка: {ve}")
        exit(1)
    except Exception as e:
        print(f"Ошибка сохранения конфигурации: {e}")
        exit(1)

# Уникальное имя файла для сессии
SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}'

# Инициализация клиента Telegram
try:
    check_for_updates()  # Проверка обновлений перед запуском клиента
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    print(f"Клиент Telegram успешно инициализирован. Используется сессия: {SESSION_FILE}")
except Exception as e:
    print(f"Ошибка инициализации Telegram клиента: {e}")
    exit(1)

# Пример вызова основного потока для клиента
async def main():
    await client.start(phone=PHONE_NUMBER)
    print(f"Успешно авторизованы как {PHONE_NUMBER}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
