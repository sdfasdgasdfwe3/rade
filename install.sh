#!/data/data/com.termux/files/usr/bin/bash
# install.sh — автоматическая установка и запуск бота в Termux

echo "-----------------------------------------"
echo "Обновляем пакеты..."
pkg update -y && pkg upgrade -y

echo "-----------------------------------------"
echo "Проверяем установку Python..."
if ! command -v python &>/dev/null; then
  echo "Python не установлен. Устанавливаем..."
  pkg install python -y
else
  echo "Python уже установлен."
fi

echo "-----------------------------------------"
echo "Проверяем установку Git..."
if ! command -v git &>/dev/null; then
  echo "Git не установлен. Устанавливаем..."
  pkg install git -y
else
  echo "Git уже установлен."
fi

# Путь к файлу сессии
SESSION_FILE="session_$(cat config.json | jq -r '.PHONE_NUMBER' | sed 's/+/ /g').session"

echo "-----------------------------------------"
echo "Проверяем наличие файла сессии..."

# Проверка существования и содержимого файла сессии
if [ -f "$SESSION_FILE" ]; then
    if [ ! -s "$SESSION_FILE" ]; then
        echo "Файл сессии пустой. Он будет перезаписан при следующем запуске бота."
    else
        echo "Сессия найдена. Создаём резервную копию..."
        cp "$SESSION_FILE" "${SESSION_FILE}.backup"
        echo "Резервная копия сессии создана: ${SESSION_FILE}.backup"
    fi
else
    echo "Сессия не найдена. Резервная копия не требуется."
fi

echo "-----------------------------------------"
echo "Удаляем старую версию репозитория (если есть)..."
rm -rf rade

echo "-----------------------------------------"
echo "Клонируем репозиторий..."
git clone https://github.com/sdfasdgasdfwe3/rade.git

# Переходим в директорию репозитория
cd rade || { echo "Ошибка: не удалось перейти в директорию 'rade'"; exit 1; }

echo "-----------------------------------------"
echo "Проверяем установленные зависимости..."
if ! pip show telethon &>/dev/null || ! pip show requests &>/dev/null || ! pip show psutil &>/dev/null; then
  echo "Зависимости не установлены. Устанавливаем..."
  pip install telethon requests psutil
else
  echo "Все зависимости уже установлены."
fi

echo "-----------------------------------------"
echo "Возвращаем резервную копию сессии, если она была создана..."
if [ -f "${SESSION_FILE}.backup" ]; then
    cp "${SESSION_FILE}.backup" "$SESSION_FILE"
    echo "Резервная копия сессии восстановлена."
else
    echo "Резервная копия не найдена. Создайте новую сессию при первом запуске."
fi

echo "-----------------------------------------"
echo "Запускаем бота..."
# Просто запускаем бота
python bot.py

# Добавляем автозапуск в .bashrc
echo "-----------------------------------------"
echo "Настроим автозапуск бота при следующем открытии Termux..."
echo "bash /data/data/com.termux/files/home/rade/install.sh" >> ~/.bashrc

echo "Автозапуск настроен. Теперь при следующем запуске терминала скрипт будет запускаться автоматически."
