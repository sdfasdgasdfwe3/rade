import asyncio  # Импортируем asyncio для работы с асинхронным кодом
import subprocess
import os  # Добавлен импорт модуля os
import requests
import json
from telethon import TelegramClient, events, Button

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"  # Исправленный URL
SCRIPT_VERSION = "0.0.3"
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = "\u2588"  # Символ по умолчанию для анимации

# Функция для отмены локальных изменений в git
def discard_local_changes():
    """Отменить локальные изменения в файле bot.py."""
    try:
        print("Отмена локальных изменений в файле bot.py...")
        subprocess.run(["git", "checkout", "--", "bot.py"], check=True)
        print("Локальные изменения в файле bot.py были отменены.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при отмене изменений: {e}")

# Функция для проверки обновлений скрипта на GitHub
def check_for_updates():
    """Проверка наличия обновлений скрипта на GitHub."""
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

            # Проверяем наличие строки "SCRIPT_VERSION" в обоих скриптах
            if "SCRIPT_VERSION" in remote_script and "SCRIPT_VERSION" in current_script:
                remote_version_line = [
                    line for line in remote_script.splitlines() if "SCRIPT_VERSION" in line
                ]
                if remote_version_line:
                    remote_version = remote_version_line[0].split('=')[1].strip().strip('"')
                    if SCRIPT_VERSION != remote_version:
                        print(f"Доступна новая версия скрипта: {remote_version} (текущая: {SCRIPT_VERSION})")
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
            print(f"Не удалось проверить обновления. Код ответа сервера: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {e}")

# Функция для настройки автозапуска
def setup_autostart():
    """Функция для настройки автозапуска бота в Termux при старте устройства"""
    boot_directory = os.path.expanduser("~/.termux/boot")
    
    # Проверяем, существует ли папка для автозапуска
    if not os.path.exists(boot_directory):
        os.makedirs(boot_directory)
        print(f"Папка {boot_directory} создана.")
    
    # Путь к скрипту автозапуска
    script_path = os.path.join(boot_directory, "start_bot.sh")
    
    # Путь к вашему скрипту бота
    bot_script_path = "/data/data/com.termux/files/home/rade/bot.py"  # Измените на актуальный путь
    
    # Создаем скрипт для автозапуска
    with open(script_path, "w") as f:
        f.write(f"""#!/data/data/com.termux/files/usr/bin/bash
cd /data/data/com.termux/files/home/rade  # Путь к вашему боту
python3 {bot_script_path}  # Запуск бота
""")
    
    # Даем права на исполнение скрипту
    os.chmod(script_path, 0o755)
    
    print(f"Автозапуск настроен. Скрипт сохранен в {script_path}.")

# Функция для удаления автозапуска
def remove_autostart():
    """Функция для удаления автозапуска бота в Termux"""
    boot_directory = os.path.expanduser("~/.termux/boot")
    script_path = os.path.join(boot_directory, "start_bot.sh")
    
    if os.path.exists(script_path):
        os.remove(script_path)
        print(f"Автозапуск удален. Скрипт {script_path} больше не будет запускаться при старте.")
    else:
        print("Скрипт автозапуска не найден. Возможно, он уже был удален.")

# Выводим инструкцию по отключению автозапуска
def print_autostart_instructions():
    """Выводим информацию по отключению автозапуска"""
    print("\nДля отключения автозапуска скрипта бота выполните следующую команду в Termux:")
    print("Удаление автозапуска:")
    print("  python3 <путь_к_скрипту>/bot.py --remove-autostart")
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
        print(f"Ошибка чтения конфигурации: {e}. Удалите {CONFIG_FILE} и попробуйте снова.")
        exit(1)
else:
    API_ID = None
    API_HASH = None
    PHONE_NUMBER = None

# Уникальное имя файла для сессии
SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}' if PHONE_NUMBER else 'session_temp'

# Инициализация клиента
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Добавляем команду /reg для регистрации и авторизации
@client.on(events.NewMessage(pattern='/reg'))
async def handle_reg(event):
    """Команда для запроса данных и авторизации."""
    if not API_ID or not API_HASH or not PHONE_NUMBER:
        # Запрашиваем данные у пользователя
        await event.respond(
            "Для регистрации мне нужны ваши данные. Пожалуйста, введите ваш API ID."
        )
        return

    # Печатаем вопрос о завершении регистрации
    await event.respond(
        "Хотите пройти авторизацию? Нажмите 'Да' для подтверждения или 'Нет' для отмены.",
        buttons=[
            [Button.text('Да', resize=True), Button.text('Нет', resize=True)]
        ]
    )

@client.on(events.CallbackQuery)
async def handle_callback(event):
    """Обработка нажатий кнопок 'Да' или 'Нет'."""
    if event.data.decode() == 'Да':
        # Запрашиваем номер телефона, если еще не указан
        if not PHONE_NUMBER:
            await event.respond("Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX):")
        else:
            # Если все данные есть, начинаем авторизацию
            await event.respond("Авторизация начинается...")
            await client.start(phone=PHONE_NUMBER)
            await event.respond("Вы успешно авторизовались в Telegram!")
    elif event.data.decode() == 'Нет':
        await event.respond("Авторизация отменена.")

@client.on(events.NewMessage)
async def handle_new_message(event):
    """Обработка ввода данных для регистрации."""
    global API_ID, API_HASH, PHONE_NUMBER

    if API_ID is None:
        API_ID = int(event.text)
        await event.respond(f"API ID получен: {API_ID}. Пожалуйста, введите ваш API Hash.")
        return
    if API_HASH is None:
        API_HASH = event.text
        await event.respond(f"API Hash получен: {API_HASH}. Пожалуйста, введите ваш номер телефона.")
        return
    if PHONE_NUMBER is None:
        PHONE_NUMBER = event.text.strip()
        await event.respond(f"Номер телефона получен: {PHONE_NUMBER}.")
        await event.respond(
            "Теперь вы можете пройти авторизацию. Для этого нажмите 'Да' или 'Нет'.",
            buttons=[
                [Button.text('Да', resize=True), Button.text('Нет', resize=True)]
            ]
        )

async def main():
    print(f"Запуск main()\nВерсия скрипта: {SCRIPT_VERSION}")
    
    # Настроим автозапуск
    setup_autostart()
    
    check_for_updates()
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Вы авторизованы в Telegram.")
    print("Для использования анимации текста используйте команду /p <ваш текст>.")
    
    # Печатаем инструкции по отключению автозапуска после старта бота
    print_autostart_instructions()
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    check_for_updates()
    asyncio.run(main())  # Теперь asyncio импортирован и main() может быть вызван
