#!/data/data/com.termux/files/usr/bin/bash

# Завершаем все процессы Python перед запуском бота
kill -9 $(ps aux | grep '[p]ython' | awk '{print $2}')

# Ждем, пока база данных освободится
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
pip3 install telethon requests aiohttp

echo "-----------------------------------------"
echo "Делаем главный файл исполняемым..."
chmod +x bot.py

echo "-----------------------------------------"
echo "Создаем .bashrc, если его нет, и добавляем автозапуск..."
touch ~/.bashrc
echo 'cd ~/rade && git pull && python3 bot.py' >> ~/.bashrc

# Обновляем cron для автоматического перезапуска (если нужно)
crontab -l | { cat; echo "@reboot cd ~/rade && git pull && python3 bot.py"; } | crontab -

echo "Установка завершена. Перезапустите Termux, чтобы бот запускался автоматически."
