import os
import re
import sys
import asyncio
import aiohttp
import subprocess
import shutil
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from configparser import ConfigParser

VERSION = "1.5"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
CONFIG_FILE = 'config.ini'
SESSION_FILE = 'session_name'

async def authenticate(client, phone):
    try:
        await client.send_code_request(phone)
        code = input("Введите код подтверждения из Telegram: ")
        return await client.sign_in(phone=phone, code=code)
    except PhoneCodeInvalidError:
        print("Неверный код подтверждения!")
        return await authenticate(client, phone)
    except SessionPasswordNeededError:
        password = input("Введите пароль двухфакторной аутентификации: ")
        return await client.sign_in(password=password)

async def main():
    print(f"🚀 Запуск бота версии {VERSION}")
    await self_update()
    
    config = create_or_read_config()
    client = TelegramClient(SESSION_FILE, 
                          int(config['api_id']), 
                          config['api_hash'])
    
    try:
        await client.start(phone=lambda: config['phone_number'])
        if not await client.is_user_authorized():
            print("🔐 Начинаем процесс авторизации...")
            await authenticate(client, config['phone_number'])
        
        print("✅ Успешная авторизация!")
        print("\n🛠️ Доступные команды:")
        print("/a - Выбор анимации")
        print("/update - Принудительное обновление")
        print("/exit - Выход из бота\n")

        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
            if cmd.strip() == '/update':
                await self_update()
            elif cmd.strip() == '/a':
                script_name = "animation_script.py"
                if not os.path.exists(script_name):
                    print(f"⛔ Скрипт {script_name} не найден!")
                else:
                    print(f"🚀 Запускаем {script_name}...")
                    await client.disconnect()
                    subprocess.Popen([sys.executable, script_name])
                    sys.exit(0)
            elif cmd.strip() == '/exit':
                await client.disconnect()
                sys.exit(0)
                
    except Exception as e:
        print(f"⛔ Ошибка: {str(e)}")
        await client.disconnect()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Работа бота завершена.")
