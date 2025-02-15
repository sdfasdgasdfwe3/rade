import os
import json
import requests
import sys
import asyncio
from telethon import TelegramClient, events
import sqlite3

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
SCRIPT_VERSION = "0.2.41"

# Emoji
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

# Глобальные переменные
current_user_id = None

# region Основная логика
def load_config():
    """Загружает конфигурацию"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"{EMOJIS['error']} Ошибка конфига: {str(e)}")
            return {}
    return {}

def save_config(config):
    """Сохраняет конфигурацию"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка сохранения: {str(e)}")

config = load_config()
API_ID = config.get("API_ID")
API_HASH = config.get("API_HASH")
PHONE_NUMBER = config.get("PHONE_NUMBER")

if not all([API_ID, API_HASH, PHONE_NUMBER]):
    try:
        print(f"{EMOJIS['auth']} Требуется авторизация:")
        API_ID = int(input(f"{EMOJIS['auth']} API ID: "))
        API_HASH = input(f"{EMOJIS['auth']} API HASH: ").strip()
        PHONE_NUMBER = input(f"{EMOJIS['phone']} Номер (+79991234567): ").strip()
        config.update({
            "API_ID": API_ID,
            "API_HASH": API_HASH,
            "PHONE_NUMBER": PHONE_NUMBER
        })
        save_config(config)
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка: {str(e)}")
        sys.exit(1)

client = TelegramClient(
    f"session_{PHONE_NUMBER.replace('+', '')}",
    API_ID,
    API_HASH,
    connection_retries=0
)

async def safe_shutdown():
    """Безопасное завершение работы"""
    if client.is_connected():
        await client.disconnect()
    print(f"\n{EMOJIS['success']} Бот полностью остановлен")

async def close_client():
    """Завершает клиент Telegram"""
    await safe_shutdown()

async def authenticate():
    """Процесс авторизации"""
    try:
        await client.start(PHONE_NUMBER)
        if not await client.is_user_authorized():
            password = input(f"{EMOJIS['auth']} Пароль 2FA: ").strip()
            await client.sign_in(password=password)
        print(f"{EMOJIS['success']} Авторизация успешна!")
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка авторизации: {str(e)}")
        sys.exit(1)

async def update_bot():
    """Обновление бота с GitHub"""
    try:
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            with open("bot.py", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"{EMOJIS['update']} Бот успешно обновлен!")
            # Перезапуск бота
            os.execv(sys.executable, [sys.executable, "bot.py"])
        else:
            print(f"{EMOJIS['error']} Ошибка при обновлении: {response.status_code}")
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка обновления: {str(e)}")

@client.on(events.NewMessage(pattern='/p'))
async def animate_handler(event):
    """Обработчик команды /p"""
    command_text = event.raw_text
    parts = command_text.split(maxsplit=1)
    if len(parts) < 2:
        await event.reply("Использование: /p текст")
        return
    text_to_animate = parts[1]
    if selected_animation in animations:
        anim_func = animations[selected_animation][1]
        try:
            await anim_func(event, text_to_animate)
        except Exception as e:
            print(f"{EMOJIS['error']} Ошибка анимации: {str(e)}")
    else:
        await event.reply("Выбрана недопустимая анимация.")

@client.on(events.NewMessage(pattern='/m'))
async def animation_menu(event):
    """Обработчик команды /m"""
    global animation_selection_mode, current_user_id
    if not event.out:
        return
    current_user_id = event.sender_id
    animation_selection_mode = True
    menu_text = "Выберите анимацию:\n"
    for num, (name, _) in sorted(animations.items()):
        menu_text += f"{num}) {name}\n"
    menu_text += "\nВведите номер желаемой анимации."
    await event.reply(menu_text)

@client.on(events.NewMessage)
async def animation_selection_handler(event):
    """Обработчик выбора анимации"""
    global animation_selection_mode, selected_animation, config
    if animation_selection_mode and event.out:
        text = event.raw_text.strip()
        if text.isdigit():
            number = int(text)
            if number in animations:
                selected_animation = number
                config["selected_animation"] = selected_animation
                save_config(config)
                await event.reply(f"{EMOJIS['success']} Вы выбрали анимацию: {animations[selected_animation][0]}")
                messages = await client.get_messages(event.chat_id, limit=10)
                deleted_count = 0
                for msg in messages:
                    if msg.out:
                        try:
                            await msg.delete()
                            deleted_count += 1
                        except Exception as e:
                            print(f"{EMOJIS['error']} Ошибка удаления: {str(e)}")
                        if deleted_count >= 4:
                            break
            else:
                await event.reply(f"{EMOJIS['error']} Неверный номер анимации.")
            animation_selection_mode = False

def main():
    """Основная функция"""
    try:
        client.loop.run_until_complete(authenticate())
        print(f"{EMOJIS['bot']} Бот запущен (v{SCRIPT_VERSION})")
        client.run_until_disconnected()
    except Exception as e:
        print(f"{EMOJIS['error']} Критическая ошибка: {str(e)}")
    finally:
        client.loop.run_until_complete(safe_shutdown())

if __name__ == "__main__":
    main()
# endregion
