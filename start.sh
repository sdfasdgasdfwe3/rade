#!/bin/bash

source venv/bin/activate
cd ~/rade

# Завершить предыдущий процесс, если есть
if [ -f .bot_pid ]; then
    old_pid=$(cat .bot_pid)
    kill -9 $old_pid 2>/dev/null
    rm .bot_pid
fi

# Запустить бота и сохранить PID
python3 bot.py &
echo $! > .bot_pid

# Остановить бота при выходе из Termux
trap 'kill -9 $(cat .bot_pid); rm .bot_pid' EXIT

# Бесконечное ожидание
wait
