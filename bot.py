import os
import sys
import requests
import git
import subprocess
import importlib
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from config import api_id, api_hash, phone_number, repo_path

# Функция для создания необходимых файлов и папок при отсутствии
def setup_project_structure():
    # Создание папки для модулей, если она отсутствует
    if not os.path.exists('modules'):
        os.makedirs('modules')

    # Создание файла с установленными модулями, если он отсутствует
    if not os.path.exists('installed_modules.txt'):
        with open('installed_modules.txt', 'w') as f:
            f.write("")  # Пустой файл, который позже будет обновляться

    # Создание конфигурационного файла, если он отсутствует
    if not os.path.exists('config.py'):
        with open('config.py', 'w') as f:
            f.write("# config.py\n")
            f.write("api_id = 'YOUR_API_ID'\n")
            f.write("api_hash = 'YOUR_API_HASH'\n")
            f.write("phone_number = 'YOUR_PHONE_NUMBER'\n")
            f.write("repo_path = '/path/to/your/repo'\n")

    # Создание файла зависимостей, если его нет
    if not os.path.exists('requirements.txt'):
        with open('requirements.txt', 'w') as f:
            f.write("telethon\n")
            f.write("gitpython\n")  # Добавьте другие зависимости по мере необходимости
    print("Проект настроен!")

# Функция для скачивания файла с GitHub
def download_file_from_github(url, dest_path):
    try:
        print(f"Скачиваю файл с {url}...")
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        print(f"Файл успешно скачан по адресу: {dest_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при скачивании файла: {e}")
        return False

# Функция для обновления бота с GitHub
def update_script_from_github():
    file_url = "https://raw.githubusercontent.com/username/repository/main/bot.py"  # Вставьте свою ссылку на файл
    dest_file = "bot.py"  # Путь, куда вы хотите сохранить файл (например, заменим текущий bot.py)

    # Скачиваем новый файл и сохраняем его
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
        origin.fetch()  # Получаем обновления с удаленного репозитория

        current_commit = repo.head.commit.hexsha
        origin.pull()  # Скачиваем последние изменения

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
    client = TelegramClient('session_name', api_id, api_hash)

    # Авторизация
    await client.start(phone_number)

    # Проверка, если сессия не авторизована, то запросить код и пароль
    if not await client.is_user_authorized():
        print("Необходимо пройти авторизацию!")
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, input('Введите код из SMS: '))

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
    client = TelegramClient('session_name', api_id, api_hash)
    client.loop.run_until_complete(main())
