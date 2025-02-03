import os
import re
import sys
import asyncio
import aiohttp
import subprocess
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from configparser import ConfigParser

VERSION = "1.1"
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

        with open(__file__, 'w', encoding='utf-8') as f:
            f.write(new_code)
            
        print("🔄 Бот успешно обновлен! Перезапускаем...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        print(f"⛔ Ошибка при обновлении: {str(e)}")

async def update_checker():
    while True:
        await asyncio.sleep(3600)  # Проверка каждые 60 минут
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

# ... (весь предыдущий код до функции main остается без изменений)

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
    
    print("\n🔑 Авторизация прошла успешно!")
    me = await client.get_me()
    print(f"👤 Имя: {me.first_name}")
    print(f"📱 Номер: {me.phone}")
    
    # Запуск фоновой задачи проверки обновлений
    asyncio.create_task(update_checker())
    
    print("\n🛠️ Доступные команды:")
    print("/update - Принудительное обновление")
    print("/exit - Выход из бота")
    print("/a - Выбор анимации")
    print("/p <текст> - Анимировать текст\n")
    
    # Добавляем только новые переменные
    user_animations = {}  # {user_id: индекс анимации}
    user_states = {}      # {user_id: текущее состояние}
    
    # Обработчики событий Telethon
    @client.on(events.NewMessage(pattern='/a'))
    async def animation_list_handler(event):
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

    # Оригинальный цикл ввода команд для управления ботом
    while True:
        cmd = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
        if cmd.strip() == '/update':
            await self_update()
        elif cmd.strip() == '/exit':
            sys.exit(0)

if __name__ == '__main__':
