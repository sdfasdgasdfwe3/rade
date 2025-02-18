import os
import sys
import configparser
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded

def debug_config():
    """Функция для отладки конфига"""
    print("\n=== ДЕБАГ КОНФИГА ===")
    print(f"Файл существует: {os.path.exists('config.ini')}")
    if os.path.exists('config.ini'):
        with open('config.ini', 'r') as f:
            content = f.read()
            print(f"Содержимое:\n{content}")
    print("====================\n")

def setup_config():
    config = configparser.ConfigParser()
    config_path = os.path.abspath('config.ini')
    
    try:
        # Принудительная проверка существования файла
        if not os.path.exists(config_path):
            raise FileNotFoundError("Конфиг не найден")
            
        # Чтение с проверкой кодировки
        with open(config_path, 'r', encoding='utf-8') as f:
            config.read_file(f)
            
        # Жесткая проверка структуры
        if not config.has_section('pyrogram'):
            raise ValueError("Секция [pyrogram] отсутствует")
            
        required = {
            'api_id': "API_ID не найден",
            'api_hash': "API_HASH не найден", 
            'phone_number': "Номер телефона не указан"
        }
        
        for key, error_msg in required.items():
            if not config.get('pyrogram', key, fallback=None):
                raise ValueError(error_msg)
                
        print("✅ Конфиг валиден")
        return config
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        debug_config()
        
        # Пересоздание конфига
        print("\n=== ПЕРЕСОЗДАНИЕ КОНФИГА ===")
        config['pyrogram'] = {
            'api_id': input("Введите API_ID: ").strip(),
            'api_hash': input("Введите API_HASH: ").strip(),
            'phone_number': input("Номер телефона (+7...): ").strip()
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
            
        print("\n✅ Конфиг пересоздан!")
        return config

def main():
    # Принудительная проверка прав
    if not os.access(os.getcwd(), os.W_OK):
        print("❌ Нет прав на запись в текущую директорию!")
        sys.exit(1)
        
    config = setup_config()
    
    # Инициализация клиента с проверкой значений
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
        print(f"❌ Неверный API_ID: {e}")
        os.remove('config.ini')
        return main()

    # Авторизация
    try:
        with app:
            print("✅ Авторизация успешна!")
    except SessionPasswordNeeded:
        print("\n🔐 Требуется пароль двухэтапной аутентификации:")
        app.password = input("Пароль: ").strip()
        try:
            with app:
                print("✅ Авторизация с паролем успешна!")
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            sys.exit(1)

    @app.on_message(filters.command("start"))
    def start(client, message):
        message.reply("⚡ Бот работает стабильно!")

    print("\n🚀 Бот запущен. Для выхода: Ctrl+C")
    app.run()

if __name__ == "__main__":
    # Принудительный сброс при ошибках
    while True:
        try:
            main()
            break
        except Exception as e:
            print(f"🛑 Непредвиденная ошибка: {e}")
            answer = input("Попробовать снова? (y/n): ").strip().lower()
            if answer != 'y':
                break
