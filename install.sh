#!/bin/bash

# Установка зависимостей для бота

# Проверка, установлен ли Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python 3 не установлен. Установите Python 3 и повторите попытку."
    exit 1
fi

# Проверка, установлен ли pip
if ! command -v pip3 &> /dev/null; then
    echo "pip3 не установлен. Установите pip3 и повторите попытку."
    exit 1
fi

# Скачивание и анализ зависимостей из кода бота
echo "Скачивание кода бота для анализа зависимостей..."
curl -fsSL https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py -o bot.py
if [ $? -ne 0 ]; then
    echo "Ошибка при скачивании кода бота."
    exit 1
fi

# Поиск импортов в коде бота
echo "Анализ зависимостей..."
DEPENDENCIES=($(grep -oP '^(?:from|import)\s+\K\w+' bot.py | sort -u))

# Установка зависимостей
echo "Установка зависимостей..."
for package in "${DEPENDENCIES[@]}"; do
    # Исключение стандартных библиотек Python
    if ! python3 -c "import $package" 2>/dev/null; then
        echo "Установка $package..."
        pip3 install "$package"
        if [ $? -ne 0 ]; then
            echo "Ошибка при установке $package."
            exit 1
        fi
    else
        echo "$package уже установлен (стандартная библиотека)."
    fi
done

# Очистка временных файлов
rm -f bot.py

echo "Все зависимости успешно установлены!"
