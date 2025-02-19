import os
import asyncio
import json
import sqlite3
from telethon import TelegramClient, events, errors
from animation_script import animations

# Автообновляем репозиторий (не трогая сессию)
os.system('git pull')

CONFIG_FILE = "config.json"
SESSION_NAME = "session"  # имя сессии (файл session.session)

# Словарь для хранения выбранных анимаций по чатам
selected_animations = {}

def load_or_create_config():
    """Загружает API-данные из файла или запрашивает у пользователя и создает файл."""
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
    print("Конфигурация сохранена в config.json.")
    return config

def create_client(config):
    return TelegramClient(SESSION_NAME, config["api_id"], config["api_hash"])

async def authorize(client, config):
    """Функция авторизации в Telegram."""
    await client.connect()
    if await client.is_user_authorized():
        print("Вы уже авторизованы. Запускаем бота...")
        return True
    print("Вы не авторизованы. Начинаем процесс авторизации...")
    try:
        await client.send_code_request(config["phone_number"])
        code = input('Введите код из Telegram: ')
        await client.sign_in(config["phone_number"], code)
    except errors.SessionPasswordNeededError:
        password = input('Введите пароль 2FA: ')
        await client.sign_in(password=password)
    print("Успешная авторизация!")
    return True

@events.register(events.NewMessage(pattern=r'^/m$'))
async def handle_m_command(event):
    """Обработка команды /m - вывод списка анимаций."""
    text = "Список доступных анимаций:\n"
    for num, (name, _) in animations.items():
        text += f"{num}. {name}\n"
    await event.respond(text)

@events.register(events.NewMessage(pattern=r'^[1-9]\d*$'))
async def handle_animation_selection(event):
    """Обработка выбора анимации цифрой."""
    try:
        selection = int(event.message.text)
        if selection in animations:
            selected_animations[event.chat_id] = selection
            await event.respond(f"Выбрана анимация: {animations[selection][0]}")
            # Удаляем 4 последних сообщения бота
            me = await event.client.get_me()
            bot_messages = await event.client.get_messages(event.chat_id, limit=4, from_user=me.id)
            await event.client.delete_messages(event.chat_id, [msg.id for msg in bot_messages])
    except ValueError:
        pass  # Игнорируем неверный ввод

@events.register(events.NewMessage(pattern=r'^/p\s+(.+)'))
async def handle_p_command(event):
    """Обработка команды /p - запуск анимации текста."""
    text = event.pattern_match.group(1)
    anim_number = selected_animations.get(event.chat_id, 1)
    animation_func = animations[anim_number][1]
    try:
        await animation_func(event, text)
    except Exception as e:
        await event.respond(f"⚠ Ошибка анимации: {e}")

async def main():
    config = load_or_create_config()
    client = create_client(config)
    if await authorize(client, config):
        client.add_event_handler(handle_m_command)
        client.add_event_handler(handle_animation_selection)
        client.add_event_handler(handle_p_command)
        print("Бот работает...")
        await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен пользователем.")
