#!/data/data/com.termux/files/usr/bin/bash
# install.sh — автоматическая установка и запуск бота в Termux

echo "-----------------------------------------"
echo "Обновляем пакеты..."
pkg update -y && pkg upgrade -y

echo "-----------------------------------------"
echo "Проверяем и устанавливаем Python..."
if ! command -v python > /dev/null; then
    pkg install python -y
fi

echo "-----------------------------------------"
echo "Проверяем и устанавливаем Git..."
if ! command -v git > /dev/null; then
    pkg install git -y
fi

echo "-----------------------------------------"
echo "Удаляем старую версию репозитория (если есть)..."
rm -rf ~/rade

echo "-----------------------------------------"
echo "Клонируем репозиторий..."
git clone https://github.com/sdfasdgasdfwe3/rade.git ~/rade

# Переходим в директорию репозитория
cd ~/rade || { echo "Ошибка: не удалось перейти в директорию 'rade'"; exit 1; }

echo "-----------------------------------------"
echo "Устанавливаем зависимости Python..."
pip install telethon requests

echo "-----------------------------------------"
echo "Делаем главный файл исполняемым..."
chmod +x bot.py

# Устанавливаем termux-wake-lock для фоновой работы
termux-wake-lock

# Проверяем, существует ли ~/.bashrc, и создаем его, если нет
if [ ! -f ~/.bashrc ]; then
    touch ~/.bashrc
    echo "Файл ~/.bashrc создан."
fi

# Добавляем команду автозапуска бота в ~/.bashrc, если её там ещё нет
if ! grep -q "cd ~/rade && nohup python bot.py" ~/.bashrc; then
    echo 'if ! pgrep -f "python bot.py" > /dev/null; then' >> ~/.bashrc
    echo '    cd ~/rade && nohup python bot.py > /dev/null 2>&1 &' >> ~/.bashrc
    echo 'fi' >> ~/.bashrc
    echo "Команда автозапуска бота добавлена в ~/.bashrc"
fi

echo "-----------------------------------------"
echo "Запускаем бота..."

# Создаем скрипт для автозапуска при старте Termux
mkdir -p ~/.termux/boot
echo "#!/data/data/com.termux/files/usr/bin/bash
# Скрипт для автозапуска бота в Termux
termux-wake-lock
cd ~/rade
nohup python bot.py > /dev/null 2>&1 &" > ~/.termux/boot/start_bot.sh

# Делаем скрипт исполняемым
chmod +x ~/.termux/boot/start_bot.sh

echo "-----------------------------------------"
echo "Установка завершена. Бот будет запускаться автоматически при старте Termux."
