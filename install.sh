#!/bin/bash

# Логирование установки
log_file="install.log"
echo "Логирование установки в файл: $log_file"
exec > >(tee -a "$log_file") 2>&1

# Функция для обработки ошибок
error_exit() {
    echo "Ошибка: $1"
    exit 1
}

# Обновление пакетов Termux
echo "Обновление пакетов..."
pkg update -y && pkg upgrade -y || error_exit "Не удалось обновить пакеты."

# Установка зависимостей
echo "Установка Python, Git и pip..."
pkg install -y python git python-pip || error_exit "Не удалось установить зависимости."

# Установка Telethon
echo "Установка библиотеки Telethon..."
pip install telethon || error_exit "Не удалось установить Telethon."

# Создание директории для бота
bot_dir="$HOME/rade"
echo "Создание директории для бота: $bot_dir"
mkdir -p "$bot_dir" || error_exit "Не удалось создать директорию."
cd "$bot_dir" || error_exit "Не удалось перейти в директорию."

# Скачивание файла bot.py
echo "Скачивание кода бота..."
wget -O bot.py https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py || error_exit "Не удалось скачать bot.py."

# Создание конфигурационного файла (если его нет)
if [ ! -f config.txt ]; then
    echo "Создание config.txt..."
    cat > config.txt << EOL
API_ID=your_api_id_here
API_HASH=your_api_hash_here
PHONE_NUMBER=your_phone_number_here
EOL
    echo "Замените данные в config.txt на свои!"
else
    echo "Файл config.txt уже существует."
fi

# Создание скрипта для запуска
echo "Создание скрипта запуска..."
echo "python3 bot.py" > start.sh
chmod +x start.sh || error_exit "Не удалось добавить права на выполнение."

# Запуск бота
echo "Запуск бота..."
./start.sh
