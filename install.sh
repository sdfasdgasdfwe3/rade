#!/bin/bash

error_exit() {
    echo "❌ Ошибка: $1"
    exit 1
}

echo "🔄 Обновление пакетов..."
pkg update -y && pkg upgrade -y || error_exit "Не удалось обновить пакеты."

echo "📦 Установка зависимостей..."
pkg install -y python git python-pip wget || error_exit "Не удалось установить зависимости."

echo "🐍 Создание виртуального окружения..."
python -m venv "$HOME/rade/venv" || error_exit "Ошибка при создании venv."
source "$HOME/rade/venv/bin/activate" || error_exit "Ошибка активации venv."

echo "🔧 Установка Telethon..."
pip install telethon || error_exit "Ошибка установки Telethon."

bot_dir="$HOME/rade"
mkdir -p "$bot_dir" || error_exit "Не удалось создать директорию."
cd "$bot_dir" || error_exit "Не удалось перейти в директорию."

echo "⬇️ Скачивание bot.py..."
wget -O bot.py https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py || error_exit "Ошибка загрузки bot.py."
[ ! -f bot.py ] && error_exit "Файл bot.py не найден."

if [ ! -f config.txt ]; then
    read -p "📝 Введите API_ID: " api_id
    read -p "📝 Введите API_HASH: " api_hash
    read -p "📞 Введите номер телефона: " phone
    cat > config.txt << EOL
API_ID=$api_id
API_HASH=$api_hash
PHONE_NUMBER=$phone
EOL
    echo "✅ Конфиг создан!"
fi

echo "🚀 Создание скрипта запуска..."
echo -e '#!/bin/bash\nsource venv/bin/activate\ncd ~/rade\npython3 bot.py' > start.sh
chmod +x start.sh || error_exit "Ошибка прав на start.sh."

echo "⚙️ Настройка автозапуска..."
echo -e '\n# Автозапуск бота\nif [ ! -f ~/rade/.bot_pid ]; then\n    cd ~/rade && ./start.sh\nfi' >> ~/.bashrc

echo "🎉 Установка завершена! Перезапустите Termux."
