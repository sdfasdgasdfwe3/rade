from telethon import TelegramClient, events

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"  # Исправленный URL
SCRIPT_VERSION = "0.0.6"
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
    typing_speed = DEFAULT_TYPING_SPEED
    cursor_symbol = DEFAULT_CURSOR

# Уникальное имя файла для сессии
SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}' if PHONE_NUMBER else 'session'

# Инициализация клиента
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Команда для регистрации вручную
@client.on(events.NewMessage(pattern=r'/reg'))
async def manual_registration(event):
    """Команда для ручной авторизации"""
    global API_ID, API_HASH, PHONE_NUMBER
    
    if not API_ID or not API_HASH or not PHONE_NUMBER:
        await event.reply("Вы не авторизованы. Пожалуйста, предоставьте ваш API ID, API Hash и номер телефона.")
        
        # Запрашиваем API_ID, API_HASH, PHONE_NUMBER
        try:
            API_ID = int(input("Введите ваш API ID: "))
            API_HASH = input("Введите ваш API Hash: ").strip()
            PHONE_NUMBER = input("Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX): ").strip()
            
            # Сохраняем данные в файл конфигурации
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "API_ID": API_ID,
                    "API_HASH": API_HASH,
                    "PHONE_NUMBER": PHONE_NUMBER,
                    "typing_speed": typing_speed,
                    "cursor_symbol": cursor_symbol
                }, f)
            await event.reply(f"Данные сохранены. Попробуйте авторизоваться!")
        except Exception as e:
            await event.reply(f"Ошибка сохранения конфигурации: {e}")
            return
    else:
        await event.reply("Авторизация уже выполнена.")

# Основная функция
async def main():
    print(f"Запуск main()\nВерсия скрипта: {SCRIPT_VERSION}")
    
    # Настроим автозапуск
    setup_autostart()
    
    check_for_updates()
    
    if PHONE_NUMBER:
        await client.start(phone=PHONE_NUMBER)
        print("Скрипт успешно запущен! Вы авторизованы в Telegram.")
    else:
        print("Не удалось найти номер телефона. Пожалуйста, авторизуйтесь с помощью команды /reg.")
        
    print("Для использования анимации текста используйте команду /p <ваш текст>.")    
    
    # Печатаем инструкции по отключению автозапуска после старта бота
    print_autostart_instructions()
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    check_for_updates()
    asyncio.run(main())  # Теперь asyncio импортирован и main() может быть вызван
