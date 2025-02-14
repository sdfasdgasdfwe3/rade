#!/data/data/com.termux/files/usr/bin/bash
# install.sh — автоматическая установка зависимостей для бота в Termux

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
pip install telethon requests

echo "-----------------------------------------"
echo "Делаем главный файл исполняемым..."
chmod +x bot.py

echo "-----------------------------------------"
# Создаем .bashrc, если его нет, и добавляем автозапуск...
touch ~/.bashrc
echo 'cd ~/rade && git pull && python3 bot.py' >> ~/.bashrc
echo 'ps aux | grep python' >> ~/.bashrc

echo "Установка завершена. Перезапустите Termux, чтобы бот запускался автоматически."
