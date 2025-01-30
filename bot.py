import hashlib
import os
import sys
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
import requests
import configparser
import subprocess
from telethon import events

def reset_local_changes():
    try:
        subprocess.run(["git", "stash", "push", "--", ".", ":!config.ini"], check=True)
        subprocess.run(["git", "clean", "-fd", "--exclude=config.ini"], check=True)
    except subprocess.CalledProcessError:
        pass

def check_for_updates():
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
    LOCAL_FILE = "bot.py"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "application/vnd.github.v3.raw"
        }
        
        local_hash = ""
        if os.path.exists(LOCAL_FILE):
            with open(LOCAL_FILE, 'rb') as f:
                local_hash = hashlib.sha256(f.read()).hexdigest()
        
        response = requests.get(GITHUB_RAW_URL, headers=headers, timeout=10)
        
        if response.status_code in [404, 403]:
            return
        response.raise_for_status()
        
        remote_content = response.text
        remote_hash = hashlib.sha256(remote_content.encode()).hexdigest()
        
        if local_hash != remote_hash:
            if os.path.exists(LOCAL_FILE):
                os.rename(LOCAL_FILE, LOCAL_FILE + ".bak")
            with open(LOCAL_FILE, 'w', encoding='utf-8') as f:
                f.write(remote_content)
            os.execv(sys.executable, [sys.executable] + sys.argv)
            
    except Exception:
        pass

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists('config.ini'):
        config.read('config.ini')
        if 'Telegram' not in config:
            raise ValueError("Конфигурация Telegram отсутствует в config.ini!")
        return config['Telegram']
    else:
        api_id = input("Введите API ID: ")
        api_hash = input("Введите API HASH: ")
        phone_number = input("Введите номер телефона (+7xxxxxxxxx): ")
        config['Telegram'] = {
            'api_id': api_id,
            'api_hash': api_hash,
            'phone_number': phone_number
        }
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        return config['Telegram']

def run_animation_script(client, chat_id):
    script_path = "animation_script.py"
    
    try:
        subprocess.run([sys.executable, script_path], check=True)
        client.send_message(chat_id, "Переход в скрипт анимаций выполнен!")
    except subprocess.CalledProcessError:
        client.send_message(chat_id, "Ошибка при выполнении скрипта анимаций!")

async def message_handler(event):
    if isinstance(event, events.NewMessage.Event):
        if event.message.message == "Анимации":
            chat_id = event.message.chat_id
            run_animation_script(client, chat_id)
        elif event.message.message == "Сброс":
            reset_local_changes()
            await event.reply("Локальные изменения удалены, кроме config.ini.")

if __name__ == "__main__":
    check_for_updates()

    try:
        config = load_config()
        api_id = config['api_id']
        api_hash = config['api_hash']
        phone_number = config['phone_number']

        client = TelegramClient('session_name', api_id, api_hash)
        client.connect()
        
        if not client.is_user_authorized():
            client.send_code_request(phone_number)
            code = input("Введите полученный код: ")
            
            try:
                client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                password = input("Введите пароль двухэтапной аутентификации: ")
                client.sign_in(password=password)
        
        check_for_updates()
        client.add_event_handler(message_handler, events.NewMessage)
        client.run_until_disconnected()

    except Exception:
        pass
    finally:
        client.disconnect()
