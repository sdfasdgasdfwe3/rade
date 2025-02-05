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

# Глобальные переменные для управления анимацией
is_typing_enabled = True
typing_speed = 1.5
pixel_typing_speed = 0.10
cursor_symbol = "▮"
selected_animation = 1

# Список анимаций
animations = {
    1: "Стандартная анимация",
    2: "Пиксельное разрушение",
}

def signal_handler(sig, frame):
    print('\nБот остановлен.')
    sys.exit(0)

def discard_local_changes():
    try:
        subprocess.run(["git", "checkout", "--", "bot.py"], check=True)
    except subprocess.CalledProcessError:
        pass

def check_for_updates():
    try:
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            remote_script = response.text
            current_file = os.path.abspath(__file__)

            with open(current_file, 'r', encoding='utf-8') as f:
                current_script = f.read()

            remote_version = None
            for line in remote_script.splitlines():
                if "SCRIPT_VERSION" in line:
                    remote_version = line.split('=')[1].strip().strip('"')
                    break

            if remote_version and SCRIPT_VERSION != remote_version:
                print(f"Доступна новая версия {remote_version} (текущая {SCRIPT_VERSION})")
                with open(current_file, 'w', encoding='utf-8') as f:
                    f.write(remote_script)
                print("Скрипт обновлен. Перезапустите программу.")
                exit()
            else:
                print("У вас актуальная версия скрипта.")
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {e}")

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        API_ID = config.get("API_ID")
        API_HASH = config.get("API_HASH")
        PHONE_NUMBER = config.get("PHONE_NUMBER")
    except (json.JSONDecodeError, KeyError):
        API_ID = API_HASH = PHONE_NUMBER = None
else:
    API_ID = API_HASH = PHONE_NUMBER = None

if not all([API_ID, API_HASH, PHONE_NUMBER]):
    try:
        print("Введите данные для авторизации:")
        API_ID = int(input("API ID: "))
        API_HASH = input("API Hash: ").strip()
        PHONE_NUMBER = input("Номер телефона: ").strip()

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "API_ID": API_ID,
                "API_HASH": API_HASH,
                "PHONE_NUMBER": PHONE_NUMBER
            }, f)
    except Exception as e:
        print(f"Ошибка: {e}")
        exit(1)

client = TelegramClient(f"session_{PHONE_NUMBER.replace('+', '')}", API_ID, API_HASH)

async def animate_text(client, event, text):
    displayed_text = ""
    msg = await event.edit(displayed_text + cursor_symbol)
    for char in text:
        displayed_text += char
        try:
            await msg.edit(displayed_text + cursor_symbol)
        except Exception:
            pass
        await asyncio.sleep(typing_speed)
    await msg.edit(displayed_text)

async def pixel_destruction(client, event, text):
    lines_count = 4
    chunk_size = len(text) // lines_count
    text_lines = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    previous_text = ""

    # Фаза 1: Пикселизация
    pixelated_text = [list(" " * len(line)) for line in text_lines]
    for _ in range(3):
        for i in range(len(pixelated_text)):
            for j in range(len(pixelated_text[i])):
                if random.random() < 0.1:
                    pixelated_text[i][j] = random.choice([".", "*", "○", "⊙", "%"])
        displayed_text = "\n".join(["".join(line) for line in pixelated_text])
        if displayed_text != previous_text:
            try:
                await event.edit(displayed_text)
                previous_text = displayed_text
            except Exception:
                pass
        await asyncio.sleep(pixel_typing_speed)

    # Фаза 2: Разрушение
    for _ in range(3):
        displayed_text = "\n".join([
            "".join([random.choice([".", "*", " ", "○", "⊙"]) for _ in line])
            for line in text_lines
        ])
        if displayed_text != previous_text:
            try:
                await event.edit(displayed_text)
                previous_text = displayed_text
            except Exception:
                pass
        await asyncio.sleep(pixel_typing_speed)
    
    await event.edit(text)

@client.on(events.NewMessage(pattern='/p'))
async def animate_handler(event):
    if event.out:
        command_text = event.raw_text
        if len(command_text.split()) > 1:
            text_to_animate = command_text.partition(' ')[2]
            try:
                if selected_animation == 1:
                    await animate_text(client, event, text_to_animate)
                elif selected_animation == 2:
                    await pixel_destruction(client, event, text_to_animate)
            except Exception as e:
                print(f"Ошибка анимации: {e}")
        else:
            await event.reply("Используйте: /p ваш текст")

@client.on(events.NewMessage(pattern='/1'))
async def list_animations(event):
    if event.out:
        animation_list = "Доступные анимации:\n" + "\n".join([f"{i}) {name}" for i, name in animations.items()])
        await event.reply(animation_list)

@client.on(events.NewMessage(pattern='^\\d+$'))
async def change_animation(event):
    if event.out:
        global selected_animation
        try:
            animation_number = int(event.raw_text)
            if animation_number in animations:
                selected_animation = animation_number
                messages = await client.get_messages(event.chat_id, limit=3)
                for msg in messages:
                    if msg.out and msg.id != event.message.id:
                        await msg.delete()
                await event.delete()
        except ValueError:
            pass

async def main():
    try:
        await client.start(PHONE_NUMBER)
        print(f"Авторизован как {PHONE_NUMBER}")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    check_for_updates()
    asyncio.run(main())
