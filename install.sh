#!/data/data/com.termux/files/usr/bin/bash

# Проверяем, запущен ли уже процесс бота
if pgrep -f "python3 bot.py" > /dev/null; then
    echo "Бот уже запущен. Прерываем запуск."
    exit 0
fi

# Завершаем все процессы Python перед запуском бота
echo "Завершаем все процессы Python..."
killall -9 python3

# Ждем несколько секунд, чтобы процессы завершились
echo "Ожидаем завершение процессов..."
sleep 10  # Увеличиваем задержку

# Проверяем, если процессы все равно остались
if pgrep -f "python3" > /dev/null; then
    echo "Некоторые процессы Python не завершились. Пробуем снова."
    killall -9 python3
    sleep 10  # Еще раз увеличиваем время ожидания
fi

# Если процессы все равно не завершены, принудительно завершаем
if pgrep -f "python3" > /dev/null; then
    echo "Ошибка: Процесс не завершается. Прерываем выполнение скрипта."
    exit 1
fi

# Далее выполняем установку зависимостей и запуск бота
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

# Проверка и создание tmux сессии с ботом
echo "-----------------------------------------"
echo "Проверка наличия активной tmux сессии..."
tmux has-session -t session_name 2>/dev/null

if [ $? != 0 ]; then
    echo "Сессия не найдена, создаем новую сессию..."
    tmux new-session -d -s session_name "python3 bot.py"
else
    echo "Подключаемся к существующей сессии..."
    tmux attach -t session_name
fi

# Создаем .bashrc и добавляем автозапуск
echo "-----------------------------------------"
echo "Создаем .bashrc, если его нет, и добавляем автозапуск..."
touch ~/.bashrc
echo 'tmux has-session -t session_name 2>/dev/null || tmux new-session -d -s session_name "python3 ~/rade/bot.py"' >> ~/.bashrc

echo "Установка завершена. Перезапустите Termux, чтобы бот запускался автоматически."

# Решение проблемы с блокировкой базы данных SQLite

echo "-----------------------------------------"
echo "Пытаемся подключиться к базе данных с обработкой ошибок..."
python3 - <<EOF
import sqlite3
import time

def connect_with_retry(db_name):
    retries = 5
    for _ in range(retries):
        try:
            conn = sqlite3.connect(db_name)
            conn.execute('PRAGMA journal_mode=WAL;')  # Включаем режим WAL для улучшения работы с блокировками
            return conn
        except sqlite3.OperationalError:
            print("Ошибка подключения к базе данных. Попробуем снова...")
            time.sleep(1)  # Подождите 1 секунду перед повторной попыткой
    raise Exception("Не удалось подключиться к базе данных после нескольких попыток.")

# Подключаемся к базе данных
db_name = '/data/data/com.termux/files/home/rade/your_database.db'
connect_with_retry(db_name)
EOF

echo "Установка завершена."
