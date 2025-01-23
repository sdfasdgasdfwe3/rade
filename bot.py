import os
import sys
import time
import git
import subprocess
import importlib
from telethon import TelegramClient, events
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

# Перезапуск бота
def restart_bot():
    print("Перезагружаю бота...")
    subprocess.Popen([sys.executable, os.path.abspath(__file__)])  # Запуск нового процесса
    sys.exit()  # Завершаем старый процесс

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
    print("Бот успешно запущен!")

    # Настройка структуры проекта
    setup_project_structure()

    # Проверка обновлений и перезапуск, если необходимо
    if update_script():
        restart_bot()

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
        # Код для обработки сообщений и команд
        pass

# Запуск бота
if __name__ == "__main__":
    client = TelegramClient('session_name', api_id, api_hash)
    client.loop.run_until_complete(main())
