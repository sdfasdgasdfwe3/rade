import os
import asyncio
import sys
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

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
                raise ValueError("🔍 Проверьте config.txt!")
            
            return int(API_ID), API_HASH, PHONE_NUMBER
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        sys.exit(1)

API_ID, API_HASH, PHONE_NUMBER = load_config()
client = TelegramClient(f'session_{PHONE_NUMBER}', API_ID, API_HASH)

async def authorize():
    try:
        await client.start(
            phone=PHONE_NUMBER,
            code_callback=lambda: input("🔢 Введите код из Telegram: ")
        )
        print("✅ Успешная авторизация!")
    except SessionPasswordNeededError:
        print("🔐 Требуется пароль двухэтапной аутентификации!")
        password = input("🔑 Введите пароль: ")
        await client.sign_in(password=password)
        print("🎉 2FA пройдена!")
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        sys.exit(1)

async def main():
    try:
        await authorize()
        print("\n🤖 Бот активен. Закройте Termux для остановки.")
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("\n👋 Завершение работы...")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except Exception as e:
        print(f"💥 Ошибка: {e}")
        sys.exit(1)
