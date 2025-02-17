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
        await client.start(phone=PHONE_NUMBER, code_callback=lambda: input("Введите код подтверждения: "))
        logger.info("Авторизация успешна!")
    except SessionPasswordNeededError:
        password = input("Введите пароль двухэтапной аутентификации: ")
        await client.start(password=password)
    except Exception as e:
        logger.error(f"Ошибка авторизации: {e}")
        raise

async def main():
    try:
        await authorize()
        logger.info("Бот активен. Для выхода нажмите Ctrl+C.")
        
        while True:
            try:
                # Пример проверки активности Termux
                if os.system("pgrep termux > /dev/null") != 0:
                    logger.warning("Termux не активен!")
                
                await asyncio.sleep(60)
            except KeyboardInterrupt:
                logger.info("Завершение работы...")
                await client.disconnect()
                break
            except Exception as e:
                logger.error(f"Ошибка в цикле: {e}")
    except Exception as e:
        logger.error(f"Фатальная ошибка: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
