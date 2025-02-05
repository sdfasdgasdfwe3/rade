import os
import json
import requests
from telethon import TelegramClient, events
import subprocess
import sys
import asyncio
import random
import signal

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
SCRIPT_VERSION = "0.0.9"

# Настройки анимации
typing_speed = 1.5
pixel_typing_speed = 0.10
cursor_symbol = "▮"
selected_animation = 1

animations = {
    1: "Стандартная анимация",
    2: "Пиксельное разрушение",
}

# Цветовая палитра
COLORS = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
    "BOLD": "\033[1m",
    "LINE": "\033[4m",
}

def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"""{COLORS['CYAN']}
██████╗░░█████╗░██████╗░███████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝
██████╔╝███████║██║░░██║█████╗░░
██╔══██╗██╔══██║██║░░██║██╔══╝░░
██║░░██║██║░░██║██████╔╝███████╗
╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░╚══════╝
{COLORS['GREEN']}Telegram Text Animator Bot {SCRIPT_VERSION}
{COLORS['YELLOW']}github.com/sdfasdgasdfwe3/rade
{COLORS['ENDC']}""")

def print_status(message, color="GREEN"):
    print(f"{COLORS[color]}[•] {message}{COLORS['ENDC']}")

def signal_handler(sig, frame):
    print(f"\n{COLORS['RED']}[!] Бот остановлен{COLORS['ENDC']}")
    sys.exit(0)

def discard_local_changes():
    try:
        subprocess.run(["git", "checkout", "--", "bot.py"], check=True)
    except Exception:
        pass

def check_for_updates():
    try:
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            remote_script = response.text
            with open(__file__, 'r', encoding='utf-8') as f:
                current_script = f.read()
            
            remote_version = None
            for line in remote_script.splitlines():
                if "SCRIPT_VERSION" in line:
                    remote_version = line.split('=')[1].strip().strip('"')
                    break

            if remote_version and SCRIPT_VERSION != remote_version:
                print_status(f"Доступно обновление {remote_version}", "YELLOW")
                with open(__file__, 'w', encoding='utf-8') as f:
                    f.write(remote_script)
                print_status("Скрипт обновлен! Перезапустите бота", "GREEN")
                exit()
    except Exception as e:
        print_status(f"Ошибка проверки обновлений: {e}", "RED")

def load_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print_status(f"Ошибка чтения конфига: {e}", "RED")
    return config

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f)
    except Exception as e:
        print_status(f"Ошибка сохранения конфига: {e}", "RED")

async def animate_text(event, text):
    message = await event.edit(f"{cursor_symbol}")
    displayed = ""
    for char in text:
        displayed += char
        try:
            await message.edit(f"{displayed}{cursor_symbol}")
        except Exception:
            pass
        await asyncio.sleep(typing_speed)
    await message.edit(displayed)

async def pixel_destruction(event, text):
    lines = 4
    chunks = [text[i:i+len(text)//lines] for i in range(0, len(text), len(text)//lines)]
    prev_text = ""
    
    # Фаза пикселизации
    for _ in range(3):
        pixelated = []
        for chunk in chunks:
            new_chunk = [random.choice([".", "*", "○", "⊙", "%"]) if random.random() < 0.1 else " " for _ in chunk]
            pixelated.append("".join(new_chunk))
        current_text = "\n".join(pixelated)
        if current_text != prev_text:
            try:
                await event.edit(current_text)
                prev_text = current_text
            except Exception:
                pass
        await asyncio.sleep(pixel_typing_speed)
    
    # Фаза разрушения
    for _ in range(3):
        destroyed = ["".join([random.choice([".", "*", " "]) for _ in chunk]) for chunk in chunks]
        current_text = "\n".join(destroyed)
        if current_text != prev_text:
            try:
                await event.edit(current_text)
                prev_text = current_text
            except Exception:
                pass
        await asyncio.sleep(pixel_typing_speed)
    
    await event.edit(text)

@client.on(events.NewMessage(pattern='/p'))
async def animation_handler(event):
    if event.out:
        args = event.text.split(maxsplit=1)
        if len(args) > 1:
            try:
                if selected_animation == 1:
                    await animate_text(event, args[1])
                elif selected_animation == 2:
                    await pixel_destruction(event, args[1])
            except Exception as e:
                print_status(f"Ошибка анимации: {e}", "RED")
        else:
            await event.reply(f"{COLORS['YELLOW']}Использование: /p <текст>{COLORS['ENDC']}")

@client.on(events.NewMessage(pattern='/animlist'))
async def show_animations(event):
    if event.out:
        anim_list = "\n".join([f"{COLORS['CYAN']}{k}) {v}{COLORS['ENDC']}" for k, v in animations.items()])
        await event.reply(f"{COLORS['GREEN']}Доступные анимации:\n{anim_list}")

@client.on(events.NewMessage(pattern=r'^\d+$'))
async def select_animation(event):
    if event.out:
        global selected_animation
        try:
            num = int(event.text)
            if num in animations:
                selected_animation = num
                await event.delete()
                messages = await client.get_messages(event.chat_id, limit=2)
                for msg in messages:
                    if msg.out and msg.id != event.id:
                        await msg.delete()
                await event.respond(f"{COLORS['GREEN']}Анимация {num} выбрана!{COLORS['ENDC']}")
        except Exception as e:
            print_status(f"Ошибка выбора анимации: {e}", "RED")

async def main():
    print_banner()
    check_for_updates()
    
    config = load_config()
    if not all(config.get(key) for key in ["API_ID", "API_HASH", "PHONE_NUMBER"]):
        print_status("Введите данные для авторизации:", "BLUE")
        config["API_ID"] = int(input(f"{COLORS['CYAN']}[?] API ID: {COLORS['ENDC']}"))
        config["API_HASH"] = input(f"{COLORS['CYAN']}[?] API Hash: {COLORS['ENDC']}").strip()
        config["PHONE_NUMBER"] = input(f"{COLORS['CYAN']}[?] Номер телефона: {COLORS['ENDC']}").strip()
        save_config(config)

    client = TelegramClient(
        session=f"session_{config['PHONE_NUMBER']}",
        api_id=config["API_ID"],
        api_hash=config["API_HASH"]
    )

    try:
        await client.start(config["PHONE_NUMBER"])
        me = await client.get_me()
        print(f"""{COLORS['GREEN']}
╔══════════════════════════════════╗
║          АВТОРИЗАЦИЯ OK          ║
╠══════════════════════════════════╣
║ ID: {me.id}
║ Имя: {me.first_name}
║ Фамилия: {me.last_name or '—'}
║ Username: @{me.username or '—'}
╚══════════════════════════════════╝{COLORS['ENDC']}""")
        print_status("Бот готов к работе! Ожидание команд...", "GREEN")
        await client.run_until_disconnected()
    except Exception as e:
        print_status(f"Критическая ошибка: {e}", "RED")
        sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.run(main())
