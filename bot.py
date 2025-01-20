import asyncio
import subprocess
import os
import requests
import json
from telethon import TelegramClient, events

# Константы
CONFIG_FILE = 'config.json'
GITHUB_RAW_URL = 'https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py'  # Исправленный URL
SCRIPT_VERSION = 0.1
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = u'\u2588'  # Символ по умолчанию для анимации

# Список доступных анимаций
animations = {
    1: {'name': 'Стандартная анимация', 'symbol': u'\u2588', 'speed': DEFAULT_TYPING_SPEED},
    2: {'name': 'Текст с эффектом дождя', 'symbol': '.', 'speed': 0.15},  # Заменили на "Текст с эффектом дождя"
    3: {'name': 'Текст с эффектом пузырей', 'symbol': u'\u2588', 'speed': 0.05},  # Заменили на "Текст с эффектом пузырей"
    4: {'name': 'Текст с эффектом "письма"', 'symbol': '*', 'speed': DEFAULT_TYPING_SPEED},  # Заменили на "Текст с эффектом письма"
}

# Флаг для проверки, отправлено ли меню
menu_sent = False

# Функция для отмены локальных изменений в git
def discard_local_changes():
    print("Отменить локальные изменения в файле bot.py.")
    try:
        print("Отмена локальных изменений в файле bot.py...")
        subprocess.run(['git', 'checkout', '--', 'bot.py'], check=True)
        print("Локальные изменения в файле bot.py были отменены.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при отмене изменений: {e}")

# Функция для настройки автозапуска
def setup_autostart():
    print("Функция для настройки автозапуска бота в Termux при старте устройства.")
    boot_directory = os.path.expanduser("~/.termux/boot")
    
    if not os.path.exists(boot_directory):
        os.makedirs(boot_directory)
        print(f"Папка {boot_directory} создана.")
    
    script_path = os.path.join(boot_directory, 'start_bot.sh')
    bot_script_path = '/data/data/com.termux/files/home/rade/bot.py'  # Измените на актуальный путь
    
    with open(script_path, 'w') as f:
        f.write(f"#!/data/data/com.termux/files/usr/bin/bash\n")
        f.write(f"cd /data/data/com.termux/files/home/rade\n")
        f.write(f"python3 {bot_script_path}\n")
    
    os.chmod(script_path, 0o755)
    print(f"Автозапуск настроен. Скрипт сохранен в {script_path}.")

# Выводим инструкцию по отключению автозапуска
def print_autostart_instructions():
    print("Для отключения автозапуска скрипта бота выполните следующую команду в Termux:")
    print("Удаление автозапуска:")
    print("  python3 путь_к_скрипту bot.py --remove-autostart")

# Функция логгирования для работы
async def log_message(log_text, log_file="bot_log.txt"):
    try:
        with open(log_file, "a", encoding="utf-8") as file:
            file.write(log_text + "\n")
    except Exception as e:
        print(f"Ошибка записи лога: {e}")

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
        print(f"Ошибка чтения конфигурации {e}. Попробуем запросить данные заново.")
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None
else:
    API_ID = None
    API_HASH = None
    PHONE_NUMBER = None

# Запрос данных авторизации
if not API_ID or not API_HASH or not PHONE_NUMBER:
    try:
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
        print("Данные успешно сохранены в конфигурации.")
    except Exception as e:
        print(f"Ошибка сохранения конфигурации {e}")
        exit(1)

SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}'
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Функция для отображения меню выбора анимации
async def show_animation_menu(event):
    global menu_sent
    if not menu_sent:
        menu_text = "Меню анимаций:\n"
        for num, animation in animations.items():
            menu_text += f"{num}. {animation['name']}\n"
        menu_text += "Выберите номер анимации для изменения."

        await event.respond(menu_text)
        menu_sent = True  # Меню отправлено, больше не отправляем его

# Обработчик команды Меню
@client.on(events.NewMessage(pattern=r'Меню'))
async def menu_handler(event):
    try:
        # Показываем меню анимаций
        await show_animation_menu(event)
        
        # Удаляем сообщение "Меню" после его отображения
        await event.delete()

    except Exception as e:
        print(f"Ошибка при выводе меню: {e}")

# Обработчик для выбора анимации по номеру
@client.on(events.NewMessage(pattern=r'\d'))
async def change_animation(event):
    try:
        # Получаем номер выбранной анимации
        choice = int(event.text.strip())
        if choice in animations:
            global cursor_symbol, typing_speed
            selected_animation = animations[choice]
            cursor_symbol = selected_animation['symbol']
            typing_speed = selected_animation['speed']

            # Сохраняем выбранную анимацию в конфигурации
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "API_ID": API_ID,
                    "API_HASH": API_HASH,
                    "PHONE_NUMBER": PHONE_NUMBER,
                    "typing_speed": typing_speed,
                    "cursor_symbol": cursor_symbol
                }, f)

            # Отправляем сообщение, подтверждающее выбор анимации
            confirmation_message = await event.respond(f"Вы выбрали анимацию: {selected_animation['name']}")

            # Удаляем сообщение с выбором анимации
            await event.delete()

            # Удаляем меню анимаций через 1 секунду (чтобы дать время на прочтение)
            await asyncio.sleep(1)
            await confirmation_message.delete()

        else:
            await event.respond("Неверный выбор. Пожалуйста, выберите номер из списка.")
    except Exception as e:
        print(f"Ошибка при изменении анимации: {e}")

# Функция отображения справки
async def show_help(event):
    help_text = (
        "Доступные команды:\n"
        "Меню - отобразить меню анимаций.\n"
        "р <текст> - показать текст с анимацией.\n"
        "\d - выбрать номер анимации из меню.\n"
    )
    await event.respond(help_text)

@client.on(events.NewMessage(pattern=r'Помощь'))
async def help_handler(event):
    await show_help(event)

async def main():
    print(f"Запуск main()... Версия скрипта {SCRIPT_VERSION}")
    
    # Настроим автозапуск
    setup_autostart()
    
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Вы авторизованы в Telegram.")
    
    # Печатаем инструкции по отключению автозапуска после старта бота
    print_autostart_instructions()

    # Получаем user_id
    await get_user_id()
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
