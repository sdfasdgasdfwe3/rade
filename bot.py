import os
import re
import sys
import asyncio
import aiohttp
import subprocess
import shutil  # Добавлен импорт shutil
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from configparser import ConfigParser

VERSION = "1.5"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
CONFIG_FILE = 'config.ini'
SESSION_FILE = 'session_name'

def parse_version(version_str):
    return tuple(map(int, version_str.split('.')))

async def check_update():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GITHUB_RAW_URL) as response:
                remote_code = await response.text()
                remote_version = re.search(r"VERSION\s*=\s*['\"](.*?)['\"]", remote_code).group(1)
                
                if parse_version(remote_version) > parse_version(VERSION):
                    return True, remote_code
    except Exception as e:
        print(f"Ошибка проверки обновлений: {str(e)}")
    return False, None

async def self_update():
    print("♻️ Начинаем процесс обновления...")
    try:
        update_available, new_code = await check_update()
        if not update_available:
            print("✅ У вас актуальная версия бота")
            return

        # Список защищенных файлов
        protected_files = {
            os.path.abspath(CONFIG_FILE),
            os.path.abspath(f"{SESSION_FILE}.session"),
            os.path.abspath(__file__)
        }

        # Удаляем все файлы и папки кроме защищенных
        current_dir = os.getcwd()
        for root, dirs, files in os.walk(current_dir, topdown=False):
            for name in files + dirs:
                full_path = os.path.abspath(os.path.join(root, name))
                
                if any(full_path.startswith(p) for p in protected_files):
                    continue
                
                try:
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                        print(f"🗑 Удален файл: {full_path}")
                    else:
                        shutil.rmtree(full_path)
                        print(f"🗑 Удалена директория: {full_path}")
                except Exception as e:
                    print(f"⚠️ Ошибка удаления {full_path}: {str(e)}")

        # Записываем новую версию
        with open(__file__, 'w', encoding='utf-8') as f:
            f.write(new_code)

        print("🔄 Бот успешно обновлен! Перезапускаем...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        print(f"⛔ Ошибка при обновлении: {str(e)}")

async def update_checker():
    while True:
        await asyncio.sleep(3600)
        await self_update()

def create_or_read_config():
    config = ConfigParser()
    
    if not os.path.exists(CONFIG_FILE):
        print("🔧 Конфигурационный файл не найден. Создаем новый...")
        
        config['Telegram'] = {
            'api_id': input("Введите ваш API ID: "),
            'api_hash': input("Введите ваш API HASH: "),
            'phone_number': input("Введите номер телефона (с кодом страны): ")
        }
        
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
        print(f"💾 Конфигурация сохранена в {CONFIG_FILE}")
    
    config.read(CONFIG_FILE)
    return config['Telegram']

async def main():
    print(f"🚀 Запуск бота версии {VERSION}")
    await self_update()  # Проверка обновлений при старте
    
    config = create_or_read_config()
    
    client = TelegramClient(
        SESSION_FILE,
        int(config['api_id']),
        config['api_hash']
    )
    
    await client.start(phone=config['phone_number'])
    
        # ... остальной код ...

    print("\n🛠️ Доступные команды:")
    print("/a - Выбор анимации")
    print("/update - Принудительное обновление")
    print("/exit - Выход из бота\n")

    # Исправлено: выравнивание цикла while и его тела
    while True:
        cmd = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
        if cmd.strip() == '/update':
            await self_update()
        elif cmd.strip() == '/a':  # Добавлено
            script_name = "animation_script.py"
            if not os.path.exists(script_name):
                print(f"⛔ Скрипт {script_name} не найден!")
            else:
                print(f"🚀 Запускаем {script_name}...")
                await client.disconnect()
                subprocess.Popen([sys.executable, script_name])
                sys.exit(0)
        elif cmd.strip() == '/exit':
            sys.exit(0)

# ... (импорты и предыдущий код остаются без изменений)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except SessionPasswordNeededError:
        print("\n🔐 Требуется двухфакторная аутентификация!")
        # Читаем конфиг заново
        config = ConfigParser()
        config.read(CONFIG_FILE)
        password = input("Введите пароль: ")
        with TelegramClient(SESSION_FILE, 
                          int(config['Telegram']['api_id']), 
                          config['Telegram']['api_hash']) as client:
            client.start(password=password)
        print("✅ Пароль успешно проверен! Перезапустите бота.")
    except KeyboardInterrupt:
        print("\n🛑 Работа бота завершена.")
    except Exception as e:
        print(f"⛔ Критическая ошибка: {str(e)}")
