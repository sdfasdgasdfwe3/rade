#!/bin/bash

# =============================================
# Настройки
# =============================================
REPO_URL="https://github.com/sdfasdgasdfwe3/rade.git"
REPO_DIR="$HOME/rade"
SESSION_NAME="bot_session"
LOCK_FILE="/tmp/bot.lock"
SCRIPT_NAME=$(basename "$0")

# =============================================
# Функции для обработки ошибок
# =============================================
error_exit() {
    echo "ОШИБКА: $1" >&2
    rm -f "$LOCK_FILE"
    exit 1
}

# =============================================
# Проверка блокировки и создание lock-файла
# =============================================
if [ -e "$LOCK_FILE" ]; then
    error_exit "Скрипт уже запущен! (обнаружен lock-файл)"
fi
touch "$LOCK_FILE" || error_exit "Не могу создать lock-файл"

# Очистка lock-файла при выходе
trap 'rm -f "$LOCK_FILE"' EXIT

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

    # Установка зависимостей из requirements.txt
    if [ -f "requirements.txt" ]; then
        pip3 install -U -r requirements.txt || echo "Предупреждение: проблемы с requirements.txt"
    fi
}

# =============================================
# Управление процессами
# =============================================
check_running() {
    # Поиск существующих процессов бота
    if pgrep -f "python3.*bot\.py" >/dev/null; then
        error_exit "Бот уже запущен! (обнаружен running process)"
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
    install_deps
    check_running
    setup_repo
    setup_tmux
    setup_autostart
    
    echo -e "\nУстановка завершена! Состояние бота:"
    tmux list-sessions | grep "$SESSION_NAME"
    echo "Для подключения используйте: tmux attach -t $SESSION_NAME"
}

# Запуск главной функции
main
