import os
import sys
import configparser
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded, BadRequest

def debug_config():
    """Отладка конфигурационного файла"""
    print("\n=== ДЕБАГ КОНФИГА ===")
    print(f"Существует: {os.path.exists('config.ini')}")
    if os.path.exists('config.ini'):
        with open('config.ini', 'r') as f:
            print(f"Содержимое:\n{f.read()}")
    print("====================\n")

def validate_config(config):
    """Проверка валидности конфига"""
    if not config.has_section('pyrogram'):
        raise ValueError("Отсутствует секция [pyrogram]")
    required = ['api_id', 'api_hash', 'phone_number']
    for key in required:
        if not config.get('pyrogram', key, fallback=None):
            raise ValueError(f"Не указан {key}")

def setup_config():
    """Создание или загрузка конфигурации"""
    config = configparser.ConfigParser()
    config_path = os.path.abspath('config.ini')
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config.read_file(f)
            validate_config(config)
            print("✅ Конфиг загружен")
            return config
        except Exception as e:
            print(f"❌ Ошибка в конфиге: {e}")
            debug_config()
            os.remove(config_path)
            return setup_config()
    
    # Создание нового конфига
    print("\n=== СОЗДАНИЕ НОВОГО КОНФИГА ===")
    config['pyrogram'] = {}
    
    # Ввод API_ID
    while True:
        api_id = input("Введите API_ID: ").strip()
        if api_id.isdigit():
            config['pyrogram']['api_id'] = api_id
            break
        print("API_ID должен быть числом!")
    
    # Ввод API_HASH
    config['pyrogram']['api_hash'] = input("Введите API_HASH: ").strip()
    
    # Ввод номера телефона
    while True:
        phone = input("Номер телефона (+7...): ").strip()
        if phone:
            config['pyrogram']['phone_number'] = phone
            break
        print("Номер не может быть пустым!")
    
    # Сохранение конфига
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)
    
    # Валидация
    try:
        validate_config(config)
        print("\n✅ Конфиг успешно создан!")
        return config
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        debug_config()
        os.remove(config_path)
        return setup_config()

def check_session():
    """Проверка существующей сессии"""
    return os.path.exists("session.session")

def auth_client(app):
    """Процесс авторизации"""
    try:
        print("\n🔐 Начало авторизации...")
        app.connect()
        
        sent_code = app.send_code(app.phone_number)
        code = input("\nВведите код из Telegram: ").strip()
        
        try:
            app.sign_in(app.phone_number, sent_code.phone_code_hash, code)
        except SessionPasswordNeeded:
            password = input("Введите пароль 2FA: ").strip()
            app.check_password(password)
        
        print("\n✅ Авторизация успешна!")
        return True
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        return False
    finally:
        app.disconnect()

def main():
    # Проверка прав
    if not os.access(os.getcwd(), os.W_OK):
        print("❌ Нет прав на запись!")
        sys.exit(1)
    
    # Настройка конфига
    config = setup_config()
    
    # Инициализация клиента
    app = Client(
        "session",
        api_id=int(config.get('pyrogram', 'api_id')),
        api_hash=config.get('pyrogram', 'api_hash'),
        phone_number=config.get('pyrogram', 'phone_number'),
        app_version="RadeBot 2.0",
        system_version="Termux 1.0",
        workers=1
    )
    
    # Авторизация при необходимости
    if not check_session():
        if not auth_client(app):
            print("🚫 Не удалось авторизоваться")
            sys.exit(1)
    
    # Запуск бота
    try:
        with app:
            print("\n✅ Сессия активна")
            me = app.get_me()
            print(f"👤 Авторизован как: {me.first_name}")
            
            @app.on_message(filters.command("start"))
            def start(client, message):
                message.reply("⚡ Бот работает!")
            
            print("\n🚀 Бот запущен. Ctrl+C для остановки")
            app.run()
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    while True:
        try:
            main()
            break
        except KeyboardInterrupt:
            print("\n🛑 Остановлено")
            break
        except Exception as e:
            print(f"🔄 Перезапуск из-за ошибки: {e}")
            if input("Повторить? (y/n): ").lower() != 'y':
                break
