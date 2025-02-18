import os
import configparser
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded, BadRequest

config = configparser.ConfigParser()

def setup_config():
    if not os.path.exists('config.ini'):
        print("Первоначальная настройка:")
        config['pyrogram'] = {
            'api_id': input("Введите API_ID: "),
            'api_hash': input("Введите API_HASH: "),
            'phone_number': input("Введите номер телефона (с кодом страны): ")
        }
        with open('config.ini', 'w') as f:
            config.write(f)
    else:
        config.read('config.ini')

def get_client():
    return Client(
        "session",
        api_id=config.get('pyrogram', 'api_id'),
        api_hash=config.get('pyrogram', 'api_hash'),
        phone_number=config.get('pyrogram', 'phone_number')
    )

def main():
    setup_config()
    app = get_client()
    
    try:
        with app:
            print("✓ Успешная авторизация!")
    except SessionPasswordNeeded:
        print("⚠ Требуется двухэтапная аутентификация")
        app.password = input("Введите пароль: ")
        try:
            with app:
                print("✓ Успешная авторизация с паролем!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            exit()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        exit()

    @app.on_message(filters.command("start"))
    def handle_start(client, message):
        message.reply("🚀 Бот успешно запущен!")

    print("\nБот работает...")
    app.run()

if __name__ == "__main__":
    main()
