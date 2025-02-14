#!/data/data/com.termux/files/usr/bin/bash

# Завершаем процессы бота
pkill -9 python3
sleep 3

# Удаляем заблокированную сессию (если есть)
rm -f ~/.telethon.session

echo "-----------------------------------------"
echo "Обновляем пакеты..."
pkg update -y && pkg upgrade -y

echo "-----------------------------------------"
echo "Устанавливаем Python и Git..."
pkg install python git -y

echo "-----------------------------------------"
echo "Проверяем репозиторий..."
if [ ! -d "$HOME/rade" ]; then
    echo "Репозиторий не найден, клонируем..."
    git clone https://github.com/sdfasdgasdfwe3/rade.git ~/rade
else
    echo "Репозиторий найден, обновляем..."
    cd ~/rade || exit
    git pull
fi

# Переходим в директорию с ботом
cd ~/rade || { echo "Ошибка: не удалось перейти в директорию 'rade'"; exit 1; }

echo "-----------------------------------------"
echo "Устанавливаем зависимости Python..."
pip install -r requirements.txt

echo "-----------------------------------------"
echo "Запускаем бота..."
nohup python3 bot.py > ~/bot.log 2>&1 &

echo "Бот запущен в фоновом режиме."

