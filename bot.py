import os
import importlib
from telethon import TelegramClient, events

# Данные авторизации
api_id = 123456  # Замените на свой API ID
api_hash = "your_api_hash"  # Замените на свой API Hash
phone = "your_phone_number"  # Замените на свой номер телефона

# Папка для хранения модулей
modules_path = "modules"

# Путь к файлу сессии
session_file = "user_session"  # Уникальное имя сессии (можно добавить номер телефона или имя пользователя)

# Создаем клиента с указанием имени сессии
client = TelegramClient(session_file, api_id, api_hash)

# Функция для загрузки доступных модулей
def load_modules():
    modules = []
    if not os.path.exists(modules_path):
        os.makedirs(modules_path)
    for file in os.listdir(modules_path):
        if file.endswith(".py"):
            module_name = file[:-3]  # Убираем .py
            modules.append(module_name)
    return modules

# Загрузка и выполнение команд
async def handle_message(event):
    text = event.raw_text
    modules = load_modules()

    for module_name in modules:
        module = importlib.import_module(f"{modules_path}.{module_name}")
        if hasattr(module, "handle_command"):
            await module.handle_command(client, event, text)

# Обработчик сообщений
@client.on(events.NewMessage)
async def on_new_message(event):
    await handle_message(event)

# Основная логика
async def main():
    # Если сессия не существует, нужно пройти авторизацию
    await client.start(phone)
    print("Бот запущен и авторизация завершена!")

    # Запуск бота и ожидание новых сообщений
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Запуск асинхронного метода
    client.loop.run_until_complete(main())
