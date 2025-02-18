import os
import configparser
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded

config = configparser.ConfigParser()

def validate_config():
    try:
        # Проверка существования секции
        if not config.has_section('pyrogram'):
            raise ValueError("Отсутствует секция [pyrogram] в конфиге")
            
        # Проверка обязательных полей
        required = ['api_id', 'api_hash', 'phone_number']
        for key in required:
            if not config.get('pyrogram', key, fallback=None):
                raise ValueError(f"Не заполнено поле: {key}")
                
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def setup_config():
    if not os.path.exists('config.ini'):
        print("\n=== НАСТРОЙКА КОНФИГУРАЦИИ ===")
        config['pyrogram'] = {
            'api_id': input("Введите API_ID: ").strip(),
            'api_hash': input("Введите API_HASH: ").strip(),
            'phone_number': input("Введите номер телефона (+7XXX...): ").strip()
        }
        with open('config.ini', 'w') as f:
            config.write(f)
        print("\n✅ Конфиг успешно создан!")
        return
    
    # Если конфиг существует, но поврежден
    config.read('config.ini')
    if not validate_config():
        print("Удаляю поврежденный конфиг...")
        os.remove('config.ini')
        setup_config()

def get_client():
    return Client(
        "session",
        api_id=config.get('pyrogram', 'api_id'),
        api_hash=config.get('pyrogram', 'api_hash'),
        phone_number=config.get('pyrogram', 'phone_number'),
        app_version="RadeBot 1.0"
    )

def handle_2fa(app):
    try:
        with app:
            print("✅ Авторизация успешна!")
    except SessionPasswordNeeded:
        print("\n⚠ Требуется двухэтапная аутентификация")
        password = input("Введите пароль: ").strip()
        app.password = password
        try:
            with app:
                print("✅ Авторизация с паролем успешна!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            exit(1)

def main():
    setup_config()
    config.read('config.ini')
    
    app = get_client()
    handle_2fa(app)

    @app.on_message(filters.command("start"))
    def start_handler(client, message):
        message.reply_text("🤖 Бот активен! Используйте /help для списка команд")

    print("\n🚀 Бот запущен. Нажмите Ctrl+C для остановки")
    app.run()

if __name__ == "__main__":
    main()
