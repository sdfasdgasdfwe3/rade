import hashlib
import os
import sys
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
import requests
import configparser

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
        
        if response.status_code == 404:
            print("Файл обновления не найден на GitHub!")
            return
        if response.status_code == 403:
            print("Достигнут лимит запросов к GitHub!")
            return
        response.raise_for_status()
        
        remote_content = response.text
        remote_hash = hashlib.sha256(remote_content.encode()).hexdigest()
        
        if local_hash != remote_hash:
            print("Обнаружено обновление! Загружаем новую версию...")
            with open(LOCAL_FILE, 'w', encoding='utf-8') as f:
                f.write(remote_content)
            print("Файл обновлен. Перезапуск скрипта...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
            
       except Exception as e:
        print(f"Ошибка при проверке обновлений: {str(e)}")

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists('config.ini'):
        config.read('config.ini')
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

check_for_updates()

config = load_config()
api_id = config['api_id']
api_hash = config['api_hash']
phone_number = config['phone_number']

client = TelegramClient('session_name', api_id, api_hash)

try:
    client.connect()
    
    if not client.is_user_authorized():
        client.send_code_request(phone_number)
        code = input("Введите полученный код: ")
        
        try:
            client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            password = input("Введите пароль двухэтапной аутентификации: ")
            client.sign_in(password=password)
    
    print("Авторизация успешна!")
    check_for_updates()

finally:
    client.disconnect()
