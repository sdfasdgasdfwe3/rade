import os
import sys
import signal
import atexit
import configparser
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded, BadRequest

def debug_config():
    """Функция для отладки конфига"""
    print("\n=== ДЕБАГ КОНФИГА ===")
    print(f"Файл существует: {os.path.exists('config.ini')}")
    if os.path.exists('config.ini'):
        with open('config.ini', 'r') as f:
            content = f.read()
            print(f"Содержимое:\n{content}")
    print("====================\n")

def validate_config(config):
    """Проверка валидности конфига"""
    if not config.has_section('pyrogram'):
        raise ValueError("Секция [pyrogram] отсутствует")
    required = ['api_id', 'api_hash', 'phone_number']
    for key in required:
        if not config.get('pyrogram', key, fallback=None):
            raise ValueError(f"Не указан {key}")

def setup_config():
    config_path = os.path.abspath('config.ini')
    config = configparser.ConfigParser()
    
    # Попытка чтения существующего конфига
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config.read_file(f)
            validate_config(config)
            print("✅ Конфиг валиден")
            return config
        except Exception as e:
            print(f"❌ Ошибка в конфиге: {e}")
            debug_config()
    
    # Создание нового конфига
    print("\n=== СОЗДАНИЕ НОВОГО КОНФИГА ===")
    config['pyrogram'] = {}
    
    # Ввод данных с проверкой
    while True:
        api_id = input("Введите API_ID: ").strip()
        if api_id.isdigit():
            break
        print("API_ID должен быть числом!")
    config['pyrogram']['api_id'] = api_id
    
    config['pyrogram']['api_hash'] = input("Введите API_HASH: ").strip()
    
    while True:
        phone = input("Номер телефона (+7...): ").strip()
        if phone:
            break
        print("Номер не может быть пустым!")
    config['pyrogram']['phone_number'] = phone
    
    # Запись и проверка
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)
    
    # Перечитываем для проверки
    new_config = configparser.ConfigParser()
    new_config.read(config_path)
    try:
        validate_config(new_config)
        print("\n✅ Конфиг успешно создан!")
        return new_config
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        debug_config()
        raise

def cleanup_session():
    """Очистка сессии, если она заблокирована"""
    session_file = "session.session"
    if os.path.exists(session_file):
        try:
            os.remove(session_file)
            print("⚠️ Удалена заблокированная сессия.")
        except Exception as e:
            print(f"❌ Не удалось удалить сессию: {e}")

def graceful_shutdown(app):
    """Функция для корректного завершения работы"""
    print("\n🛑 Завершение работы бота...")
    try:
        app.stop()
        print("✅ Сессия Telegram завершена.")
    except Exception as e:
        print(f"❌ Ошибка при завершении сессии: {e}")
    sys.exit(0)

def main():
    if not os.access(os.getcwd(), os.W_OK):
        print("❌ Нет прав на запись в текущую директорию!")
        sys.exit(1)
        
    config = setup_config()
    
    try:
        app = Client(
            "session",
            api_id=int(config.get('pyrogram', 'api_id')),
            api_hash=config.get('pyrogram', 'api_hash'),
            phone_number=config.get('pyrogram', 'phone_number'),
            app_version="RadeBot 2.0",
            system_version="Termux 1.0"
        )
    except ValueError as e:
        print(f"❌ Ошибка в данных: {e}")
        os.remove('config.ini')
        return main()

    # Обработчик сигналов для корректного завершения
    def signal_handler(signum, frame):
        graceful_shutdown(app)

    # Регистрация обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Сигнал завершения
    atexit.register(graceful_shutdown, app)  # При завершении работы Python

    @app.on_message(filters.command("start"))
    def start(client, message):
        message.reply("⚡ Бот работает стабильно!")

    try:
        with app:
            print("✅ Авторизация успешна!")
            app.run()  # Запускаем бота внутри контекстного менеджера
    except SessionPasswordNeeded:
        print("\n🔐 Требуется пароль двухэтапной аутентификации:")
        app.password = input("Пароль: ").strip()
        try:
            with app:
                print("✅ Авторизация с паролем успешна!")
                app.run()  # Запускаем внутри контекста
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            sys.exit(1)
    except BadRequest as e:
        if "database is locked" in str(e):
            print("❌ База данных заблокирована. Очищаю сессию...")
            cleanup_session()
            print("🔄 Попробуйте запустить бота снова.")
        else:
            print(f"❌ Ошибка BadRequest: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()  # Убираем цикл while True
