#!/data/data/com.termux/files/usr/bin/bash

# =============================================
# Настройки
# =============================================
REPO_URL="https://github.com/sdfasdgasdfwe3/rade.git"
REPO_DIR="$HOME/rade"
SCRIPT_NAME=$(basename "$0")
LOCK_FILE="$REPO_DIR/bot.lock"

# Зависимости Python
PYTHON_DEPS="requests telethon psutil"

# =============================================
# Функции для обработки ошибок
# =============================================
error_exit() {
    echo "ОШИБКА: $1" >&2
    exit 1
}

# =============================================
# Обновление пакетов
# =============================================
update_packages() {
    echo "-----------------------------------------"
    echo "Обновляем пакеты..."
    pkg update -y && pkg upgrade -y || error_exit "Ошибка обновления пакетов"
}

# =============================================
# Установка git и Python
# =============================================
install_git_python() {
    echo "-----------------------------------------"
    echo "Устанавливаем Python и Git..."
    pkg install python git -y || error_exit "Ошибка установки Python или Git"
}

# =============================================
# Работа с репозиторием
# =============================================
setup_repo() {
    echo "-----------------------------------------"
    echo "Удаляем старую версию репозитория (если есть), но сохраняем config.json..."
    if [ -d "$REPO_DIR" ]; then
        mv "$REPO_DIR/config.json" "$HOME/config_backup.json" 2>/dev/null
        rm -rf "$REPO_DIR"
    fi

    echo "-----------------------------------------"
    echo "Клонируем репозиторий..."
    git clone "$REPO_URL" "$REPO_DIR" || error_exit "Ошибка клонирования репозитория"

    echo "-----------------------------------------"
    echo "Восстанавливаем config.json, если он был..."
    if [ -f "$HOME/config_backup.json" ]; then
        mv "$HOME/config_backup.json" "$REPO_DIR/config.json"
    fi
}

# =============================================
# Установка зависимостей Python
# =============================================
install_python_deps() {
    echo "-----------------------------------------"
    echo "Создаем виртуальное окружение и устанавливаем зависимости..."
    cd "$REPO_DIR" || error_exit "Ошибка перехода в директорию репозитория"
    
    # Создаем виртуальное окружение
    python -m venv venv || error_exit "Ошибка создания виртуального окружения"
    
    # Активируем виртуальное окружение
    source venv/bin/activate || error_exit "Ошибка активации виртуального окружения"
    
    # Обновляем pip (если нужно)
    pip install --upgrade pip || error_exit "Ошибка обновления pip"
    
    # Устанавливаем зависимости
    echo "Устанавливаем зависимости: $PYTHON_DEPS"
    for dep in $PYTHON_DEPS; do
        pip install "$dep" || error_exit "Ошибка установки зависимости: $dep"
    done
}

# =============================================
# Настройка автозапуска
# =============================================
setup_autostart() {
    echo "-----------------------------------------"
    echo "Настраиваем автозапуск..."
    if ! grep -q "cd ~/rade && source venv/bin/activate && git pull && python bot.py" ~/.bashrc; then
        echo 'cd ~/rade && source venv/bin/activate && git pull && python bot.py' >> ~/.bashrc
    fi
    echo "Автозапуск настроен."
}

# =============================================
# Завершение бота при выходе из Termux
# =============================================
setup_exit_hook() {
    echo "-----------------------------------------"
    echo "Настраиваем завершение бота при выходе из Termux..."
    if ! grep -q "pkill -f 'python.*bot.py'" ~/.bashrc; then
        echo 'trap "pkill -f \"python.*bot.py\"" EXIT' >> ~/.bashrc
    fi
    echo "Хук завершения настроен."
}

# =============================================
# Главный процесс выполнения
# =============================================
main() {
    update_packages
    install_git_python
    setup_repo
    install_python_deps
    setup_autostart
    setup_exit_hook

    echo "-----------------------------------------"
    echo "Установка завершена. Перезапустите Termux, чтобы бот запускался автоматически."
}

# Запуск главной функции
main
