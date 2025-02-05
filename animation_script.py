import os
import sys
import asyncio
import subprocess
from telethon import TelegramClient, events
from configparser import ConfigParser

CONFIG_FILE = 'config.ini'
SESSION_FILE = 'session_name'
CHOICE_FILE = 'animation_choice.txt'

# Доступные анимации (можно добавить или изменить варианты)
AVAILABLE_ANIMATIONS = {
    "1": {"name": "Медленный набор текста", "typing_speed": 0.3, "cursor_symbol": "|"},
    "2": {"name": "Быстрый набор текста", "typing_speed": 0.1, "cursor_symbol": "_"},
}

def create_or_read_config():
    config = ConfigParser()
    config.read(CONFIG_FILE)
    if not config.has_section('Telegram'):
        print("❌ Отсутствует секция [Telegram] в конфиге!")
        sys.exit(1)
    return config['Telegram']

async def main():
    config = create_or_read_config()
    client = TelegramClient(SESSION_FILE, int(config['api_id']), config['api_hash'])
    await client.start(phone=lambda: config['phone_number'])
    
    # Получаем свои данные, чтобы отправить сообщение самому себе
    me = await client.get_me()
    
    # Формируем текст со списком доступных анимаций
    animations_text = "Выберите анимацию, отправив номер:\n"
    for num, data in AVAILABLE_ANIMATIONS.items():
        animations_text += f"{num}: {data['name']}\n"
    animations_text += "\nОтправьте сообщение с номером выбранной анимации."
    
    # Отправляем сообщение себе в личные сообщения
    await client.send_message(me, animations_text)
    print("Список анимаций отправлен. Ожидание выбора...")

    # Обработчик входящих сообщений – ждем, пока пользователь отправит корректный номер
    @client.on(events.NewMessage(incoming=True))
    async def selection_handler(event):
        text = event.raw_text.strip()
        if text in AVAILABLE_ANIMATIONS:
            # Сохраняем выбор в файл
            with open(CHOICE_FILE, 'w', encoding='utf-8') as f:
                f.write(text)
            await event.reply(f"Вы выбрали анимацию: {AVAILABLE_ANIMATIONS[text]['name']}\nЗапускаю основной бот...")
            # Завершаем работу клиента выбора анимации
            await client.disconnect()
            # Запускаем основной бот (bot.py)
            subprocess.Popen([sys.executable, "bot.py"])
            sys.exit(0)
        else:
            await event.reply("Неверный выбор. Пожалуйста, отправьте номер из списка.")

    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Скрипт выбора анимации завершён пользователем.")
