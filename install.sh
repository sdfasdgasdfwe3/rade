error_exit() {
    echo "❌ Ошибка: $1"
    exit 1
}

echo "🔄 Обновление Termux..."
pkg update -y && pkg upgrade -y || error_exit "Не удалось обновить Termux."

echo "📦 Установка системных пакетов..."
pkg install -y python wget git || error_exit "Не удалось установить системные пакеты."

echo "🐍 Создание виртуального окружения..."
python -m venv "$HOME/rade/venv" || error_exit "Ошибка создания venv."
source "$HOME/rade/venv/bin/activate" || error_exit "Ошибка активации venv."

echo "🔧 Установка Python-библиотек..."
pip install telethon requests psutil || error_exit "Ошибка установки библиотек."

bot_dir="$HOME/rade"
mkdir -p "$bot_dir" || error_exit "Не удалось создать директорию."
cd "$bot_dir" || error_exit "Не удалось перейти в директорию."

echo "⬇️ Скачивание файлов..."
wget -O bot.py https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py
wget -O animation_script.py https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/animation_script.py

[ ! -f bot.py ] && error_exit "Файл bot.py не найден."
[ ! -f animation_script.py ] && error_exit "Файл animation_script.py не найден."

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
