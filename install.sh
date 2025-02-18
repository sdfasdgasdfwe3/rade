#!/bin/bash

# Обновление пакетов
pkg update -y

# Установка зависимостей
pkg install -y git python

# Клонирование/обновление репозитория
if [ -d "rade" ]; then
    cd rade
    git pull
else
    git clone https://github.com/yourusername/rade.git
    cd rade
fi

# Установка Python-зависимостей
pip install --upgrade pyrogram tgcrypto requests

# Настройка автозапуска
if ! grep -q "AUTO-INSTALLED-COMMANDS" ~/.bashrc; then
    echo '' >> ~/.bashrc
    echo '# AUTO-INSTALLED-COMMANDS' >> ~/.bashrc
    echo 'if [ -d "$HOME/rade" ]; then' >> ~/.bashrc
    echo '    cd "$HOME/rade"' >> ~/.bashrc
    echo '    echo "======================"' >> ~/.bashrc
    echo '    echo "Для запуска бота введите:"' >> ~/.bashrc 
    echo '    echo "python bot.py"' >> ~/.bashrc
    echo '    echo "======================"' >> ~/.bashrc
    echo 'fi' >> ~/.bashrc
fi

# Создание конфига при первом запуске
if [ ! -f "config.ini" ]; then
    touch config.ini
fi

echo "Установка завершена!"
echo "Перезапустите Termux или выполните:"
echo "source ~/.bashrc"
