import os
import asyncio
import json
import sqlite3
from telethon import TelegramClient, events, errors
from animation_script import animations

os.system('git pull')

CONFIG_FILE = "config.json"
SESSION_NAME = "session"

selected_animations = {}
awaiting_animation_choice = set()

def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    print("Файл config.json не найден. Создаю новый...")
    config = {
        "api_id": int(input('Введите api_id: ')),
        "api_hash": input('Введите api_hash: '),
        "phone_number": input('Введите номер телефона: ')
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    return config

async def safe_connect(client):
    for attempt in range(1, 6):
        try:
            await client.connect()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                await asyncio.sleep(2)
            else:
                raise
    raise Exception("Не удалось подключиться.")

def create_client(config):
    return TelegramClient(SESSION_NAME, config["api_id"], config["api_hash"])

async def authorize(client, config):
    await safe_connect(client)
    if await client.is_user_authorized():
        return True
    try:
        await client.send_code_request(config["phone_number"])
        code = input('Введите код из Telegram: ')
        await client.sign_in(config["phone_number"], code)
    except errors.SessionPasswordNeededError:
        password = input('Введите пароль 2FA: ')
        await client.sign_in(password=password)
    return await client.is_user_authorized()

@events.register(events.NewMessage(pattern=r'^/m\b'))
async def handle_m_command(event):
    """Вывод списка анимаций и ожидание выбора."""
    text = "Выберите анимацию, отправив её номер:\n"
    for num, (name, _) in animations.items():
        text += f"{num}. {name}\n"
    await event.respond(text)
    awaiting_animation_choice.add(event.chat_id)  # Ожидаем номер

@events.register(events.NewMessage)
async def handle_text(event):
    """Обработка выбора анимации или анимации текста."""
    chat_id = event.chat_id

    if chat_id in awaiting_animation_choice:
        try:
            selection = int(event.text.strip())
            if selection in animations:
                selected_animations[chat_id] = selection
                confirmation = await event.respond(f"Выбрана анимация: {animations[selection][0]}")
                awaiting_animation_choice.remove(chat_id)

                me = await event.client.get_me()
                bot_messages = await event.client.get_messages(chat_id, limit=4, from_user=me.id)
                await event.client.delete_messages(chat_id, [msg.id for msg in bot_messages])
            else:
                await event.respond("❌ Неверный номер анимации.")
        except ValueError:
            await event.respond("❌ Введите номер анимации цифрой.")

    elif event.text.startswith("/p "):
        text = event.text[3:].strip()
        if not text:
            await event.respond("❌ Укажите текст после /p.")
        else:
            anim_number = selected_animations.get(chat_id, 1)
            animation_func = animations[anim_number][1]
            await animation_func(event, text)

async def main():
    config = load_or_create_config()
    client = create_client(config)
    if await authorize(client, config):
        client.add_event_handler(handle_m_command)
        client.add_event_handler(handle_text)
        print("Бот работает...")
        await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
