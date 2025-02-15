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
    setup_autostart
    
    echo -e "\nУстановка завершена! Бот будет автоматически запускаться при старте Termux."
    echo "Логи будут сохранены в ~/rade/bot.log"
}

# Запуск главной функции
main
