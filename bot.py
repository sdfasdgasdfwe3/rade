import os
import asyncio
import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    try:
        with open("config.txt", "r") as f:
            config = {}
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
            
            API_ID = config.get("API_ID")
            API_HASH = config.get("API_HASH")
            PHONE_NUMBER = config.get("PHONE_NUMBER")
            
            if not all([API_ID, API_HASH, PHONE_NUMBER]):
                raise ValueError("Не все параметры указаны в config.txt")
            
            return int(API_ID), API_HASH, PHONE_NUMBER
    except Exception as e:
        logger.error(f"Ошибка конфигурации: {e}")
        raise

API_ID, API_HASH, PHONE_NUMBER = load_config()
client = TelegramClient(f'session_{PHONE_NUMBER}', API_ID, API_HASH)

async def authorize():
    try:
        await client.start(
            phone=PHONE_NUMBER,
            code_callback=lambda: input("Введите код подтверждения из Telegram: "),
            password=lambda: input("Введите пароль двухэтапной аутентификации: ") if input("Требуется пароль? (y/n): ").lower() == "y" else None
        )
        logger.info("Авторизация успешна!")
    except Exception as e:
        logger.error(f"Ошибка авторизации: {e}")
        raise

async def main():
    try:
        await authorize()
        logger.info("Бот активен. Для выхода нажмите Ctrl+C.")
        while True:
            await asyncio.sleep(3600)  # Бесконечный цикл
    except KeyboardInterrupt:
        logger.info("Завершение работы...")
    except Exception as e:
        logger.error(f"Фатальная ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
