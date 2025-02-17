import os
import asyncio
import sys
import json
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from animation_script import animations

# Конфигурация
CONFIG_FILE = "config.txt"
EMOJIS = {
    "success": "✅",
    "error": "❌",
    "menu": "📋",
    "info": "ℹ️",
    "bot": "🤖",
    "animation": "🎭"
}

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = {}
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
            
            API_ID = config.get("API_ID")
            API_HASH = config.get("API_HASH")
            PHONE_NUMBER = config.get("PHONE_NUMBER")
            SELECTED_ANIM = config.get("SELECTED_ANIM", "1")
            
            if not all([API_ID, API_HASH, PHONE_NUMBER]):
                raise ValueError("Не все параметры в конфиге!")
            
            return int(API_ID), API_HASH, PHONE_NUMBER, int(SELECTED_ANIM)
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка конфига: {e}")
        sys.exit(1)

def save_config(api_id, api_hash, phone, selected_anim):
    with open(CONFIG_FILE, "w") as f:
        f.write(
            f"API_ID={api_id}\n"
            f"API_HASH={api_hash}\n"
            f"PHONE_NUMBER={phone}\n"
            f"SELECTED_ANIM={selected_anim}"
        )

API_ID, API_HASH, PHONE_NUMBER, SELECTED_ANIM = load_config()
client = TelegramClient(f'session_{PHONE_NUMBER}', API_ID, API_HASH)
animation_selection_mode = False

# ========== КОМАНДЫ ==========
@client.on(events.NewMessage(pattern='/m'))
async def animation_menu(event):
    global animation_selection_mode
    try:
        menu_msg = await event.reply(f"{EMOJIS['menu']} Загружаю анимации...")
        menu_text = "\n".join([f"{num}) {name}" for num, (name, _) in animations.items()])
        selection_msg = await event.reply(menu_text)
        
        # Сохраняем ID сообщений для удаления
        client.message_ids_to_delete = [menu_msg.id, selection_msg.id]
        animation_selection_mode = True
        
    except Exception as e:
        await event.reply(f"{EMOJIS['error']} Ошибка: {str(e)}")

@client.on(events.NewMessage(pattern='/p'))
async def animate_handler(event):
    try:
        text = event.raw_text.split(maxsplit=1)[1]
        anim_name, anim_func = animations[SELECTED_ANIM]
        msg = await event.reply(f"{EMOJIS['animation']} Запускаю анимацию...")
        await anim_func(msg, text)
    except IndexError:
        await event.reply(f"{EMOJIS['error']} Формат: /p <текст>")
    except KeyError:
        await event.reply(f"{EMOJIS['error']} Анимация {SELECTED_ANIM} не найдена!")

@client.on(events.NewMessage)
async def handle_message(event):
    global SELECTED_ANIM, animation_selection_mode
    if animation_selection_mode and event.raw_text.isdigit():
        try:
            # Удаляем меню
            if hasattr(client, 'message_ids_to_delete'):
                await client.delete_messages(
                    await event.get_input_chat(),
                    client.message_ids_to_delete
                )
            
            # Обработка выбора
            num = int(event.raw_text)
            if num in animations:
                SELECTED_ANIM = num
                save_config(API_ID, API_HASH, PHONE_NUMBER, SELECTED_ANIM)
                confirm_msg = await event.reply(
                    f"{EMOJIS['success']} Выбрано: {animations[num][0]}"
                )
                await asyncio.sleep(2)
                await confirm_msg.delete()
                
        except Exception as e:
            await event.reply(f"{EMOJIS['error']} Ошибка: {str(e)}")
        finally:
            animation_selection_mode = False

# ========== СИСТЕМНЫЕ ФУНКЦИИ ==========
async def authorize():
    try:
        await client.start(
            phone=PHONE_NUMBER,
            code_callback=lambda: input(f"{EMOJIS['info']} Введите код из Telegram: ")
        )
        print(f"{EMOJIS['success']} Авторизация успешна!")
    except SessionPasswordNeededError:
        password = input(f"{EMOJIS['info']} Введите пароль 2FA: ")
        await client.sign_in(password=password)
        print(f"{EMOJIS['success']} 2FA пройдена!")
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка: {str(e)}")
        sys.exit(1)

async def main():
    try:
        await authorize()
        print(
            f"\n{EMOJIS['bot']} Бот активен!\n"
            f"{EMOJIS['info']} Команды:\n"
            f"/m - Выбор анимации\n"
            f"/p <текст> - Применить анимацию\n"
            f"{EMOJIS['info']} Закройте Termux для остановки."
        )
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print(f"\n{EMOJIS['info']} Завершение работы...")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except Exception as e:
        print(f"{EMOJIS['error']} Критическая ошибка: {str(e)}")
        sys.exit(1)
