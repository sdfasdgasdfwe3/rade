import os
import configparser
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded

def setup_config():
    config = configparser.ConfigParser()
    config_path = 'config.ini'
    
    # Создаем новый конфиг при необходимости
    if not os.path.exists(config_path):
        print("\n=== НОВАЯ КОНФИГУРАЦИЯ ===")
        config['pyrogram'] = {
            'api_id': input("Введите API_ID: ").strip(),
            'api_hash': input("Введите API_HASH: ").strip(),
            'phone_number': input("Номер телефона (+79991234567): ").strip()
        }
        
        with open(config_path, 'w') as f:
            config.write(f)
        print("\n✅ Конфиг создан!")
        return config

    # Проверка существующего конфига
    try:
        config.read(config_path)
        
        if not config.has_section('pyrogram'):
            raise ValueError("Отсутствует секция [pyrogram]")
            
        required = ['api_id', 'api_hash', 'phone_number']
        for key in required:
            if not config.get('pyrogram', key, fallback=None):
                raise ValueError(f"Отсутствует параметр: {key}")
                
        print("✅ Конфиг валиден")
        return config
        
    except Exception as e:
        print(f"\n❌ Ошибка конфига: {e}")
        os.remove(config_path)
        return setup_config()

def main():
    # Инициализация конфига
    config = setup_config()
    
    # Создание клиента
    app = Client(
        "session",
        api_id=config.get('pyrogram', 'api_id'),
        api_hash=config.get('pyrogram', 'api_hash'),
        phone_number=config.get('pyrogram', 'phone_number')
    )
    
    # Авторизация
    try:
        with app:
            print("✅ Авторизация успешна!")
    except SessionPasswordNeeded:
        print("\n🔐 Введите пароль двухэтапной аутентификации:")
        app.password = input("Пароль: ").strip()
        try:
            with app:
                print("✅ Авторизация с паролем успешна!")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            exit(1)

    # Хэндлеры
    @app.on_message(filters.command("start"))
    def start(client, message):
        message.reply("🤖 Бот активен!")

    print("\n🚀 Бот запущен. Для остановки: Ctrl+C")
    app.run()

if __name__ == "__main__":
    main()
