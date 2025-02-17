import os
import time
import logging
from telethon import TelegramClient

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Чтение данных авторизации
def load_config():
    try:
        with open("config.txt", "r") as config_file:
            config = config_file.readlines()
        
        API_ID = config[0].strip().split('=')[1]
        API_HASH = config[1].strip().split('=')[1]
        PHONE_NUMBER = config[2].strip().split('=')[1]
        
        return API_ID, API_HASH, PHONE_NUMBER
    except Exception as e:
        logger.error(f"Ошибка при чтении config.txt: {e}")
        raise

# Создание клиента для авторизации
API_ID, API_HASH, PHONE_NUMBER = load_config()
client = TelegramClient('session_name', API_ID, API_HASH)

# Функция для авторизации
async def authorize():
    try:
        await client.start(phone=PHONE_NUMBER)
        logger.info("Авторизация успешна!")
    except Exception as e:
        logger.error(f"Ошибка при авторизации: {e}")
        raise

# Основная функция бота
async def main():
    try:
        await authorize()
        logger.info("Бот работает и готов к использованию.")
        
        # Периодически проверяем, что Termux открыт
        while True:
            try:
                time.sleep(60)  # Проверяем раз в минуту
            except KeyboardInterrupt:
                logger.info("Закрытие бота...")
                await client.disconnect()
                break
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")

# Запуск клиента
if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
