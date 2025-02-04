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

VERSION = "1.8"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
CONFIG_FILE = 'config.ini'
SESSION_FILE = 'rade_session'

def create_config():
    """Создает конфигурационный файл с пояснениями"""
    config = ConfigParser()
    
    config['Telegram'] = {
        '# Получите API ID и Hash на my.telegram.org': None,
        'api_id': 'ВАШ_API_ID',
        'api_hash': 'ВАШ_API_HASH',
        '# Номер в международном формате': None,
        'phone_number': '+79991234567'
    }

    with open(CONFIG_FILE, 'w') as f:
        config.write(f)

    print(f"""
    =============================================
    Создан новый конфигурационный файл {CONFIG_FILE}
    
    1. Зарегистрируйте приложение здесь:
       https://my.telegram.org/apps
       
    2. Введите полученные данные в конфиг:
       - api_id (цифры)
       - api_hash (32 символа)
       - номер телефона с кодом страны
    
    3. Сохраните файл и перезапустите бота
    =============================================
    """)
    sys.exit()

def validate_config(config):
    """Проверяет корректность конфигурации"""
    required = {
        'api_id': ("Введите API ID (цифры)", r'^\d+$'),
        'api_hash': ("Введите API Hash (32 символа)", r'^[a-f0-9]{32}$'),
        'phone_number': ("Введите номер телефона", r'^\+[0-9]{9,15}$')
    }

    for key, (message, pattern) in required.items():
        value = config.get('Telegram', key)
        if 'ВАШ_' in value or not re.match(pattern, value):
            print(f"\n❌ Ошибка в параметре {key}:")
            print(f"   - {message}")
            print(f"   - Текущее значение: {value}")
            print("\n⚠️ Исправьте конфиг и перезапустите бота")
            sys.exit(1)

async def self_update():
    """Система автоматического обновления"""
    print("🔍 Проверка обновлений...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GITHUB_RAW_URL) as response:
                if response.status == 200:
                    new_content = await response.text()
                    version_match = re.search(r'VERSION\s*=\s*"([\d.]+)"', new_content)
                    
                    if version_match and version_match.group(1) > VERSION:
                        print(f"🆕 Обнаружена версия {version_match.group(1)}, обновление...")
                        with open('bot_temp.py', 'w') as f:
                            f.write(new_content)
                        shutil.move('bot_temp.py', __file__)
                        print("✅ Обновление завершено. Перезапуск...")
                        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        print(f"⚠️ Ошибка обновления: {e}")

async def main():
    # Проверка и создание конфига
    if not os.path.exists(CONFIG_FILE):
        create_config()
    
    # Проверка конфига
    config = ConfigParser()
    config.read(CONFIG_FILE)
    validate_config(config)
    tg_config = config['Telegram']

    # Инициализация клиента
    client = TelegramClient(
        SESSION_FILE,
        int(tg_config['api_id']),
        tg_config['api_hash']
    )

    # Процесс авторизации
    try:
        if not await client.is_user_authorized():
            print("\n🔐 Начинаем авторизацию...")
            await client.start(
                phone=lambda: tg_config['phone_number'],
                code_callback=lambda: input("✉️ Введите код из Telegram: "),
                password=lambda: input("🔑 Введите пароль 2FA: ")
            )
            print("✅ Авторизация успешна!")
    except Exception as e:
        print(f"🚨 Ошибка авторизации: {e}")
        sys.exit(1)

    # Основной интерфейс
    print(f"""
    ============================
    Бот успешно запущен! 
    Версия: {VERSION}
    Номер: {tg_config['phone_number']}
    Команды:
    /a - Запуск анимации
    /update - Проверить обновления
    /exit - Выход
    ============================
    """)

    while True:
        cmd = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
        if cmd == '/a':
            # Логика запуска анимации
            pass
        elif cmd == '/update':
            await self_update()
        elif cmd == '/exit':
            await client.disconnect()
            sys.exit()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Работа бота завершена.")
