import asyncio
import subprocess
import os
import requests
import json
from telethon import TelegramClient, events

# Константы
CONFIG_FILE = 'config.json'
GITHUB_RAW_URL = 'https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py'
SCRIPT_VERSION = 0.1
DEFAULT_TYPING_SPEED = 0.1  # Уменьшаем скорость для эффекта печатной машинки
DEFAULT_CURSOR = u'\u2588'

# Функция для проверки обновлений
def check_for_updates():
    try:
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            remote_script = response.text
            current_file = os.path.abspath(__file__)

            with open(current_file, 'r', encoding='utf-8') as f:
                current_script = f.read()

            if remote_script != current_script:
                with open(current_file, 'w', encoding='utf-8') as f:
                    f.write(remote_script)
                print("Скрипт обновлен. Перезапустите программу.")
                exit()
    except Exception as e:
        print(f"Ошибка проверки обновлений: {e}")

# Загрузка конфигурации
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
else:
    config = {
        "API_ID": int(input("Введите ваш API ID: ")),
        "API_HASH": input("Введите ваш API Hash: ").strip(),
        "PHONE_NUMBER": input("Введите ваш номер телефона: ").strip(),
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f)

API_ID = config['API_ID']
API_HASH = config['API_HASH']
PHONE_NUMBER = config['PHONE_NUMBER']
SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}'

# Инициализация клиента
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Глобальные переменные для анимации
animations = {
    "1": "typing_machine",    # Печатная машинка
    "2": "running_line",      # Бегущая строка
    "3": "blinking_text",     # Мерцающий текст
    "4": "carousel_text",     # Карусель текста
}
selected_animation = "typing_machine"  # Устанавливаем печатную машинку как анимацию по умолчанию

# Анимации
async def typing_machine(event, text):
    # Эмуляция печатной машинки
    cursor = DEFAULT_CURSOR
    for i in range(len(text)):
        current_text = text[:i+1] + cursor
        await event.edit(current_text)
        await asyncio.sleep(DEFAULT_TYPING_SPEED)
    await event.edit(text)  # Заканчиваем, удаляя курсор

async def running_line(event, text):
    for i in range(len(text) + 1):
        await event.edit(text[:i])
        await asyncio.sleep(0.3)

async def blinking_text(event, text):
    for _ in range(5):
        await event.edit(text)
        await asyncio.sleep(0.5)
        await event.edit("")
        await asyncio.sleep(0.5)

async def carousel_text(event, text):
    for i in range(len(text)):
        rotated = text[i:] + text[:i]
        await event.edit(rotated)
        await asyncio.sleep(0.3)

# Обработчик команды выбора анимации
@client.on(events.NewMessage(pattern='/menu'))
async def menu_handler(event):
    # Выводим список анимаций как текст
    menu_text = (
        "Выберите стиль анимации:\n"
        "1. Печатная машинка\n"
        "2. Бегущая строка\n"
        "3. Мерцающий текст\n"
        "4. Карусель текста\n"
        "Введите номер выбранной анимации (1-4):"
    )
    await event.respond(menu_text)

# Обработчик текстовых сообщений для выбора анимации
@client.on(events.NewMessage(pattern=r'^[1-4]$'))
async def select_animation(event):
    global selected_animation
    choice = event.message.text.strip()  # Получаем выбор пользователя
    if choice in animations:
        selected_animation = animations[choice]
        await event.respond(f"Вы выбрали анимацию: {selected_animation.replace('_', ' ').title()}")
    else:
        await event.respond("Неверный выбор! Пожалуйста, выберите цифру от 1 до 4.")

# Обработчик анимаций
@client.on(events.NewMessage(pattern=r'/p (.+)'))
async def animated_text_handler(event):
    global selected_animation
    text = event.pattern_match.group(1)

    if selected_animation == "typing_machine":
        await typing_machine(event, text)
    elif selected_animation == "running_line":
        await running_line(event, text)
    elif selected_animation == "blinking_text":
        await blinking_text(event, text)
    elif selected_animation == "carousel_text":
        await carousel_text(event, text)

async def main():
    await client.start(phone=PHONE_NUMBER)
    print("Бот запущен. Для выбора анимации введите /menu, для запуска анимации используйте /p текст.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    check_for_updates()
    asyncio.run(main())
