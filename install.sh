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

# Список зависимостей
DEPENDENCIES=(
    "telethon"
    "requests"
    "psutil"
)

# Установка зависимостей
echo "Установка зависимостей..."
for package in "${DEPENDENCIES[@]}"; do
    echo "Установка $package..."
    pip3 install "$package"
    if [ $? -ne 0 ]; then
        echo "Ошибка при установке $package."
        exit 1
    fi
done

echo "Все зависимости успешно установлены!"
