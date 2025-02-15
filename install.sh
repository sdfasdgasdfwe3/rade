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

        # Проверка на облачный пароль (Two-Step Verification)
        read -p "🔐 У вас включена двухфакторная аутентификация? (y/n): " HAS_2FA
        if [[ "$HAS_2FA" == "y" || "$HAS_2FA" == "Y" ]]; then
            read -p "🔐 Введите облачный пароль: " CLOUD_PASSWORD
        else
            CLOUD_PASSWORD=""
        fi
    else
        # Автоматический режим: используем переменные окружения
        API_ID=${API_ID:-""}
        API_HASH=${API_HASH:-""}
        PHONE_NUMBER=${PHONE_NUMBER:-""}
        CLOUD_PASSWORD=${CLOUD_PASSWORD:-""}

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
    "PHONE_NUMBER": "$PHONE_NUMBER",
    "CLOUD_PASSWORD": "$CLOUD_PASSWORD"
}
EOF
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
    setup_autostart
    
    echo -e "\nУстановка завершена! Бот будет автоматически запускаться при старте Termux."
    echo "Логи будут сохранены в ~/rade/bot.log"
}

# Запуск главной функции
main
