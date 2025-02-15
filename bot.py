import os
import json
import requests
import sys
import subprocess
import asyncio
import signal
import time
from telethon import TelegramClient, events
import psutil
from animation_script import animations
import animation_script
import sqlite3  # Добавлен импорт sqlite3

# Константы
CONFIG_FILE = "config.json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
ANIMATION_SCRIPT_GITHUB_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/animation_script.py"
SCRIPT_VERSION = "0.2.41"

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

# Функция для установки режима WAL
def set_wal_mode():
    db_path = f"session_{PHONE_NUMBER.replace('+', '')}.session"
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")  # Включаем режим WAL
        conn.close()
        print(f"{EMOJIS['success']} Режим WAL включен для базы данных.")
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка при включении режима WAL: {e}")

def kill_previous_instances():
    """Безопасно завершает предыдущие экземпляры бота"""
    current_pid = os.getpid()
    killed = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info.get('cmdline', []))
            if ('python' in proc.info['name'].lower() 
                and 'bot.py' in cmdline 
                and proc.info['pid'] != current_pid):
                
                print(f"{EMOJIS['exit']} Завершаем процесс PID {proc.info['pid']}")
                proc.terminate()
                killed.append(proc.info['pid'])
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError, AttributeError):
            continue
    
    if killed:
        print(f"{EMOJIS['success']} Завершено процессов: {len(killed)}")
        time.sleep(2)
    
    return len(killed) > 0

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

# Включаем режим WAL перед созданием клиента
set_wal_mode()

client = TelegramClient(
    f"session_{PHONE_NUMBER.replace('+', '')}",
    API_ID,
    API_HASH,
    connection_retries=0
)

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

async def authenticate_client():
    """Функция для авторизации с поддержкой двухэтапной аутентификации"""
    try:
        await client.start(PHONE_NUMBER)
        print(f"{EMOJIS['success']} Авторизация успешна!")
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка авторизации:", e)
        sys.exit(1)

async def handle_2fa():
    """Обработка двухэтапной аутентификации"""
    try:
        print(f"{EMOJIS['auth']} Включена двухэтапная аутентификация. Введите облачный пароль:")
        password = input(f"{EMOJIS['auth']} Пароль: ").strip()
        await client.sign_in(password=password)
        print(f"{EMOJIS['success']} Облачный пароль принят!")
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка ввода пароля:", e)
        sys.exit(1)

async def close_client():
    if client.is_connected():
        await client.disconnect()
    print(f"\n{EMOJIS['exit']} Бот успешно остановлен.")

def signal_handler(sig, frame):
    print(f"\n{EMOJIS['exit']} Получен сигнал завершения. Останавливаем бота...")
    try:
        client.loop.run_until_complete(close_client())
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка остановки:", e)
    finally:
        sys.exit(0)

def main():
    kill_previous_instances()
    check_for_updates()
    check_for_animation_script_updates()
    
    try:
        # Запуск авторизации
        client.loop.run_until_complete(authenticate_client())
        
        # Проверка на двухэтапную аутентификацию
        if client.is_user_authorized():
            print(f"{EMOJIS['bot']} Скрипт запущен. Версия: {SCRIPT_VERSION}")
            me = client.loop.run_until_complete(client.get_me())
            username = me.username if me.username else (me.first_name if me.first_name else "Unknown")
            print(f"{EMOJIS['bot']} Вы авторизованы как: {username}")
            print("Телеграмм канал: t.me/kwotko")
            print("Для остановки нажмите Ctrl+C")
            signal.signal(signal.SIGINT, signal_handler)
            client.run_until_disconnected()
        else:
            # Если требуется двухэтапная аутентификация
            client.loop.run_until_complete(handle_2fa())
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
