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
cursor_symbol = "⏳"  # Символ курсора

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

# Анимация текста
@client.on(events.NewMessage(pattern=r'/(.*)'))
async def type_text(event):
    """Команда для печатания текста с анимацией."""
    global typing_speed, cursor_symbol, is_typing_enabled
    try:
        if not event.out or not is_typing_enabled:
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
        await event.reply("<b>Произошла ошибка во время выполнения команды.</b>", parse_mode='html')

# Команда для изменения скорости печатания
@client.on(events.NewMessage(pattern=r'/s (\d*\.?\d+)'))
async def set_typing_speed(event):
    """Команда для изменения скорости печатания."""
    global typing_speed
    try:
        if not event.out:
            return

        new_speed = float(event.pattern_match.group(1))

        if 0.1 <= new_speed <= 0.5:
            typing_speed = new_speed

            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            config["typing_speed"] = typing_speed
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f)

            await event.reply(f"<b>Скорость печатания изменена на {typing_speed} секунд.</b>", parse_mode='html')
        else:
            await event.reply("<b>Введите значение задержки в диапазоне от 0.1 до 0.5 секунд.</b>", parse_mode='html')

    except ValueError:
        await event.reply("<b>Некорректное значение. Укажите число в формате 0.1 - 0.5.</b>", parse_mode='html')
    except Exception as e:
        print(f"Ошибка при изменении скорости: {e}")
        await event.reply("<b>Произошла ошибка при изменении скорости.</b>", parse_mode='html')

# Новый обработчик для команды /magic
@client.on(events.NewMessage(pattern='/magic'))
async def magic_handler(event):
    # Переход в set.py и вызов функции magic_script
    await set.magic_script(client, event)

async def main():
    # Авторизация и подключение
    await client.start(phone=PHONE_NUMBER)
    print(f"Успешно авторизованы как {PHONE_NUMBER}")

    # Ожидаем завершения работы
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
