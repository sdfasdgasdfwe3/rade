import os
import sys
import signal
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
    
    print("\n=== СОЗДАНИЕ НОВОГО КОНФИГА ===")
    config['pyrogram'] = {}
    
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
    
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)
    
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
    """Завершает активные сессии и удаляет поврежденные файлы"""
    try:
        if os.path.exists("session.session"):
            os.remove("session.session")
            print("🛑 Удален поврежденный файл сессии")
    except Exception as e:
        print(f"❌ Ошибка при очистке сессии: {e}")

def main():
    if not os.access(os.getcwd(), os.W_OK):
        print("❌ Нет прав на запись в текущую директорию!")
        sys.exit(1)
    
    cleanup_session()
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
    
    def signal_handler(signum, frame):
        print("\n🛑 Получен сигнал завершения, останавливаю бота...")
        app.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    @app.on_message(filters.command("start"))
    def start(client, message):
        message.reply("⚡️ Бот работает стабильно!")
    
    try:
        app.start()
        print("✅ Авторизация успешна!")
        print("🚀 Бот запущен. Ожидание сообщений...")
        app.run()
    except SessionPasswordNeeded:

print("\n🔐 Требуется пароль 2FA:")
        app.password = input("Пароль: ").strip()
        try:
            app.start()
            print("✅ Авторизация с паролем успешна!")
            app.run()
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            sys.exit(1)
    except BadRequest as e:
        print(f"❌ Ошибка в запросе: {e}")
        cleanup_session()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        app.stop()

if name == "main":
    main()
