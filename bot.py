import hashlib
import os
import sys
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
import requests

def check_for_updates():
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3ra/main/bot.py"
    LOCAL_FILE = "bot.py"
    
    try:
        # Получаем текущий хеш локального файла
        local_hash = ""
        if os.path.exists(LOCAL_FILE):
            with open(LOCAL_FILE, 'rb') as f:
                local_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Скачиваем удаленную версию
        response = requests.get(GITHUB_RAW_URL)
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

# Проверка обновлений перед запуском
check_for_updates()

# Остальной код авторизации
api_id = int(input("Введите API ID: "))
api_hash = input("Введите API HASH: ")
phone_number = input("Введите номер телефона (+7xxxxxxxxx): ")

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
    check_for_updates()  # Дополнительная проверка после авторизации

finally:
    client.disconnect()
