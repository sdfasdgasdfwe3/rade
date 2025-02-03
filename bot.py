import os
import re
import sys
import asyncio
import aiohttp
import shutil
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from configparser import ConfigParser
import animation_script

VERSION = "1.2"
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
        temp_dir = "temp_update"
        os.makedirs(temp_dir, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            files_to_update = {
                "bot.py": GITHUB_RAW_URL,
                "animation_script.py": GITHUB_RAW_URL.replace("bot.py", "animation_script.py")
            }
            
            for filename, url in files_to_update.items():
                async with session.get(url) as response:
                    with open(os.path.join(temp_dir, filename), 'wb') as f:
                        f.write(await response.read())
            
            gitignore_lines = [
                "session_name.session\n",
                "*.session\n",
                "config.ini\n"
            ]
            if os.path.exists(".gitignore"):
                with open(".gitignore", "r+") as f:
                    content = f.read()
                    for line in gitignore_lines:
                        if line.strip() not in content:
                            f.write(line)
            else:
                with open(".gitignore", "w") as f:
                    f.writelines(gitignore_lines)
            
            for filename in files_to_update.keys():
                if os.path.exists(filename):
                    os.remove(filename)
                shutil.move(os.path.join(temp_dir, filename), filename)
            
            shutil.rmtree(temp_dir)
            
        print("🔄 Бот успешно обновлен! Перезапускаем...")
        os.execl(sys.executable, sys.executable, *sys.argv)
        
    except Exception as e:
        print(f"⛔ Ошибка при обновлении: {str(e)}")
        if os.path.exists(temp_dir):
            for filename in files_to_update.keys():
                if os.path.exists(os.path.join(temp_dir, filename)):
                    shutil.move(os.path.join(temp_dir, filename), filename)
            shutil.rmtree(temp_dir)

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
    await self_update()
    
    config = create_or_read_config()
    
    client = TelegramClient(SESSION_FILE, int(config['api_id']), config['api_hash'])
    await client.start(phone=config['phone_number'])
    
    print("\n🔑 Авторизация прошла успешно!")
    me = await client.get_me()
    print(f"👤 Имя: {me.first_name}")
    print(f"📱 Номер: {me.phone}")

    user_animations = {}
    user_states = {}

    @client.on(events.NewMessage(pattern='/a'))
    async def handle_animation_selection(event):
        user_id = event.sender_id
        response = "🎬 Доступные анимации:\n"
        for idx, anim in enumerate(animation_script.animations):
            response += f"{idx}. {anim['name']}\n"
        await event.respond(response + "\nВведите номер анимации:")
        user_states[user_id] = 'awaiting_animation_choice'

    @client.on(events.NewMessage(pattern='/p'))
    async def animate_text_handler(event):
        user_id = event.sender_id
        text = event.raw_text[3:].strip()
        
        if not text:
            await event.respond("❌ Укажите текст: /p Ваш текст")
            return
            
        anim_index = user_animations.get(user_id)
        if anim_index is None:
            await event.respond("⚠️ Сначала выберите анимацию через /a")
            return
            
        try:
            animation = animation_script.animations[anim_index]
            frames = animation['function'](text)
            
            for frame in frames:
                await event.respond(frame)
                await asyncio.sleep(0.3)
        except Exception as e:
            await event.respond(f"⚠️ Ошибка: {str(e)}")

    @client.on(events.NewMessage)
    async def message_handler(event):
        user_id = event.sender_id
        if user_states.get(user_id) == 'awaiting_animation_choice':
            try:
                choice = int(event.raw_text.strip())
                if 0 <= choice < len(animation_script.animations):
                    user_animations[user_id] = choice
                    selected_anim = animation_script.animations[choice]['name']
                    await event.respond(f"✅ Выбрано: {selected_anim}")
                    user_states.pop(user_id, None)
                else:
                    await event.respond("❌ Неверный номер. Попробуйте снова.")
            except ValueError:
                await event.respond("❌ Введите число.")

    asyncio.create_task(update_checker())
    print("\n🛠️ Бот готов к работе! Ожидание сообщений...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except SessionPasswordNeededError:
        print("\n🔐 Требуется двухфакторная аутентификация!")
        password = input("Введите пароль: ")
        with TelegramClient(SESSION_FILE, 
                          int(create_or_read_config()['api_id']), 
                          create_or_read_config()['api_hash']) as client:
            client.start(password=password)
        print("✅ Пароль успешно проверен! Перезапустите бота.")
    except KeyboardInterrupt:
        print("\n🛑 Работа бота завершена.")
    except Exception as e:
        print(f"⛔ Критическая ошибка: {str(e)}")
