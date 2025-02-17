#!/bin/bash

# Настройка логирования
log_file="setup.log"
echo "Логирование установки в файл: $log_file"
exec > >(tee -a "$log_file") 2>&1

# Установка зависимостей
echo "Обновление пакетов..."
pkg update && pkg upgrade -y || { echo "Ошибка при обновлении пакетов"; exit 1; }

echo "Установка Python, Git и pip..."
pkg install python -y || { echo "Ошибка при установке Python"; exit 1; }
pkg install git -y || { echo "Ошибка при установке Git"; exit 1; }
pkg install python-pip -y || { echo "Ошибка при установке pip"; exit 1; }

echo "Установка Telethon..."
pip install telethon || { echo "Ошибка при установке Telethon"; exit 1; }

# Создание директории для бота
bot_dir="/data/data/com.termux/files/home/rade"
echo "Создание директории для бота: $bot_dir"
mkdir -p "$bot_dir" || { echo "Ошибка при создании директории"; exit 1; }
cd "$bot_dir" || { echo "Ошибка при переходе в директорию"; exit 1; }

# Скачивание файла бота
echo "Скачивание файла бота..."
wget -O bot.py https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py || { echo "Ошибка при скачивании bot.py"; exit 1; }

# Создание конфигурационного файла
if [ ! -f config.txt ]; then
    echo "Создание config.txt..."
    echo "API_ID=your_api_id_here" > config.txt
    echo "API_HASH=your_api_hash_here" >> config.txt
    echo "PHONE_NUMBER=your_phone_number_here" >> config.txt
else
    echo "Файл config.txt уже существует."
fi

# Создание скрипта для запуска
echo "Создание скрипта запуска..."
echo "python3 bot.py" > start.sh
chmod +x start.sh || { echo "Ошибка при добавлении прав на выполнение"; exit 1; }

# Запуск бота
echo "Запуск бота..."
./start.sh
