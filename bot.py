import asyncio  # Импортируем asyncio для работы с асинхронным кодом
import subprocess
import os  # Добавлен импорт модуля os
import requests
import json
from telethon import TelegramClient, events

# Константы
CONFIG_FILE = config.json
GITHUB_RAW_URL = httpsraw.githubusercontent.comsdfasdgasdfwe3rademainbot.py  # Исправленный URL
SCRIPT_VERSION = 0.0.4
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = u2588  # Символ по умолчанию для анимации

# Функция для отмены локальных изменений в git
def discard_local_changes()
    Отменить локальные изменения в файле bot.py.
    try
        print(Отмена локальных изменений в файле bot.py...)
        subprocess.run([git, checkout, --, bot.py], check=True)
        print(Локальные изменения в файле bot.py были отменены.)
    except subprocess.CalledProcessError as e
        print(fОшибка при отмене изменений {e})

# Функция для проверки обновлений скрипта на GitHub
def check_for_updates()
    Проверка наличия обновлений скрипта на GitHub.
    try
        # Сначала отменяем локальные изменения
        discard_local_changes()

        # Теперь обновляем скрипт
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200
            remote_script = response.text
            current_file = os.path.abspath(__file__)

            with open(current_file, 'r', encoding='utf-8') as f
                current_script = f.read()

            # Проверяем наличие строки SCRIPT_VERSION в обоих скриптах
            if SCRIPT_VERSION in remote_script and SCRIPT_VERSION in current_script
                remote_version_line = [
                    line for line in remote_script.splitlines() if SCRIPT_VERSION in line
                ]
                if remote_version_line
                    remote_version = remote_version_line[0].split('=')[1].strip().strip('')
                    if SCRIPT_VERSION != remote_version
                        print(fДоступна новая версия скрипта {remote_version} (текущая {SCRIPT_VERSION}))
                        with open(current_file, 'w', encoding='utf-8') as f
                            f.write(remote_script)
                        print(Скрипт обновлен. Перезапустите программу.)
                        exit()
                    else
                        print(У вас уже установлена последняя версия скрипта.)
                else
                    print(Не удалось найти информацию о версии в загруженном скрипте.)
            else
                print(Не удалось определить версии для сравнения.)
        else
            print(fНе удалось проверить обновления. Код ответа сервера {response.status_code})
    except Exception as e
        print(fОшибка при проверке обновлений {e})

# Функция для настройки автозапуска
def setup_autostart()
    Функция для настройки автозапуска бота в Termux при старте устройства
    boot_directory = os.path.expanduser(~.termuxboot)
    
    # Проверяем, существует ли папка для автозапуска
    if not os.path.exists(boot_directory)
        os.makedirs(boot_directory)
        print(fПапка {boot_directory} создана.)
    
    # Путь к скрипту автозапуска
    script_path = os.path.join(boot_directory, start_bot.sh)
    
    # Путь к вашему скрипту бота
    bot_script_path = datadatacom.termuxfileshomeradebot.py  # Измените на актуальный путь
    
    # Создаем скрипт для автозапуска
    with open(script_path, w) as f
        f.write(f#!datadatacom.termuxfilesusrbinbash
cd datadatacom.termuxfileshomerade  # Путь к вашему боту
python3 {bot_script_path}  # Запуск бота
)
    
    # Даем права на исполнение скрипту
    os.chmod(script_path, 0o755)
    
    print(fАвтозапуск настроен. Скрипт сохранен в {script_path}.)

# Функция для удаления автозапуска
def remove_autostart()
    Функция для удаления автозапуска бота в Termux
    boot_directory = os.path.expanduser(~.termuxboot)
    script_path = os.path.join(boot_directory, start_bot.sh)
    
    if os.path.exists(script_path)
        os.remove(script_path)
        print(fАвтозапуск удален. Скрипт {script_path} больше не будет запускаться при старте.)
    else
        print(Скрипт автозапуска не найден. Возможно, он уже был удален.)

# Выводим инструкцию по отключению автозапуска
def print_autostart_instructions()
    Выводим информацию по отключению автозапуска
    print(nДля отключения автозапуска скрипта бота выполните следующую команду в Termux)
    print(Удаление автозапуска)
    print(  python3 путь_к_скриптуbot.py --remove-autostart)
    print(Чтобы отключить автозапуск вручную, просто удалите файл)
    print(  rm ~.termuxbootstart_bot.sh)

# Проверяем наличие файла конфигурации
if os.path.exists(CONFIG_FILE)
    try
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f
            config = json.load(f)
        API_ID = config.get(API_ID)
        API_HASH = config.get(API_HASH)
        PHONE_NUMBER = config.get(PHONE_NUMBER)
        typing_speed = config.get(typing_speed, DEFAULT_TYPING_SPEED)
        cursor_symbol = config.get(cursor_symbol, DEFAULT_CURSOR)
    except (json.JSONDecodeError, KeyError) as e
        print(fОшибка чтения конфигурации {e}. Попробуем запросить данные заново.)
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None
else
    # Если файл не существует, запрашиваем данные у пользователя
    API_ID = None
    API_HASH = None
    PHONE_NUMBER = None

if not API_ID or not API_HASH or not PHONE_NUMBER
    try
        print(Пожалуйста, введите данные для авторизации в Telegram)
        API_ID = int(input(Введите ваш API ID ))
        API_HASH = input(Введите ваш API Hash ).strip()
        PHONE_NUMBER = input(Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX) ).strip()
        
        # Сохраняем данные в файл конфигурации
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f
            json.dump({
                API_ID API_ID,
                API_HASH API_HASH,
                PHONE_NUMBER PHONE_NUMBER,
                typing_speed DEFAULT_TYPING_SPEED,
                cursor_symbol DEFAULT_CURSOR
            }, f)
        print(Данные успешно сохранены в конфигурации.)
    except Exception as e
        print(fОшибка сохранения конфигурации {e})
        exit(1)

# Уникальное имя файла для сессии
SESSION_FILE = f'session_{PHONE_NUMBER.replace(+, ).replace(-, )}'

# Инициализация клиента
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

@client.on(events.NewMessage(pattern=r'p (.+)'))
async def animated_typing(event)
    Команда для печатания текста с анимацией.
    global typing_speed, cursor_symbol
    try
        if not event.out
            return

        text = event.pattern_match.group(1)
        typed_text = 

        for char in text
            typed_text += char
            await event.edit(typed_text + cursor_symbol)
            await asyncio.sleep(typing_speed)

        await event.edit(typed_text)
    except Exception as e
        print(fОшибка анимации {e})

async def main()
    print(fЗапуск main()nВерсия скрипта {SCRIPT_VERSION})
    
    # Настроим автозапуск
    setup_autostart()
    
    check_for_updates()
    await client.start(phone=PHONE_NUMBER)
    print(Скрипт успешно запущен! Вы авторизованы в Telegram.)
    print(Для использования анимации текста используйте команду p ваш текст.)
    
    # Печатаем инструкции по отключению автозапуска после старта бота
    print_autostart_instructions()
    
    await client.run_until_disconnected()

if __name__ == __main__
    check_for_updates()
    asyncio.run(main())  # Теперь asyncio импортирован и main() может быть вызван
