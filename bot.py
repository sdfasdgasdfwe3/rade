import os
import json
import requests
import sys
import subprocess
import asyncio
import signal
from telethon import TelegramClient, events
from animation_script import animations

CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
SCRIPT_VERSION = "0.1.0"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            if "selected_animation" not in config:
                config["selected_animation"] = 1
            return config
        except Exception:
            return {}
    return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print("Ошибка сохранения конфигурации:", e)

config = load_config()
API_ID = config.get("API_ID")
API_HASH = config.get("API_HASH")
PHONE_NUMBER = config.get("PHONE_NUMBER")
selected_animation = config.get("selected_animation", 1)

if not all([API_ID, API_HASH, PHONE_NUMBER]):
    try:
        API_ID = int(input("Введите API ID: "))
        API_HASH = input("Введите API HASH: ").strip()
        PHONE_NUMBER = input("Введите номер телефона: ").strip()
        config = {"API_ID": API_ID, "API_HASH": API_HASH, "PHONE_NUMBER": PHONE_NUMBER, "selected_animation": selected_animation}
        save_config(config)
    except Exception as e:
        print("Error:", e)
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
                discard_local_changes()
                with open(os.path.abspath(__file__), 'w') as f:
                    f.write(remote_script)
                print("Скрипт обновлен. Пожалуйста, перезапустите скрипт.")
                exit()
        else:
            print("Ошибка проверки обновлений:", response.status_code)
    except Exception as e:
        print("Ошибка проверки обновлений:", e)

animation_selection_mode = False

@client.on(events.NewMessage(pattern='/p'))
async def animate_handler(event):
    command_text = event.raw_text
    parts = command_text.split(maxsplit=1)
    if len(parts) < 2:
        await event.reply("Usage: /p text")
        return
    text_to_animate = parts[1]
    if selected_animation in animations:
        anim_func = animations[selected_animation][1]
        try:
            await anim_func(event, text_to_animate)
        except Exception as e:
            print("Ошибка анимации:", e)
    else:
        await event.reply("Invalid animation selected.")

@client.on(events.NewMessage(pattern='/m'))
async def animation_menu(event):
    global animation_selection_mode
    animation_selection_mode = True
    menu_text = "Select animation:\n"
    for num, (name, _) in sorted(animations.items()):
        menu_text += f"{num}) {name}\n"
    menu_text += "Enter the number of the desired animation."
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
                await event.reply(f"Animation {number} selected.")
            else:
                await event.reply("Invalid animation number.")
            animation_selection_mode = False

def main():
    check_for_updates()
    client.start(PHONE_NUMBER)
    print("Бот запущен. Нажмите Ctrl+C, чтобы остановить.")
    client.run_until_disconnected()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    main()
