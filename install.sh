#!/bin/bash
set -e
echo "🔄 Обновление списка пакетов..."
apt-get update -qq

echo "📦 Установка системных зависимостей..."
apt-get install -y -qq python3-dev python3-pip > /dev/null

echo "⚙️ Обновление pip..."
pip3 install --upgrade --quiet pip > /dev/null

echo "📦 Установка Python-пакетов..."
pip3 install --quiet telethon psutil requests > /dev/null

echo "✅ Все зависимости успешно установлены!"
