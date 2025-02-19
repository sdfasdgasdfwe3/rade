#!/bin/bash

# Устанавливаем необходимые пакеты
pkg install -y python git

# Клонируем репозиторий
git clone https://raw.githubusercontent.com/sdfasdgasdfwe3/rade.git
cd your-bot

# Устанавливаем зависимости
pip install --quiet telethon

# Добавляем автоматический переход в папку с ботом при запуске Termux
if ! grep -q "your-bot" ~/.bashrc; then
    echo 'cd ~/your-bot' >> ~/.bashrc
    echo 'echo "Для запуска бота напишите: python bot.py"' >> ~/.bashrc
fi

# Применяем изменения в текущей сессии
source ~/.bashrc

# Запускаем бота
python bot.py
