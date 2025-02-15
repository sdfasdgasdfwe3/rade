import os
import json
import sys
import aiohttp
import asyncio
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

try:
    import animation_script
    animations = animation_script.ANIMATIONS
except (ImportError, AttributeError) as e:
    print("❌ Ошибка загрузки анимационного скрипта:", e)
    animations = {}

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/.../bot.py"
ANIMATION_SCRIPT_GITHUB_URL = "https://raw.githubusercontent.com/.../animation_script.py"
SCRIPT_VERSION = "0.2.39"

EMOJIS = {
    "auth": "🔑",
    "phone": "📱",
    "update": "🔄",
    "version": "🏷️",
    "success": "✅",
    "error": "❌",
    "info": "ℹ️",
    "exit": "👋",
    "menu": "📋",
    "bot": "🤖"
}

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            config.setdefault("selected_animation", 1)
            return config
    except (FileNotFoundError, json.JSONDecodeError):
        return {"selected_animation": 1}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f)

async def check_for_updates():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GITHUB_RAW_URL) as response:
                if response.status == 200:
                    remote_script = await response.text()
                    if 'SCRIPT_VERSION' in remote_script:
                        remote_version = remote_script.split('SCRIPT_VERSION = "')[1].split('"')[0]
                        if remote_version != SCRIPT_VERSION:
                            print(f"{EMOJIS['update']} Найдено обновление {remote_version}")
                            with open(__file__, 'w', encoding='utf-8') as f:
                                f.write(remote_script)
                            print(f"{EMOJIS['success']} Перезапустите скрипт")
                            sys.exit(0)
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка обновления:", e)

async def check_animation_script_updates():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ANIMATION_SCRIPT_GITHUB_URL) as response:
                if response.status == 200:
                    remote_script = await response.text()
                    if 'ANIMATION_SCRIPT_VERSION' in remote_script:
                        remote_version = remote_script.split('ANIMATION_SCRIPT_VERSION = "')[1].split('"')[0]
                        if hasattr(animation_script, 'ANIMATION_SCRIPT_VERSION'):
                            if remote_version != animation_script.ANIMATION_SCRIPT_VERSION:
                                print(f"{EMOJIS['update']} Обновление анимаций до {remote_version}")
                                with open('animation_script.py', 'w', encoding='utf-8') as f:
                                    f.write(remote_script)
                                sys.exit(0)
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка обновления анимаций:", e)

async def main():
    config = load_config()
    
    if not all(config.get(k) for k in ["API_ID", "API_HASH", "PHONE_NUMBER"]):
        print(f"{EMOJIS['auth']} Требуется настройка:")
        config["API_ID"] = int(input("API ID: "))
        config["API_HASH"] = input("API HASH: ").strip()
        config["PHONE_NUMBER"] = input("Номер телефона (+7999...): ").strip()
        save_config(config)

    client = TelegramClient(
        session=f"session_{config['PHONE_NUMBER'].replace('+', '')}",
        api_id=config["API_ID"],
        api_hash=config["API_HASH"]
    )

    try:
        await client.start(
            phone=config["PHONE_NUMBER"],
            password=lambda: input("Пароль двухфакторной аутентификации: ")
        )
    except SessionPasswordNeededError:
        password = input("Введите пароль двухфакторной аутентификации: ")
        await client.start(phone=config["PHONE_NUMBER"], password=password)
    
    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"{EMOJIS['success']} Авторизован как @{me.username}")
    else:
        print(f"{EMOJIS['error']} Ошибка авторизации")
        return

    @client.on(events.NewMessage(pattern='/p'))
    async def animate_handler(event):
        text = event.raw_text.split(maxsplit=1)
        if len(text) < 2:
            await event.reply("Формат: /p текст")
            return
        
        anim_id = config["selected_animation"]
        if anim_id not in animations:
            await event.reply("Анимация не найдена")
            return
        
        try:
            await animations[anim_id][1](event, text[1])
        except Exception as e:
            print(f"{EMOJIS['error']} Ошибка анимации:", e)
            await event.reply("Ошибка выполнения анимации")

    @client.on(events.NewMessage(pattern='/m'))
    async def animation_menu(event):
        menu = "Выберите анимацию:\n" + "\n".join(
            f"{num}) {name}" for num, (name, _) in sorted(animations.items())
        )
        sent = await event.reply(menu)
        
        async with client.conversation(event.chat_id, timeout=60) as conv:
            try:
                response = await conv.get_response()
                if response.raw_text.isdigit():
                    num = int(response.raw_text)
                    if num in animations:
                        config["selected_animation"] = num
                        save_config(config)
                        await conv.send_message(f"{EMOJIS['success']} Выбрана анимация: {animations[num][0]}")
                    else:
                        await conv.send_message(f"{EMOJIS['error']} Неверный номер")
            except asyncio.TimeoutError:
                await event.reply(f"{EMOJIS['error']} Время вышло")

    print(f"{EMOJIS['bot']} Бот запущен (v{SCRIPT_VERSION})")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
