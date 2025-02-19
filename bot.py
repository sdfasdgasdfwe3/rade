import os
import asyncio
import json
import sqlite3
from telethon import TelegramClient, events, errors

# Автообновление репозитория (не трогая сессию)
os.system('git pull')

CONFIG_FILE = "config.json"
SESSION_NAME = "session"  # имя сессии (файл session.session)

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

async def safe_connect(client, retries=5, delay=2):
    """Пытается подключиться к Telegram с повторными попытками, если сессия заблокирована."""
    for attempt in range(1, retries + 1):
        try:
            await client.connect()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"База данных заблокирована. Попытка {attempt}/{retries} через {delay} сек...")
                await asyncio.sleep(delay)
            else:
                raise
    raise Exception("Не удалось подключиться к сессии, база данных постоянно заблокирована.")

async def safe_disconnect(client, retries=5, delay=2):
    """Пытается корректно отключиться с повторными попытками, если база данных заблокирована."""
    for attempt in range(1, retries + 1):
        try:
            await client.disconnect()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"Ошибка при отключении: база данных заблокирована. Попытка {attempt}/{retries} через {delay} сек...")
                await asyncio.sleep(delay)
            else:
                raise
    print("Предупреждение: не удалось корректно отключиться, возможно, сессия не сохранена.")

async def authorize(client, config):
    """Функция авторизации в Telegram."""
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

# Импортируем анимации из отдельного скрипта
from animation_script import animations

# Словарь для хранения выбранной анимации для каждого чата
selected_animations = {}

def get_animation_list():
    msg = "Доступные анимации:\n"
    for num, (name, _) in animations.items():
        msg += f"{num}: {name}\n"
    msg += "\nЧтобы выбрать анимацию, отправьте команду: /m <номер>"
    return msg

async def handle_commands(event):
    """Обработчик команд: /m и /p (бот реагирует только на команды, начинающиеся с '/')"""
    message = event.message.message.strip()
    if not message.startswith('/'):
        return

    if message.startswith('/m'):
        parts = message.split(maxsplit=1)
        if len(parts) == 1:
            # Отправляем список анимаций
            await event.reply(get_animation_list())
        else:
            try:
                selection = int(parts[1].strip())
                if selection in animations:
                    selected_animations[event.chat_id] = selection
                    # Отправляем сообщение с подтверждением выбора анимации
                    confirmation = await event.reply(f"Выбрана анимация ({animations[selection][0]})")
                    # Получаем id бота
                    me = await event.client.get_me()
                    # Получаем 4 последних сообщения, отправленные ботом
                    bot_messages = await event.client.get_messages(event.chat_id, limit=4, from_user=me.id)
                    # Удаляем их
                    await event.client.delete_messages(event.chat_id, [msg.id for msg in bot_messages])
                else:
                    await event.reply("Неверный номер анимации. Попробуйте снова.")
            except ValueError:
                await event.reply("Пожалуйста, укажите корректный номер анимации после /m.")
    elif message.startswith('/p'):
        parts = message.split(maxsplit=1)
        if len(parts) == 1:
            await event.reply("Пожалуйста, укажите текст для анимации после команды /p.")
        else:
            text = parts[1]
            anim_number = selected_animations.get(event.chat_id, 1)
            animation_func = animations[anim_number][1]
            try:
                await animation_func(event, text)
            except Exception as e:
                await event.reply(f"Ошибка при анимации текста: {e}")
    else:
        # Неизвестная команда – игнорируем
        pass

async def main():
    config = load_or_create_config()
    client = create_client(config)
    if await authorize(client, config):
        print("Бот работает...")
        client.add_event_handler(handle_commands, events.NewMessage)
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
