import os
import requests
import subprocess
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Ваши настройки
API_ID = 'your_api_id'  # Ваш API ID
API_HASH = 'your_api_hash'  # Ваш API Hash
GITHUB_REPO = 'https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py'  # API для получения информации об обновлениях
AUTHORIZED_PHONE = 'your_phone_number'  # Номер телефона для авторизации
TOKEN = 'your_telegram_bot_token'  # Токен вашего бота

# Путь к файлу для хранения авторизованных пользователей (на устройстве пользователя)
USER_DATA_FILE = os.path.expanduser('~/.my_telegram_bot_data.json')  # Пример хранения в домашней папке пользователя

# Загрузка авторизованных пользователей из файла
def load_authorized_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Сохранение авторизованных пользователей в файл
def save_authorized_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)

# Функция для авторизации
def authenticate(update: Update, context: CallbackContext):
    authorized_users = load_authorized_users()
    user_id = update.message.from_user.id

    # Проверка, авторизован ли пользователь
    if user_id in authorized_users:
        update.message.reply_text("Вы уже авторизованы!")
    elif update.message.text.startswith(AUTHORIZED_PHONE):
        # Если номер телефона правильный, авторизуем пользователя
        authorized_users[user_id] = update.message.text
        save_authorized_users(authorized_users)
        update.message.reply_text("Вы успешно авторизованы!")
    else:
        update.message.reply_text("Неверный номер телефона!")

# Функция для проверки обновлений на GitHub
def check_updates():
    response = requests.get(GITHUB_REPO)
    if response.status_code == 200:
        commits = response.json()
        latest_commit = commits[0]['commit']['message']
        return f"Последнее обновление: {latest_commit}"
    else:
        return "Не удалось проверить обновления."

# Функция для обработки пересылки файлов и их установки
def handle_file(update: Update, context: CallbackContext):
    if update.message.document:
        file = update.message.document
        file_name = file.file_name
        file_id = file.file_id

        # Получаем файл с Telegram
        new_file = update.message.bot.get_file(file_id)
        new_file.download(file_name)

        # Пример команды для установки файла (можно подстроить под вашу задачу)
        try:
            subprocess.run(["pip", "install", file_name], check=True)
            update.message.reply_text(f"Модуль {file_name} успешно установлен.")
        except subprocess.CalledProcessError:
            update.message.reply_text(f"Ошибка установки модуля {file_name}.")
    else:
        update.message.reply_text("Пожалуйста, отправьте файл для установки.")

# Функция для обработки команды /start
def start(update: Update, context: CallbackContext):
    # Проверка, если файл с авторизацией существует
    if not os.path.exists(USER_DATA_FILE):
        update.message.reply_text("Пожалуйста, пройдите авторизацию, отправив свой номер телефона.")
    else:
        update.message.reply_text("Привет! Я бот для установки обновлений и модулей. Вы уже авторизованы.")

# Функция для проверки обновлений
def check_for_updates(update: Update, context: CallbackContext):
    updates = check_updates()
    update.message.reply_text(updates)

# Основная функция для запуска бота
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Команды
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("check_updates", check_for_updates))

    # Обработка сообщений и файлов
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, authenticate))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/octet-stream"), handle_file))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
