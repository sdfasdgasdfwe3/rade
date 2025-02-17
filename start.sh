#!/bin/bash

source venv/bin/activate
cd ~/rade

# Удалить старый PID-файл
rm -f .bot_pid

# Запустить бота в фоне и записать PID
python3 bot.py &
echo $! > .bot_pid

# Функция для остановки
cleanup() {
    echo "Остановка бота..."
    kill -9 $(cat .bot_pid) 2>/dev/null
    rm -f .bot_pid
}

# Перехват сигналов
trap cleanup EXIT TERM INT

# Бесконечное ожидание
while true; do
    sleep 1
done
