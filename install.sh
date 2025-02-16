#!/data/data/com.termux/files/usr/bin/bash
# install.sh — автоматическая установка и запуск бота в Termux

echo "-----------------------------------------"
echo "Обновляем пакеты..."
pkg update -y && pkg upgrade -y

echo "-----------------------------------------"
echo "Устанавливаем Python..."
pkg install python -y

echo "-----------------------------------------"
echo "Устанавливаем Git..."
pkg install git -y

echo "-----------------------------------------"
echo "Удаляем старую версию репозитория (если есть)..."
rm -rf rade

echo "-----------------------------------------"
echo "Клонируем репозиторий..."
git clone https://github.com/sdfasdgasdfwe3/rade.git

# Переходим в директорию репозитория
cd rade || { echo "Ошибка: не удалось перейти в директорию 'rade'"; exit 1; }

echo "-----------------------------------------"
echo "Устанавливаем зависимости Python..."
pip install telethon requests psutil

echo "-----------------------------------------"
echo "Запускаем бота..."
python bot.py

# Добавляем автозапуск в .bashrc
echo "-----------------------------------------"
echo "Настроим автозапуск бота при следующем открытии Termux..."
echo "bash /data/data/com.termux/files/home/rade/install.sh" >> ~/.bashrc

echo "Автозапуск настроен. Теперь при следующем запуске терминала скрипт будет запускаться автоматически."
