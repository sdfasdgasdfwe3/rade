#!/bin/bash

# Проверка наличия Python
if ! command -v python3 &>/dev/null; then
    echo "Python3 не найден. Устанавливаем Python3..."
    pkg install python -y
fi

# Проверка наличия pip
if ! command -v pip3 &>/dev/null; then
    echo "pip3 не найден. Устанавливаем pip..."
    python3 -m ensurepip --upgrade
fi

# Установка зависимостей
echo "Устанавливаем зависимости..."
pip3 install -r <(echo -e "requests\ntelethon\npsutil")

# Обновление репозитория
echo "Обновляем репозиторий..."
git pull || git clone https://github.com/sdfasdgasdfwe3/rade.git

# Переход в папку с репозиторием
cd rade || { echo "Ошибка перехода в папку 'rade'"; exit 1; }

# Проверка наличия файла с зависимостями и его установка
echo "Устанавливаем Python зависимости..."
pip3 install -r requirements.txt

# Делаем главный файл исполняемым
chmod +x bot.py

# Проверка на существование сессии tmux и запуск бота
SESSION_NAME="bot_session"
echo "Проверка наличия активной tmux сессии..."

tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
    echo "Сессия не найдена, создаем новую сессию..."
    tmux new-session -d -s $SESSION_NAME "python3 bot.py"
else
    echo "Сессия найдена, подключаемся к существующей сессии..."
    tmux attach -t $SESSION_NAME
fi

# Добавляем автозапуск при старте
echo "Добавляем автозапуск в .bashrc..."
echo "tmux has-session -t $SESSION_NAME 2>/dev/null || tmux new-session -d -s $SESSION_NAME 'python3 ~/rade/bot.py'" >> ~/.bashrc

echo "Установка завершена. Бот успешно запущен!"
