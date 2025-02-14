#!/bin/bash

# =============================================
# Настройки
# =============================================
REPO_URL="https://github.com/sdfasdgasdfwe3/rade.git"
REPO_DIR="$HOME/rade"
SESSION_NAME="bot_session"
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
# Установка tmux, если он отсутствует
# =============================================
install_tmux() {
    if ! command -v tmux &>/dev/null; then
        echo "Устанавливаем tmux..."
        pkg install tmux -y || error_exit "Ошибка установки tmux"
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
# Настройка автозапуска через termux-boot
# =============================================
setup_autostart() {
    local boot_script="$HOME/.termux/boot/start_bot"
    
    echo "Настраиваем автозапуск через termux-boot..."
    mkdir -p ~/.termux/boot
    echo '#!/data/data/com.termux/files/usr/bin/sh
tmux new-session -d -s bot_session "python3 ~/rade/bot.py"' > "$boot_script"
    chmod +x "$boot_script"
    echo "Автозапуск настроен через termux-boot."
}

# =============================================
# Главный процесс выполнения
# =============================================
main() {
    install_git  # Устанавливаем git, если он отсутствует
    install_tmux  # Устанавливаем tmux, если он отсутствует
    install_deps
    setup_repo
    setup_autostart
    
    echo -e "\nУстановка завершена! Бот будет автоматически запускаться при старте Termux."
    echo "Для подключения к сессии используйте: tmux attach -t bot_session"
}

# Запуск главной функции
main
