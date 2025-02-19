import os
import asyncio
import json
import sqlite3
from telethon import TelegramClient, events, errors
from animation_script import animations

os.system('git pull')

CONFIG_FILE = "config.json"
SESSION_NAME = "session"

selected_animations = {}
awaiting_animation_choice = set()

def load_or_create_config():
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

async def safe_connect(client, retries=5, delay=2):
    for attempt in range(1, retries + 1):
        try:
            await client.connect()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                await asyncio.sleep(delay)
            else:
                raise
    raise Exception("Не удалось подключиться к сессии, база данных постоянно заблокирована.")

async def safe_disconnect(client, retries=5, delay=2):
    for attempt in range(1, retries + 1):
        try:
            await client.disconnect()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                await asyncio.sleep(delay)
            else:
                raise
    print("Предупреждение: не удалось корректно отключиться, возможно, сессия не сохранена.")

def create_client(config):
    return TelegramClient(SESSION_NAME, config["api_id"], config["api_hash"])

async def authorize(client, config):
    await safe_connect(client)
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
    except errors.AuthRestartError:
        print("Telegram требует перезапуска авторизации. Повторяем попытку...")
        await client.send_code_request(config["phone_number"])
        code = input('Введите код из Telegram: ')
        await client.sign_in(config["phone_number"], code)
    except Exception as e:
        print(f'Ошибка авторизации: {e}')
        return False
    print("Успешная авторизация!")
    return True

@events.register(events.NewMessage(pattern=r'^/m$'))
async def handle_m_command(event):
    """Вывод списка анимаций и ожидание выбора."""
    text = "Список доступных анимаций:\n"
    for num, (name, _) in animations.items():
        text += f"{num}. {name}\n"
    text += "\nОтправьте номер анимации, чтобы выбрать её."
    await event.respond(text)
    awaiting_animation_choice.add(event.chat_id)

@events.register(events.NewMessage)
async def handle_message(event):
    """Обработка выбора анимации или анимации текста."""
    chat_id = event.chat_id

    if chat_id in awaiting_animation_choice:
        if event.text.isdigit():
            selection = int(event.text.strip())
            if selection in animations:
                selected_animations[chat_id] = selection
                confirmation = await event.respond(f"Выбрана анимация: {animations[selection][0]}")
                awaiting_animation_choice.remove(chat_id)

                me = await event.client.get_me()
                bot_messages = await event.client.get_messages(chat_id, limit=4, from_user=me.id)
                await event.client.delete_messages(chat_id, [msg.id for msg in bot_messages])
            return
        else:
            return  # Игнорируем нечисловой ввод, не отправляя лишних сообщений

    if event.text.startswith("/p "):
        parts = event.text.split(maxsplit=1)
        if len(parts) == 1:
            await event.respond("❌ Укажите текст после /p.")
        else:
            text = parts[1]
            anim_number = selected_animations.get(chat_id, 1)
            animation_func = animations[anim_number][1]
            try:
                # Проверка на изменение текста перед редактированием
                async def safe_edit(message, new_text):
                    if message.text != new_text:
                        await message.edit(new_text)

                await animation_func(event, text, safe_edit)
            except errors.rpcerrorlist.MessageNotModifiedError:
                pass  # Игнорируем ошибку "Content of the message was not modified"
            except Exception as e:
                await event.respond(f"⚠ Ошибка анимации: {e}")

async def main():
    config = load_or_create_config()
    client = create_client(config)
    if await authorize(client, config):
        client.add_event_handler(handle_m_command)
        client.add_event_handler(handle_message)
        print("Бот работает...")
        try:
            await client.run_until_disconnected()
        except Exception as e:
            print(f"Ошибка в работе бота: {e}")
    await safe_disconnect(client)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен пользователем.")
    except Exception as e:
        print(f"Ошибка: {e}")
