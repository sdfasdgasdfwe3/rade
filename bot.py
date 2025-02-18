import os
import sys
import signal
import logging
import atexit
import configparser
from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),  # Логи будут записываться в файл bot.log
        logging.StreamHandler(sys.stdout)  # Логи также будут выводиться в консоль
    ]
)
logger = logging.getLogger(__name__)

def debug_config():
    """Функция для отладки конфига"""
    logger.debug("\n=== ДЕБАГ КОНФИГА ===")
    logger.debug(f"Файл существует: {os.path.exists('config.ini')}")
    if os.path.exists('config.ini'):
        with open('config.ini', 'r') as f:
            content = f.read()
            logger.debug(f"Содержимое:\n{content}")
    logger.debug("====================\n")

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
            logger.info("✅ Конфиг валиден")
            return config
        except Exception as e:
            logger.error(f"❌ Ошибка в конфиге: {e}")
            debug_config()
    
    # Создание нового конфига
    logger.info("\n=== СОЗДАНИЕ НОВОГО КОНФИГА ===")
    config['pyrogram'] = {}
    
    # Ввод данных с проверкой
    while True:
        api_id = input("Введите API_ID: ").strip()
        if api_id.isdigit():
            break
        logger.warning("API_ID должен быть числом!")
    config['pyrogram']['api_id'] = api_id
    
    config['pyrogram']['api_hash'] = input("Введите API_HASH: ").strip()
    
    while True:
        phone = input("Номер телефона (+7...): ").strip()
        if phone:
            break
        logger.warning("Номер не может быть пустым!")
    config['pyrogram']['phone_number'] = phone
    
    # Запись и проверка
    with open(config_path, 'w', encoding='utf-8') as f:
        config.write(f)
    
    # Перечитываем для проверки
    new_config = configparser.ConfigParser()
    new_config.read(config_path)
    try:
        validate_config(new_config)
        logger.info("\n✅ Конфиг успешно создан!")
        return new_config
    except Exception as e:
        logger.critical(f"❌ Критическая ошибка: {e}")
        debug_config()
        raise

def cleanup():
    """Функция для выполнения очистки перед завершением программы"""
    logger.info("🛑 Выполняю очистку перед завершением...")
    # Добавьте сюда любые действия, которые нужно выполнить перед выходом
    # Например, закрытие соединений, удаление временных файлов и т.д.

def main():
    if not os.access(os.getcwd(), os.W_OK):
        logger.critical("❌ Нет прав на запись в текущую директорию!")
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
        logger.error(f"❌ Ошибка в данных: {e}")
        os.remove('config.ini')
        return main()

    # Регистрируем функцию cleanup для выполнения при завершении программы
    atexit.register(cleanup)

    # Обработчик сигналов для корректного завершения
    def signal_handler(signum, frame):
        logger.info("\n🛑 Получен сигнал завершения, останавливаю бота...")
        try:
            if app.is_connected:  # Проверяем, подключен ли клиент
                app.stop()
                logger.info("✅ Бот успешно остановлен.")
        except Exception as e:
            logger.error(f"❌ Ошибка при остановке бота: {e}")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    @app.on_message(filters.command("start"))
    def start(client, message):
        message.reply("⚡ Бот работает стабильно!")
        logger.info("Получена команда /start")

    try:
        # Запускаем клиент вручную, без контекстного менеджера
        app.start()
        logger.info("✅ Авторизация успешна! Бот запущен.")
        app.idle()  # Ожидаем входящих сообщений
    except SessionPasswordNeeded:
        logger.info("\n🔐 Требуется пароль двухэтапной аутентификации:")
        app.password = input("Пароль: ").strip()
        try:
            app.start()
            logger.info("✅ Авторизация с паролем успешна! Бот запущен.")
            app.idle()  # Ожидаем входящих сообщений
        except Exception as e:
            logger.error(f"❌ Ошибка: {e}")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        # Останавливаем клиент при завершении
        if app.is_connected:
            app.stop()
            logger.info("✅ Бот успешно остановлен.")

if __name__ == "__main__":
    main()  # Убираем цикл while True
