#!/bin/bash

# =============================================
# Настройки
# =============================================
REPO_URL="https://github.com/sdfasdgasdfwe3/rade.git"
REPO_DIR="$HOME/rade"
SCRIPT_NAME=$(basename "$0")

# =============================================
# Функции для обработки ошибок
# =============================================
error_exit() {
    echo "ОШИБКА: $1" >&2
    exit 1
}

# =============================================
# Установка git, если он отсутствует
# =============================================
install_git() {
    if ! command -v git &>/dev/null; then
        echo "Устанавливаем git..."
        pkg install git -y || error_exit "Ошибка установки git"
    fi
}

# =============================================
# Проверка и установка зависимостей
# =============================================
install_deps() {
    # Проверка Python
    if ! command -v python3 &>/dev/null; then
        echo "Устанавливаем Python3..."
        pkg install python -y || error_exit "Ошибка установки Python"
    fi

    # Проверка pip
    if ! command -v pip3 &>/dev/null; then
        echo "Устанавливаем pip..."
        python3 -m ensurepip --upgrade || error_exit "Ошибка установки pip"
    fi

    # Установка базовых зависимостей
    echo "Устанавливаем зависимости..."
    pip3 install -U requests telethon psutil || error_exit "Ошибка установки зависимостей"
}

# =============================================
# Работа с репозиторием
# =============================================
setup_repo() {
    if [ -d "$REPO_DIR/.git" ]; then
        echo "Обновляем репозиторий..."
        cd "$REPO_DIR" && git pull || error_exit "Ошибка обновления репозитория"
    else
        echo "Клонируем репозиторий..."
        git clone "$REPO_URL" "$REPO_DIR" || error_exit "Ошибка клонирования"
        cd "$REPO_DIR" || error_exit "Ошибка перехода в директорию"
    fi
}

# =============================================
# Запрос данных для авторизации
# =============================================
get_auth_data() {
    if [ -t 0 ]; then
        # Интерактивный режим: запрашиваем данные у пользователя
        echo "🔑 Необходима авторизация. Введите данные от Telegram:"
        read -p "🔑 Введите API ID: " API_ID
        read -p "🔑 Введите API HASH: " API_HASH
        read -p "📱 Введите номер телефона (формат +79991234567): " PHONE_NUMBER
    else
        # Автоматический режим: используем переменные окружения
        API_ID=${API_ID:-""}
        API_HASH=${API_HASH:-""}
        PHONE_NUMBER=${PHONE_NUMBER:-""}

        if [ -z "$API_ID" ] || [ -z "$API_HASH" ] || [ -z "$PHONE_NUMBER" ]; then
            error_exit "Переменные окружения API_ID, API_HASH и PHONE_NUMBER не установлены."
        fi
    fi

    # Сохраняем данные в config.json
    echo "Создаем config.json..."
    cat > "$REPO_DIR/config.json" <<EOF
{
    "API_ID": "$API_ID",
    "API_HASH": "$API_HASH",
    "PHONE_NUMBER": "$PHONE_NUMBER"
}
EOF
}

# =============================================
# Автоматическая проверка на облачный пароль
# =============================================
check_cloud_password() {
    echo "Проверяем наличие облачного пароля..."

    # Создаем временный Python-скрипт для проверки
    cat > "$REPO_DIR/check_2fa.py" <<EOF
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import json

with open("config.json", "r") as f:
    config = json.load(f)

client = TelegramClient("session_name", config["API_ID"], config["API_HASH"])

async def main():
    try:
        await client.start(phone=config["PHONE_NUMBER"])
        print("Облачный пароль не требуется.")
    except SessionPasswordNeededError:
        print("Облачный пароль требуется.")
    finally:
        await client.disconnect()

with client:
    client.loop.run_until_complete(main())
EOF

    # Запускаем проверку
    CLOUD_PASSWORD_REQUIRED=$(python3 "$REPO_DIR/check_2fa.py" | grep "Облачный пароль требуется")

    if [ -n "$CLOUD_PASSWORD_REQUIRED" ]; then
        read -p "🔐 Введите облачный пароль: " CLOUD_PASSWORD
        echo "Добавляем облачный пароль в config.json..."
        jq --arg password "$CLOUD_PASSWORD" '. + {CLOUD_PASSWORD: $password}' "$REPO_DIR/config.json" > "$REPO_DIR/config.tmp.json"
        mv "$REPO_DIR/config.tmp.json" "$REPO_DIR/config.json"
    else
        echo "Облачный пароль не требуется."
    fi

    # Удаляем временный скрипт
    rm "$REPO_DIR/check_2fa.py"
}

# =============================================
# Настройка автозапуска через ~/.bashrc
# =============================================
setup_autostart() {
    local autostart_cmd="nohup python3 ~/rade/bot.py > ~/rade/bot.log 2>&1 &"
    
    # Добавляем команду в ~/.bashrc, если её там нет
    if ! grep -qF "$autostart_cmd" ~/.bashrc; then
        echo "Добавляем автозапуск в .bashrc..."
        echo -e "\n# Telegram bot autostart\n$autostart_cmd" >> ~/.bashrc
    else
        echo "Автозапуск уже настроен"
    fi
}

# =============================================
# Главный процесс выполнения
# =============================================
main() {
    install_git  # Устанавливаем git, если он отсутствует
    install_deps
    setup_repo
    get_auth_data
    check_cloud_password
    setup_autostart
    
    echo -e "\nУстановка завершена! Бот будет автоматически запускаться при старте Termux."
    echo "Логи будут сохранены в ~/rade/bot.log"
}

# Запуск главной функции
main
