import hashlib
import os
import sys
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
import requests

def check_for_updates():
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3ra/main/bot.py"  # Проверьте URL!
    LOCAL_FILE = "bot.py"
    
    try:
        # Добавляем заголовки для GitHub API
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "application/vnd.github.v3.raw"
        }
        
        # Получаем текущий хеш локального файла
        local_hash = ""
        if os.path.exists(LOCAL_FILE):
            with open(LOCAL_FILE, 'rb') as f:
                local_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Делаем запрос с таймаутом
        response = requests.get(GITHUB_RAW_URL, headers=headers, timeout=10)
        
        # Проверяем статус ответа
        if response.status_code == 404:
            print("Файл обновления не найден на GitHub!")
            return
        if response.status_code == 403:
            print("Достигнут лимит запросов к GitHub!")
            return
        response.raise_for_status()  # Проверка других ошибок
        
        remote_content = response.text
        remote_hash = hashlib.sha256(remote_content.encode()).hexdigest()
        
        if local_hash != remote_hash:
            print("Обнаружено обновление! Загружаем новую версию...")
            with open(LOCAL_FILE, 'w', encoding='utf-8') as f:
                f.write(remote_content)
            print("Файл обновлен. Перезапуск скрипта...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
            
    except requests.exceptions.HTTPError as e:
        print(f"HTTP ошибка при проверке обновлений: {e.response.status_code}")
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {str(e)}")

# Проверка обновлений перед запуском
check_for_updates()

# Остальной код авторизации
api_id = int(input("Введите API ID: "))
api_hash = input("Введите API HASH: "))
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
