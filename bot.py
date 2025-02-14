import os
import json
import requests
import sys
import subprocess
import asyncio
import signal
from telethon import TelegramClient, events
import psutil
from animation_script import animations
import animation_script

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
ANIMATION_SCRIPT_GITHUB_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/animation_script.py"
SCRIPT_VERSION = "0.2.39"

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

def is_bot_running():
    current_pid = os.getpid()
    for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(process.info['cmdline'])
            if 'python' in process.info['name'].lower() and 'bot.py' in cmdline:
                if process.info['pid'] != current_pid:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError, TypeError):
            continue
    return False

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if "selected_animation" not in config:
                config["selected_animation"] = 1
            return config
        except Exception as e:
            print(f"{EMOJIS['error']} Ошибка загрузки конфига:", e)
            return {}
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка сохранения конфига:", e)

config = load_config()
API_ID = config.get("API_ID")
API_HASH = config.get("API_HASH")
PHONE_NUMBER = config.get("PHONE_NUMBER")
selected_animation = config.get("selected_animation", 1)

if not all([API_ID, API_HASH, PHONE_NUMBER]):
    try:
        print(f"{EMOJIS['auth']} Необходима авторизация. Введите данные от Telegram:")
        API_ID = int(input(f"{EMOJIS['auth']} Введите API ID: "))
        API_HASH = input(f"{EMOJIS['auth']} Введите API HASH: ").strip()
        PHONE_NUMBER = input(f"{EMOJIS['phone']} Введите номер телефона (формат +79991234567): ").strip()
        config = {
            "API_ID": API_ID,
            "API_HASH": API_HASH,
            "PHONE_NUMBER": PHONE_NUMBER,
            "selected_animation": selected_animation
        }
        save_config(config)
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка:", e)
        sys.exit(1)

if is_bot_running():
    print("⚠️ Бот уже запущен! Второй экземпляр запускать нельзя.")
    sys.exit(1)

client = TelegramClient(f"session_{PHONE_NUMBER.replace('+', '')}", API_ID, API_HASH)

def discard_local_changes():
    try:
        subprocess.run(["git", "checkout", "--", os.path.basename(__file__)], check=True)
    except Exception:
        pass

def check_for_updates():
    try:
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            remote_script = response.text
            remote_version = None
            for line in remote_script.splitlines():
                if "SCRIPT_VERSION" in line:
                    try:
                        remote_version = line.split('=')[1].strip().strip('"')
                    except Exception:
                        pass
                    break
            if remote_version and SCRIPT_VERSION != remote_version:
                print(f"{EMOJIS['update']} Обнаружена новая версия {remote_version} (текущая {SCRIPT_VERSION}). Обновление...")
                discard_local_changes()
                with open(os.path.abspath(__file__), 'w', encoding='utf-8') as f:
                    f.write(remote_script)
                print(f"{EMOJIS['success']} Скрипт обновлён. Перезапустите программу.")
                exit()
        else:
            print(f"{EMOJIS['error']} Ошибка проверки обновлений: статус {response.status_code}")
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка проверки обновлений:", e)

def check_for_animation_script_updates():
    try:
        response = requests.get(ANIMATION_SCRIPT_GITHUB_URL)
        if response.status_code == 200:
            remote_file = response.text
            remote_version = None
            for line in remote_file.splitlines():
                if "ANIMATION_SCRIPT_VERSION" in line:
                    try:
                        remote_version = line.split('=')[1].strip().strip('"')
                    except Exception:
                        pass
                    break
            if remote_version and remote_version != animation_script.ANIMATION_SCRIPT_VERSION:
                print(f"{EMOJIS['update']} Обнаружена новая версия анимационного скрипта {remote_version} (текущая {animation_script.ANIMATION_SCRIPT_VERSION}). Обновление...")
                with open("animation_script.py", "w", encoding="utf-8") as f:
                    f.write(remote_file)
                print(f"{EMOJIS['success']} Файл animation_script.py обновлён. Перезапустите программу.")
                exit()
            else:
                print(f"{EMOJIS['success']} Анимационный скрипт актуален.")
        else:
            print(f"{EMOJIS['error']} Ошибка проверки обновлений анимационного скрипта: статус {response.status_code}")
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка проверки обновлений анимационного скрипта:", e)

animation_selection_mode = False
current_user_id = None

@client.on(events.NewMessage(pattern='/p'))
async def animate_handler(event):
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
            print(f"{EMOJIS['error']} Ошибка анимации:", e)
    else:
        await event.reply("Выбрана недопустимая анимация.")

@client.on(events.NewMessage(pattern='/m'))
async def animation_menu(event):
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
                            print(f"{EMOJIS['error']} Ошибка удаления:", e)
                        if deleted_count >= 4:
                            break
            else:
                await event.reply(f"{EMOJIS['error']} Неверный номер анимации.")
            animation_selection_mode = False

async def close_client():
    if client.is_connected():
        await client.disconnect()
    print(f"\n{EMOJIS['exit']} Бот успешно остановлен.")

def signal_handler(sig, frame):
    print(f"\n{EMOJIS['exit']} Получен сигнал завершения. Останавливаем бота...")
    client.loop.run_until_complete(close_client())
    sys.exit(0)

def main():
    check_for_updates()
    check_for_animation_script_updates()
    try:
        client.start(PHONE_NUMBER)
        print(f"{EMOJIS['bot']} Скрипт запущен. Версия: {SCRIPT_VERSION}")
        me = client.loop.run_until_complete(client.get_me())
        username = me.username if me.username else (me.first_name if me.first_name else "Unknown")
        print(f"{EMOJIS['bot']} Вы авторизованы как: {username}")
        print("Телеграмм канал: t.me/kwotko")
        print("Для остановки нажмите Ctrl+C")
        signal.signal(signal.SIGINT, signal_handler)
        client.run_until_disconnected()
    except Exception as e:
        print(f"{EMOJIS['error']} Критическая ошибка:", e)
    finally:
        client.loop.run_until_complete(close_client())

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
