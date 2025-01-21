import os
import json
import requests
from telethon import TelegramClient, events
import subprocess
import sys
import asyncio
import set
import random

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
SCRIPT_VERSION = "0.0.9"

# Глобальные переменные для управления анимацией
is_typing_enabled = True  # Флаг, включающий анимацию
typing_speed = 1.5  # Уменьшенная скорость печатания (в два раза быстрее)
pixel_typing_speed = 0.10  # Уменьшенная скорость для пиксельного разрушения (в два раза быстрее)
cursor_symbol = "▮"  # Символ курсора для анимации
selected_animation = 1  # Выбранная анимация по умолчанию

# Список анимаций
animations = {
    1: "Стандартная анимация",
    2: "Пиксельное разрушение",
    3: "Падение букв сверху вниз",  # Новая анимация
}

# Функция для отмены локальных изменений в git
def discard_local_changes():
    try:
        subprocess.run(["git", "checkout", "--", "bot.py"], check=True)
    except subprocess.CalledProcessError as e:
        pass

# Функция для проверки обновлений скрипта на GitHub
def check_for_updates():
    try:
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            remote_script = response.text
            current_file = os.path.abspath(__file__)

            with open(current_file, 'r', encoding='utf-8') as f:
                current_script = f.read()

            if SCRIPT_VERSION in remote_script and SCRIPT_VERSION in current_script:
                remote_version_line = [
                    line for line in remote_script.splitlines() if SCRIPT_VERSION in line
                ]
                if remote_version_line:
                    remote_version = remote_version_line[0].split('=')[1].strip().strip('"')
                    if SCRIPT_VERSION != remote_version:
                        print(f"Доступна новая версия скрипта {remote_version} (текущая {SCRIPT_VERSION})")
                        with open(current_file, 'w', encoding='utf-8') as f:
                            f.write(remote_script)
                        print("Скрипт обновлен. Перезапустите программу.")
                        exit()
                    else:
                        print("У вас уже установлена последняя версия скрипта.")
                else:
                    print("Не удалось найти информацию о версии в загруженном скрипте.")
            else:
                print("Не удалось определить версии для сравнения.")
        else:
            print(f"Не удалось проверить обновления. Код ответа сервера {response.status_code}")
    except Exception as e:
        print(f"Ошибка при проверке обновлений {e}")

if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        API_ID = config.get("API_ID")
        API_HASH = config.get("API_HASH")
        PHONE_NUMBER = config.get("PHONE_NUMBER")
    except (json.JSONDecodeError, KeyError) as e:
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None
else:
    API_ID = None
    API_HASH = None
    PHONE_NUMBER = None

if not API_ID or not API_HASH or not PHONE_NUMBER:
    try:
        print("Пожалуйста, введите данные для авторизации в Telegram:")        
        API_ID = int(input("Введите ваш API ID: "))
        API_HASH = input("Введите ваш API Hash: ").strip()
        PHONE_NUMBER = input("Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX): ").strip()

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "API_ID": API_ID,
                "API_HASH": API_HASH,
                "PHONE_NUMBER": PHONE_NUMBER
            }, f)
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")
        exit(1)

client = TelegramClient(f"session_{PHONE_NUMBER.replace('+', '').replace('-', '')}", API_ID, API_HASH)

async def animate_text(client, event, text):
    displayed_text = ""
    for char in text:
        displayed_text += char
        await client.edit_message(event.chat_id, event.message.id, displayed_text + cursor_symbol)
        await asyncio.sleep(typing_speed)
    await client.edit_message(event.chat_id, event.message.id, displayed_text)

async def pixel_destruction(client, event, text):
    lines_count = 4
    chunk_size = len(text) // lines_count
    text_lines = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    previous_text = ""
    pixelated_text = [list(" " * len(line)) for line in text_lines]
    for _ in range(5):
        for i in range(len(pixelated_text)):
            for j in range(len(pixelated_text[i])):
                if random.random() < 0.1:
                    pixelated_text[i][j] = random.choice([".", "◯", "⊙ ", "◎ ", "○"])
        displayed_text = "\n".join(["".join(line) for line in pixelated_text])
        if displayed_text != previous_text and displayed_text.strip() != "":
            try:
                await client.edit_message(event.chat_id, event.message.id, displayed_text)
                previous_text = displayed_text
            except ValueError:
                pass
        await asyncio.sleep(pixel_typing_speed)

    for _ in range(5):
        displayed_text = "\n".join(["".join([random.choice([".", "◯", "⊙ ", "◎ ", "○"]) for _ in range(len(line))]) for line in text_lines])
        if displayed_text != previous_text and displayed_text.strip() != "":
            try:
                await client.edit_message(event.chat_id, event.message.id, displayed_text)
                previous_text = displayed_text
            except ValueError:
                pass
        await asyncio.sleep(pixel_typing_speed)

    await client.edit_message(event.chat_id, event.message.id, text)

# Новая анимация "Падение букв сверху вниз"
async def falling_text_animation(client, event, text):
    lines = text.split("\n")
    progress_events = [asyncio.Event() for _ in lines]

    async def animate_line(line, progress_event, next_event=None):
        original_text = list(line)
        placeholder = [" " for _ in original_text]
        total_letters = len(original_text)
        displayed_letters = 0

        while displayed_letters < total_letters:
            available_indices = [j for j, char in enumerate(placeholder) if char == " "]
            if available_indices:
                chosen_index = random.choice(available_indices)
                placeholder[chosen_index] = original_text[chosen_index]
                displayed_letters += 1

            displayed_text = "\n".join(["".join(placeholder) if i == index else line
                                        for index, line in enumerate(lines)])


            if displayed_letters >= int(0.8 * total_letters) and not progress_event.is_set():
                progress_event.set()

            await asyncio.sleep(0.2)

        if next_event:
            next_event.set()

    tasks = []
    for i in range(len(lines) - 1, -1, -1):
        next_event = progress_events[i + 1] if i + 1 < len(progress_events) else None
        tasks.append(animate_line(lines[i], progress_events[i], next_event))

    await asyncio.gather(*tasks)

@client.on(events.NewMessage(pattern='/falling'))
async def falling_animation_handler(event):
    if event.out:
        command_text = event.raw_text
        if len(command_text.split()) > 1:
            text_to_animate = command_text.partition(' ')[2]
            await falling_text_animation(client, event, text_to_animate)
        else:
            await event.reply("Пожалуйста, укажите текст для анимации после команды /falling.")

@client.on(events.NewMessage(pattern='/p'))
async def animate_handler(event):
    if event.out:
        command_text = event.raw_text
        if len(command_text.split()) > 1:
            text_to_animate = command_text.partition(' ')[2]
            if selected_animation == 1:
                await animate_text(client, event, text_to_animate)
            elif selected_animation == 2:
                await pixel_destruction(client, event, text_to_animate)
            elif selected_animation == 3:
                await falling_text_animation(client, event, text_to_animate)
        else:
            await event.reply("Пожалуйста, укажите текст для анимации после команды /p.")

@client.on(events.NewMessage(pattern='/1'))
async def list_animations(event):
    if event.out:
        animation_list = "Анимации:\n" + "\n".join([f"{i}) {name}" for i, name in animations.items()])
        await event.reply(animation_list)

@client.on(events.NewMessage(pattern='^\\d+$'))
async def change_animation(event):
    if event.out:
        global selected_animation
        animation_number = int(event.raw_text)
        if animation_number in animations:
            selected_animation = animation_number
            messages = await client.get_messages(event.chat_id, limit=3)
            for msg in messages:
                if msg.out:
                    await client.delete_messages(event.chat_id, msg.id)

async def main():
    await client.start(phone=PHONE_NUMBER)
    print(f"Успешно авторизованы как {PHONE_NUMBER}")
    await client.run_until_disconnected()
# Новый обработчик для команды /magic
@client.on(events.NewMessage(pattern='/magic'))
async def magic_handler(event):
    # Переход в set.py и вызов функции magic_script
    await set.magic_script(client, event)

async def main():
    await client.start(phone=PHONE_NUMBER)
    print(f"Успешно авторизованы как {PHONE_NUMBER}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
