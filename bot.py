import asyncio  # Импортируем asyncio для работы с асинхронным кодом
import subprocess
import os  # Добавлен импорт модуля os
import requests
import json
from telethon import TelegramClient, events
from random import choice

# Константы
CONFIG_FILE = 'config.json'
GITHUB_RAW_URL = 'https://raw.githubusercontent.com/sdfasdgasdfwe3rademainbot.py'  # Исправленный URL
SCRIPT_VERSION = 0.1.0
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = '▌'  # Символ по умолчанию для анимации
HEART = '🤍'
COLORED_HEARTS = ['💗', '💓', '💖', '💘', '❤️', '💞']
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

# Функция для отмены локальных изменений в git
def discard_local_changes():
    try:
        print('Отмена локальных изменений в файле bot.py...')
        subprocess.run(['git', 'checkout', '--', 'bot.py'], check=True)
        print('Локальные изменения в файле bot.py были отменены.')
    except subprocess.CalledProcessError as e:
        print(f'Ошибка при отмене изменений {e}')

# Функция для проверки обновлений скрипта на GitHub
def check_for_updates():
    try:
        # Сначала отменяем локальные изменения
        discard_local_changes()

        # Теперь обновляем скрипт
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
                        print(f'Доступна новая версия скрипта {remote_version} (текущая {SCRIPT_VERSION})')
                        with open(current_file, 'w', encoding='utf-8') as f:
                            f.write(remote_script)
                        print('Скрипт обновлен. Перезапустите программу.')
                        exit()
                    else:
                        print('У вас уже установлена последняя версия скрипта.')
                else:
                    print('Не удалось найти информацию о версии в загруженном скрипте.')
            else:
                print('Не удалось определить версии для сравнения.')
        else:
            print(f'Не удалось проверить обновления. Код ответа сервера {response.status_code}')
    except Exception as e:
        print(f'Ошибка при проверке обновлений {e}')

# Функция для настройки автозапуска
def setup_autostart():
    boot_directory = os.path.expanduser('~/.termux/boot')

    # Проверяем, существует ли папка для автозапуска
    if not os.path.exists(boot_directory):
        os.makedirs(boot_directory)
        print(f'Папка {boot_directory} создана.')

    # Путь к скрипту автозапуска
    script_path = os.path.join(boot_directory, 'start_bot.sh')

    # Путь к вашему скрипту бота
    bot_script_path = 'data/data/com.termux/files/home/radebot.py'  # Измените на актуальный путь

    # Создаем скрипт для автозапуска
    with open(script_path, 'w') as f:
        f.write(f'#!/data/data/com.termux/files/usr/bin/bash\n')
        f.write(f'cd /data/data/com.termux/files/home/radebot\n')
        f.write(f'python3 {bot_script_path}\n')

    # Даем права на исполнение скрипту
    os.chmod(script_path, 0o755)

    print(f'Автозапуск настроен. Скрипт сохранен в {script_path}.')

# Функция для удаления автозапуска
def remove_autostart():
    boot_directory = os.path.expanduser('~/.termux/boot')
    script_path = os.path.join(boot_directory, 'start_bot.sh')

    if os.path.exists(script_path):
        os.remove(script_path)
        print(f'Автозапуск удален. Скрипт {script_path} больше не будет запускаться при старте.')
    else:
        print('Скрипт автозапуска не найден. Возможно, он уже был удален.')

# Выводим инструкцию по отключению автозапуска
def print_autostart_instructions():
    print('Для отключения автозапуска скрипта бота выполните следующую команду в Termux:')
    print('Удаление автозапуска:')
    print('  python3 путь_к_скрипту bot.py --remove-autostart')
    print('Чтобы отключить автозапуск вручную, просто удалите файл:')
    print('  rm ~/.termux/boot/start_bot.sh')

# Проверяем наличие файла конфигурации
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        API_ID = config.get('API_ID')
        API_HASH = config.get('API_HASH')
        PHONE_NUMBER = config.get('PHONE_NUMBER')
        typing_speed = config.get('typing_speed', DEFAULT_TYPING_SPEED)
        cursor_symbol = config.get('cursor_symbol', DEFAULT_CURSOR)
    except (json.JSONDecodeError, KeyError) as e:
        print(f'Ошибка чтения конфигурации {e}. Попробуем запросить данные заново.')
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None
else:
    API_ID = None
    API_HASH = None
    PHONE_NUMBER = None

if not API_ID or not API_HASH or not PHONE_NUMBER:
    try:
        print('Пожалуйста, введите данные для авторизации в Telegram')
        API_ID = int(input('Введите ваш API ID: '))
        API_HASH = input('Введите ваш API Hash: ').strip()
        PHONE_NUMBER = input('Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX): ').strip()

        # Сохраняем данные в файл конфигурации
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'API_ID': API_ID,
                'API_HASH': API_HASH,
                'PHONE_NUMBER': PHONE_NUMBER,
                'typing_speed': DEFAULT_TYPING_SPEED,
                'cursor_symbol': DEFAULT_CURSOR
            }, f)
        print('Данные успешно сохранены в конфигурации.')
    except Exception as e:
        print(f'Ошибка сохранения конфигурации {e}')
        exit(1)

# Уникальное имя файла для сессии
SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}'

# Инициализация клиента
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Функция для генерации анимации с разноцветными сердечками
def generate_parade_colored():
    output = ''
    for c in PARADE_MAP:
        if c == '0':
            output += HEART
        elif c == '1':
            output += choice(COLORED_HEARTS)
        else:
            output += c
    return output

# Обработчик сообщения с анимацией
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
        print(f'Ошибка анимации: {e}')

# Обработчик для сердечек
@client.on(events.NewMessage(outgoing=True))
async def handle_heart(event):
    if HEART in event.message.message and event.sender_id == client.get_me().id:
        if event.is_channel or event.is_group:
            # Если это канал или группа, сразу начинаем анимацию
            await process_build_place(event)
            await process_colored_parade(event)
            await process_love_words(event)
        else:
            # Для обычного чата отслеживаем, когда собеседник прочитает сообщение
            async for user in client.iter_participants(event.peer_id):
                if user.id == event.sender_id:
                    continue
                if user.status and user.status != "offline":
                    await asyncio.sleep(3)
                    await client.edit_message(event.peer_id, event.message.id, generate_parade_colored())
                    await process_love_words(event)
                    await process_colored_parade(event)
                    break

# Функции анимации
async def process_love_words(event):
    await client.edit_message(event.peer_id, event.message.id, 'i')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id, event.message.id, 'i love')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id, event.message.id, 'i love you')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id, event.message.id, 'i love you forever')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id, event.message.id, 'i love you forever💗')

async def process_build_place(event):
    output = ''
    for i in range(8):
        output += '\n'
        for j in range(11):
            output += HEART
            await client.edit_message(event.peer_id, event.message.id, output)
            await asyncio.sleep(0.01)

async def process_colored_parade(event):
    for i in range(50):
        text = generate_parade_colored()
        await client.edit_message(event.peer_id, event.message.id, text)
        await asyncio.sleep(0.01)

# Основная функция для запуска клиента
async def main():
    print(f'Запуск main() - Версия скрипта {SCRIPT_VERSION}')
    setup_autostart()
    check_for_updates()
    await client.start(phone=PHONE_NUMBER)
    print('Скрипт успешно запущен! Вы авторизованы в Telegram.')
    print('Для использования анимации текста используйте команду p ваш текст.')
    print_autostart_instructions()
    await client.run_until_disconnected()

if __name__ == '__main__':
    check_for_updates()
    asyncio.run(main())
