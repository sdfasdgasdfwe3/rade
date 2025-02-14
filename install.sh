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
# Настройка tmux
# =============================================
setup_tmux() {
    echo "Проверка tmux сессии..."
    if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        echo "Запускаем бота в новой сессии..."
        tmux new-session -d -s "$SESSION_NAME" "python3 $REPO_DIR/bot.py" || error_exit "Ошибка запуска tmux"
        sleep 2
    else
        echo "Сессия tmux уже запущена."
    fi

    # Проверка жизнеспособности сессии
    if ! tmux list-sessions | grep -q "$SESSION_NAME"; then
        error_exit "Сессия tmux не запустилась"
    fi
}

# =============================================
# Настройка автозапуска
# =============================================
setup_autostart() {
    local autostart_cmd="tmux has-session -t $SESSION_NAME 2>/dev/null || tmux new-session -d -s $SESSION_NAME 'python3 $REPO_DIR/bot.py'"
    
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
    setup_tmux
    setup_autostart
    
    echo -e "\nУстановка завершена! Состояние бота:"
    tmux list-sessions | grep "$SESSION_NAME"
    echo "Для подключения используйте: tmux attach -t $SESSION_NAME"
}

# Запуск главной функции
main
