#!/bin/bash

# Логирование установки
log_file="install.log"
exec > >(tee -a "$log_file") 2>&1

error_exit() {
    echo "Ошибка: $1"
    exit 1
}

echo "Обновление пакетов..."
pkg update -y && pkg upgrade -y || error_exit "Не удалось обновить пакеты."

echo "Установка зависимостей..."
pkg install -y python git python-pip wget || error_exit "Не удалось установить зависимости."

echo "Создание виртуального окружения..."
python -m venv "$HOME/rade/venv" || error_exit "Ошибка при создании venv."
source "$HOME/rade/venv/bin/activate" || error_exit "Ошибка активации venv."

echo "Установка Telethon..."
pip install telethon || error_exit "Ошибка установки Telethon."

bot_dir="$HOME/rade"
mkdir -p "$bot_dir" || error_exit "Не удалось создать директорию."
cd "$bot_dir" || error_exit "Не удалось перейти в директорию."

echo "Скачивание bot.py..."
wget -O bot.py https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py || error_exit "Ошибка загрузки bot.py."
[ ! -f bot.py ] && error_exit "Файл bot.py не найден."

if [ ! -f config.txt ]; then
    read -p "Введите API_ID: " api_id
    read -p "Введите API_HASH: " api_hash
    read -p "Введите номер телефона: " phone
    cat > config.txt << EOL
API_ID=$api_id
API_HASH=$api_hash
PHONE_NUMBER=$phone
EOL
fi

echo "Создание скрипта запуска..."
echo -e '#!/bin/bash\nsource venv/bin/activate\npython3 bot.py' > start.sh
chmod +x start.sh || error_exit "Ошибка прав на start.sh."

echo "Запуск бота..."
echo "При первом запуске введите код подтверждения из Telegram."
nohup ./start.sh > bot.log 2>&1 &
echo "Бот запущен в фоне. Логи: bot.log."
