import os
import asyncio
import sys
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from animation_script import animations

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
            SELECTED_ANIM = config.get("SELECTED_ANIM", "1")  # Новое поле
            
            if not all([API_ID, API_HASH, PHONE_NUMBER]):
                raise ValueError("🔍 Проверьте config.txt!")
            
            return int(API_ID), API_HASH, PHONE_NUMBER, int(SELECTED_ANIM)
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        sys.exit(1)

def save_config(api_id, api_hash, phone, selected_anim):
    with open("config.txt", "w") as f:
        f.write(
            f"API_ID={api_id}\n"
            f"API_HASH={api_hash}\n"
            f"PHONE_NUMBER={phone}\n"
            f"SELECTED_ANIM={selected_anim}"  # Сохраняем выбор анимации
        )

API_ID, API_HASH, PHONE_NUMBER, SELECTED_ANIM = load_config()
client = TelegramClient(f'session_{PHONE_NUMBER}', API_ID, API_HASH)
animation_selection_mode = False

# ========== КОМАНДЫ ==========
@client.on(events.NewMessage(pattern='/m'))
async def animation_menu(event):
    global animation_selection_mode
    menu = "🎭 Выберите анимацию:\n" + "\n".join(
        [f"{num}) {name}" for num, (name, _) in animations.items()]
    )
    await event.reply(menu)
    animation_selection_mode = True

@client.on(events.NewMessage(pattern='/p'))
async def animate_handler(event):
    try:
        text = event.raw_text.split(maxsplit=1)[1]
        anim_func = animations[SELECTED_ANIM][1]
        await anim_func(event, text)
    except IndexError:
        await event.reply("❌ Используйте: /p <текст>")
    except KeyError:
        await event.reply("❌ Анимация не найдена!")

@client.on(events.NewMessage)
async def handle_message(event):
    global SELECTED_ANIM, animation_selection_mode
    if animation_selection_mode and event.raw_text.isdigit():
        num = int(event.raw_text)
        if num in animations:
            SELECTED_ANIM = num
            save_config(API_ID, API_HASH, PHONE_NUMBER, SELECTED_ANIM)
            await event.reply(f"✅ Выбрана анимация: {animations[num][0]}")
        animation_selection_mode = False

# ========== ОСНОВНАЯ ЛОГИКА ==========
async def authorize():
    try:
        await client.start(
            phone=PHONE_NUMBER,
            code_callback=lambda: input("🔢 Введите код из Telegram: ")
        )
        print("✅ Успешная авторизация!")
    except SessionPasswordNeededError:
        password = input("🔐 Введите пароль 2FA: ")
        await client.sign_in(password=password)
        print("🎉 2FA пройдена!")
    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        sys.exit(1)

async def main():
    try:
        await authorize()
        print("\n🤖 Бот активен. Команды:\n"
              "/m - меню анимаций\n"
              "/p <текст> - применить анимацию\n"
              "Закройте Termux для остановки.")
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
