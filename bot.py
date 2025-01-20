import asyncio
import subprocess
import os
import requests
import json
from telethon import TelegramClient, events

# Константы
CONFIG_FILE = 'config.json'
GITHUB_RAW_URL = 'https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py'  # Исправленный URL
SCRIPT_VERSION = 0.1
DEFAULT_TYPING_SPEED = 0.3
DEFAULT_CURSOR = u'\u2588'  # Символ по умолчанию для анимации

# Список доступных анимаций
animations = {
    1: {'name': 'Стандартная анимация', 'symbol': u'\u2588', 'speed': DEFAULT_TYPING_SPEED},
    2: {'name': 'Текст с эффектом дождя', 'symbol': '.', 'speed': 0.15},
    3: {'name': 'Текст с эффектом пузырей', 'symbol': u'\u2588', 'speed': 0.05},
    4: {'name': 'Текст с эффектом "письма"', 'symbol': '*', 'speed': DEFAULT_TYPING_SPEED},
}

# Добавление функции для получения user_id
async def get_user_id():
    try:
        me = await client.get_me()
        print(f"Ваш user_id: {me.id}")  # Выводим user_id в консоль
    except Exception as e:
        print(f"Ошибка при получении user_id: {e}")

# Функция для настройки автозапуска
def setup_autostart():
    # (весь код без изменений)
    pass

# Все другие функции без изменений...

# Инициализация клиента
client = TelegramClient('session', API_ID, API_HASH)

# Обработчик команды Меню
@client.on(events.NewMessage(pattern=r'Меню'))
async def menu_handler(event):
    try:
        # Показываем меню анимаций
        menu_message = await show_animation_menu(event)
        
        # Удаляем сообщение "Меню" после его отображения
        await event.delete()

    except Exception as e:
        print(f"Ошибка при выводе меню: {e}")

# Функция для отображения меню выбора анимации
async def show_animation_menu(event):
    menu_text = "Меню анимаций:\n"
    for num, animation in animations.items():
        menu_text += f"{num}. {animation['name']}\n"
    menu_text += "Выберите номер анимации для изменения."

    # Отправляем меню и сохраняем ID сообщения
    menu_message = await event.respond(menu_text)
    return menu_message  # Возвращаем объект сообщения с меню

# Обработчик для выбора анимации по номеру
@client.on(events.NewMessage(pattern=r'\\d'))
async def change_animation(event):
    try:
        # Получаем номер выбранной анимации
        choice = int(event.text.strip())
        if choice in animations:
            global cursor_symbol, typing_speed
            selected_animation = animations[choice]
            cursor_symbol = selected_animation['symbol']
            typing_speed = selected_animation['speed']

            # Сохраняем выбранную анимацию в конфигурации
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "API_ID": API_ID,
                    "API_HASH": API_HASH,
                    "PHONE_NUMBER": PHONE_NUMBER,
                    "typing_speed": typing_speed,
                    "cursor_symbol": cursor_symbol
                }, f)

            # Отправляем сообщение, подтверждающее выбор анимации
            confirmation_message = await event.respond(f"Вы выбрали анимацию: {selected_animation['name']}")

            # Удаляем сообщение с выбором анимации
            await event.delete()

            # Удаляем меню анимаций через 1 секунду (чтобы дать время на прочтение)
            await asyncio.sleep(1)
            await confirmation_message.delete()

        else:
            await event.respond("Неверный выбор. Пожалуйста, выберите номер из списка.")
    except Exception as e:
        print(f"Ошибка при изменении анимации: {e}")

# Функция для отображения справки
async def show_help(event):
    help_text = (
        "Доступные команды:\n"
        "Меню - отобразить меню анимаций.\n"
        "р <текст> - показать текст с анимацией.\n"
        "\\d - выбрать номер анимации из меню.\n"
    )
    await event.respond(help_text)

@client.on(events.NewMessage(pattern=r'Помощь'))
async def help_handler(event):
    await show_help(event)

async def main():
    print(f"Запуск main()... Версия скрипта {SCRIPT_VERSION}")
    
    # Настроим автозапуск
    setup_autostart()
    
    check_for_updates()
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Вы авторизованы в Telegram.")
    print("Для использования анимации текста используйте команду р ваш текст.")
    
    # Печатаем инструкции по отключению автозапуска после старта бота
    print_autostart_instructions()

    # Получаем user_id
    await get_user_id()
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    check_for_updates()
    asyncio.run(main())  # Теперь asyncio импортирован и main() может быть вызван
