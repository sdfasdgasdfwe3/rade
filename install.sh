#!/data/data/com.termux/files/usr/bin/bash

# Включаем режим немедленного выхода при ошибках
set -e

# Функция для обработки ошибок
handle_error() {
    echo "Произошла ошибка в строке $1. Прерывание выполнения."
    exit 1
}

trap 'handle_error $LINENO' ERR

# Завершаем только процессы бота, игнорируя ошибки если процессов нет
echo "-----------------------------------------"
echo "Останавливаем предыдущие запуски бота..."
pkill -f "python3 bot.py" || true

# Короткая пауза вместо 5 секунд (можно настроить при необходимости)
echo "Ожидаем 2 секунды..."
sleep 2

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
echo "Удаляем старую версию репозитория..."
rm -rf rade

echo "-----------------------------------------"
echo "Клонируем репозиторий..."
git clone https://github.com/sdfasdgasdfwe3/rade.git

# Переходим в директорию репозитория
cd rade

echo "-----------------------------------------"
echo "Обновляем pip..."
pip install --upgrade pip

echo "-----------------------------------------"
echo "Устанавливаем зависимости Python..."
pip install telethon requests

echo "-----------------------------------------"
echo "Делаем главный файл исполняемым..."
chmod +x bot.py

echo "-----------------------------------------"
echo "Настраиваем автозапуск..."
BASHRC=~/.bashrc
AUTOSTART_CMD='cd ~/rade && git pull -q && python3 bot.py'

# Проверяем, не добавлена ли уже команда
if ! grep -Fxq "$AUTOSTART_CMD" "$BASHRC"; then
    echo "$AUTOSTART_CMD" >> "$BASHRC"
    echo "Автозапуск добавлен в .bashrc"
else
    echo "Автозапуск уже настроен"
fi

echo "-----------------------------------------"
echo "Запускаем бота..."
python3 bot.py &

echo "Установка успешно завершена!"
echo "Для ручного запуска: cd ~/rade && python3 bot.py"
echo "Перезапустите Termux или выполните: source ~/.bashrc"
