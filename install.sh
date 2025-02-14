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
pip install telethon requests

echo "-----------------------------------------"
echo "Делаем главный файл исполняемым..."
chmod +x bot.py

# Добавляем команду автозапуска бота в ~/.bashrc, если её там ещё нет
if ! grep -q "cd ~/rade && nohup python bot.py" ~/.bashrc; then
    echo 'if ! pgrep -f "python bot.py" > /dev/null; then' >> ~/.bashrc
    echo '    cd ~/rade && nohup python bot.py > /dev/null 2>&1 &' >> ~/.bashrc
    echo 'fi' >> ~/.bashrc
    echo "Команда автозапуска бота добавлена в ~/.bashrc"
fi

echo "-----------------------------------------"
echo "Запускаем бота..."
cd ~/rade
python bot.py
