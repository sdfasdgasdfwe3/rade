#!/data/data/com.termux/files/usr/bin/bash

# Завершаем все процессы Python перед запуском бота
kill -9 $(ps aux | grep '[p]ython' | awk '{print $2}')

# Ждем несколько секунд, чтобы процессы завершились
sleep 5

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

# Переходим к tmux сессии
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
echo 'cd ~/rade && git pull && tmux has-session -t session_name 2>/dev/null || tmux new-session -d -s session_name "python3 bot.py"' >> ~/.bashrc

echo "Установка завершена. Перезапустите Termux, чтобы бот запускался автоматически."
