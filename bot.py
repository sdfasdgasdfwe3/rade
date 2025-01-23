import os
import sys
import json
import requests
import git
import subprocess
import importlib
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

# Конфигурация
CONFIG_FILE = "config.json"  # Файл конфигурации
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"  # URL для скачивания главного файла
DOWNLOADS_FOLDER = "/storage/emulated/0/Download/Telegram/"  # Папка загрузок на Android

# Функция для создания необходимых файлов и папок при отсутствии
def setup_project_structure():
    if not os.path.exists('modules'):
        os.makedirs('modules')

    if not os.path.exists('installed_modules.txt'):
        with open('installed_modules.txt', 'w') as f:
            f.write("")

    if not os.path.exists(CONFIG_FILE):
        API_ID = input("Введите API_ID: ")
        API_HASH = input("Введите API_HASH: ")
        PHONE_NUMBER = input("Введите номер телефона: ")
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({"API_ID": API_ID, "API_HASH": API_HASH, "PHONE_NUMBER": PHONE_NUMBER}, f)
    print("Проект настроен!")

# Загрузка конфигурации из файла
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get("API_ID"), config.get("API_HASH"), config.get("PHONE_NUMBER")
    else:
        print(f"Ошибка: файл конфигурации {CONFIG_FILE} не найден.")
        sys.exit(1)

# Функция для скачивания файла с GitHub
def download_file_from_github(url, dest_path):
    try:
        print(f"Скачиваю файл с {url}...")
        response = requests.get(url)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        print(f"Файл успешно скачан по адресу: {dest_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании файла: {e}")
        return False

# Функция для обновления бота с GitHub
def update_script_from_github():
    file_url = GITHUB_RAW_URL  # Ссылка на ваш файл
    dest_file = "bot.py"  # Путь к файлу

    if download_file_from_github(file_url, dest_file):
        print("Обновление прошло успешно. Перезагружаю бота...")
        restart_bot()
    else:
        print("Не удалось обновить файл.")

# Перезапуск бота
def restart_bot():
    print("Перезагружаю бота...")
    subprocess.Popen([sys.executable, os.path.abspath(__file__)])  # Запуск нового процесса
    sys.exit()  # Завершаем старый процесс

# Проверка наличия обновлений на GitHub
def update_script():
    try:
        repo = git.Repo(repo_path)
        origin = repo.remotes.origin
        origin.fetch()

        current_commit = repo.head.commit.hexsha
        origin.pull()

        updated_commit = repo.head.commit.hexsha

        if current_commit != updated_commit:
            print("Код был обновлен! Перезагружаю бота...")
            return True
        else:
            print("Обновлений нет.")
            return False
    except Exception as e:
        print(f"Ошибка при обновлении: {e}")
        return False

# Загрузка модуля
def load_module(module_name):
    try:
        importlib.import_module(module_name)
        print(f"Модуль {module_name} подключен.")
    except ImportError:
        print(f"Ошибка при подключении модуля {module_name}.")

# Получение списка установленных модулей
def get_installed_modules():
    installed = subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode("utf-8").split("\n")
    modules = [module.split("==")[0] for module in installed if module]
    
    with open("installed_modules.txt", "w") as f:
        for module in modules:
            f.write(module + '\n')

# Основная функция бота
async def main():
    # Загрузка конфигурации
    API_ID, API_HASH, PHONE_NUMBER = load_config()

    session_name = 'session_name'  # Уникальное имя сессии
    client = TelegramClient(session_name, API_ID, API_HASH)

    # Удаляем старую сессию, если она существует
    if os.path.exists(f"{session_name}.session"):
        os.remove(f"{session_name}.session")

    try:
        await client.start(PHONE_NUMBER)
    except Exception as e:
        print(f"Ошибка при старте клиента: {e}")
        return

    # Проверка авторизации
    if not await client.is_user_authorized():
        print("Необходимо пройти авторизацию!")
        await client.send_code_request(PHONE_NUMBER)
        await client.sign_in(PHONE_NUMBER, input('Введите код из SMS: '))

        try:
            await client.sign_in(password=input('Введите ваш 2FA пароль: '))
        except SessionPasswordNeededError:
            print("Пароль 2FA не требуется.")
        print("Авторизация прошла успешно!")

    print("Бот успешно запущен!")

    # Настройка структуры проекта
    setup_project_structure()

    # Проверка обновлений и перезапуск, если необходимо
    if update_script():
        restart_bot()

    # Получение списка установленных модулей
    get_installed_modules()

    # Проверка и установка модулей
    @client.on(events.NewMessage(pattern='/install_module'))
    async def install_module(event):
        if event.document:
            file_path = await event.download_media()
            print(f"Файл сохранен по пути: {file_path}")
            os.system(f"pip install {file_path}")
            await event.reply("Модуль успешно установлен!")

    # Команда для установки модуля через pip
    @client.on(events.NewMessage(pattern='^/up (.+)$'))
    async def download_module(event):
        module_name = event.pattern_match.group(1)
        os.system(f"pip install {module_name}")
        await event.reply(f"Модуль {module_name} успешно установлен!")

    # Основной цикл бота
    while True:
        pass

# Запуск бота
if __name__ == "__main__":
    # Загрузка конфигурации
    API_ID, API_HASH, PHONE_NUMBER = load_config()
    client = TelegramClient('session_name', API_ID, API_HASH)  # Передаем API_ID и API_HASH напрямую
    client.loop.run_until_complete(main())
