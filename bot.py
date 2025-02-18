import os
import configparser
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded

config = configparser.ConfigParser()

def load_or_create_config():
    config_path = 'config.ini'
    
    # Если конфиг не существует или пустой
    if not os.path.exists(config_path) or os.path.getsize(config_path) == 0:
        print("\n=== НАСТРОЙКА КОНФИГУРАЦИИ ===")
        config['pyrogram'] = {
            'api_id': input("Введите API_ID: ").strip(),
            'api_hash': input("Введите API_HASH: ").strip(),
            'phone_number': input("Введите номер телефона (+7XXXXXXXXXX): ").strip()
        }
        
        with open(config_path, 'w') as f:
            config.write(f)
        print("\n✅ Конфигурация сохранена!")
        return config
    
    # Если конфиг существует, проверяем его
    config.read(config_path)
    
    try:
        required = ['api_id', 'api_hash', 'phone_number']
        if not config.has_section('pyrogram'):
            raise ValueError("Отсутствует секция [pyrogram]")
            
        for key in required:
            if not config.get('pyrogram', key, fallback=None):
                raise ValueError(f"Отсутствует параметр: {key}")
                
    except Exception as e:
        print(f"\n❌ Ошибка в конфиге: {e}")
        os.remove(config_path)
        return load_or_create_config()
    
    return config

def main():
    # Загружаем или создаем конфиг
    config = load_or_create_config()
    
    # Инициализация клиента
    app = Client(
        "session",
        api_id=config.get('pyrogram', 'api_id'),
        api_hash=config.get('pyrogram', 'api_hash'),
        phone_number=config.get('pyrogram', 'phone_number')
    )
    
    # Обработка 2FA
    try:
        with app:
            print("✅ Авторизация успешна!")
    except SessionPasswordNeeded:
        print("\n⚠ Требуется двухэтапная аутентификация")
        app.password = input("Введите пароль: ").strip()
        try:
            with app:
                print("✅ Авторизация с паролем успешна!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            exit(1)

    # Обработчики сообщений
    @app.on_message(filters.command("start"))
    def start(client, message):
        message.reply("🚀 Бот работает! Используйте /help для справки")

    print("\nБот запущен...")
    app.run()

if __name__ == "__main__":
    main()
