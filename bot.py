import os
import asyncio
import json
import sqlite3
from telethon import TelegramClient, errors, events
from animation_script import animations

# Автообновляем репозиторий (не трогая сессию)
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

def create_client(config):
    return TelegramClient(SESSION_NAME, config["api_id"], config["api_hash"])

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

# Словарь для хранения выбранных анимаций по чатам
selected_animations = {}
# Словарь для отслеживания, что бот ожидает ввод цифры для выбора анимации
awaiting_selection = {}

@events.register(events.NewMessage(pattern=r'^/m\b'))
async def handle_m_command(event):
    """Обработка команды /m - выбор анимации."""
    parts = event.message.text.split()
    if len(parts) == 1:
        # Отправляем список доступных анимаций и просим отправить цифру выбора
        text = "Список доступных анимаций:\n"
        for num, (name, _) in animations.items():
            text += f"{num}. {name}\n"
        text += "\nОтправьте цифру для выбора анимации."
        await event.respond(text)
        awaiting_selection[event.chat_id] = True
    else:
        try:
            selection = int(parts[1])
            if selection in animations:
                selected_animations[event.chat_id] = selection
                # Отправляем подтверждение выбора анимации
                confirmation = await event.respond(f"Выбрана анимация: {animations[selection][0]}")
                # Ждем небольшую паузу, чтобы сообщение успело сохраниться
                await asyncio.sleep(0.5)
                # Получаем 3 предыдущих сообщения относительно подтверждения и удаляем их вместе с подтверждением
                older_msgs = await event.client.get_messages(event.chat_id, limit=3, offset_id=confirmation.id)
                ids_to_delete = [confirmation.id] + [msg.id for msg in older_msgs]
                await event.client.delete_messages(event.chat_id, ids_to_delete)
            else:
                await event.respond("❌ Неверный номер анимации.")
        except ValueError:
            await event.respond("❌ Укажите корректный номер анимации после /m.")

@events.register(events.NewMessage(pattern=r'^\d+$'))
async def handle_animation_digit(event):
    """Обработка сообщения, состоящего только из цифры, для выбора анимации."""
    if event.chat_id in awaiting_selection and awaiting_selection[event.chat_id]:
        try:
            selection = int(event.message.text)
            if selection in animations:
                selected_animations[event.chat_id] = selection
                confirmation = await event.respond(f"Выбрана анимация: {animations[selection][0]}")
                awaiting_selection[event.chat_id] = False  # сбрасываем состояние ожидания
                await asyncio.sleep(0.5)
                older_msgs = await event.client.get_messages(event.chat_id, limit=3, offset_id=confirmation.id)
                ids_to_delete = [confirmation.id] + [msg.id for msg in older_msgs]
                await event.client.delete_messages(event.chat_id, ids_to_delete)
            else:
                await event.respond("❌ Неверный номер анимации.")
        except ValueError:
            await event.respond("❌ Укажите корректный номер анимации.")
    # Если бот не ожидает ввода, ничего не делаем

@events.register(events.NewMessage(pattern=r'^/p\b'))
async def handle_p_command(event):
    """Обработка команды /p - запуск анимации текста."""
    parts = event.message.text.split(maxsplit=1)
    if len(parts) == 1:
        await event.respond("❌ Укажите текст после /p.")
    else:
        text = parts[1]
        anim_number = selected_animations.get(event.chat_id, 1)
        animation_func = animations[anim_number][1]
        try:
            await animation_func(event, text)
        except Exception as e:
            await event.respond(f"⚠ Ошибка анимации: {e}")

async def main():
    config = load_or_create_config()
    client = create_client(config)
    # Регистрация обработчиков событий
    client.add_event_handler(handle_m_command)
    client.add_event_handler(handle_animation_digit)
    client.add_event_handler(handle_p_command)
    
    if await authorize(client, config):
        # Получаем данные авторизованного пользователя
        me = await client.get_me()
        # Выводим информацию
        print(f"Вы авторизированы как: {me.username if me.username else me.first_name}")
        print("Наш TG: t.me/kwotko")
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
