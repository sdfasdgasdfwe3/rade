import asyncio  # Импортируем asyncio для работы с асинхронным кодом 
import subprocess
import os  # Добавлен импорт модуля os
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
    2: {'name': 'Текст с эффектом дождя', 'symbol': '.', 'speed': 0.15},  # Заменили на "Текст с эффектом дождя"
    3: {'name': 'Текст с эффектом пузырей', 'symbol': u'\u2588', 'speed': 0.05},  # Заменили на "Текст с эффектом пузырей"
    4: {'name': 'Текст с эффектом "письма"', 'symbol': '*', 'speed': DEFAULT_TYPING_SPEED},  # Заменили на "Текст с эффектом письма"
}

# Добавление функции для получения user_id
async def get_user_id():
    try:
        me = await client.get_me()
        print(f"Ваш user_id: {me.id}")  # Выводим user_id в консоль
    except Exception as e:
        print(f"Ошибка при получении user_id: {e}")

# Функция для отмены локальных изменений в git
def discard_local_changes():
    print("Отменить локальные изменения в файле bot.py.")
    try:
        print("Отмена локальных изменений в файле bot.py...")
        subprocess.run(['git', 'checkout', '--', 'bot.py'], check=True)
        print("Локальные изменения в файле bot.py были отменены.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при отмене изменений: {e}")

# Функция для проверки обновлений скрипта на GitHub
def check_for_updates():
    print("Проверка наличия обновлений скрипта на GitHub.")
    try:
        # Сначала отменяем локальные изменения
        discard_local_changes()

        # Теперь обновляем скрипт
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            remote_script = response.text
            current_file = os.path.abspath(__file__)

            with open(current_file, 'r', encoding='utf-8') as f:
                current_script = f.read()

            # Проверяем наличие строки SCRIPT_VERSION в обоих скриптах
            if str(SCRIPT_VERSION) in remote_script and str(SCRIPT_VERSION) in current_script:
                remote_version_line = [
                    line for line in remote_script.splitlines() if str(SCRIPT_VERSION) in line
                ]
                if remote_version_line:
                    remote_version = remote_version_line[0].split('=')[1].strip().strip('')
                    if str(SCRIPT_VERSION) != remote_version:
                        print(f"Доступна новая версия скрипта {remote_version} (текущая {SCRIPT_VERSION})")
                        with open(current_file, 'w', encoding='utf-8') as f:
                            f.write(remote_script)
                        print("Скрипт обновлен. Перезапустите программу.")
                        exit()
                    else:
                        print("У вас уже установлена последняя версия скрипта.")
                else:
                    print("Не удалось найти информацию о версии в загруженном скрипте.")
            else:
                print("Не удалось определить версии для сравнения.")
        else:
            print(f"Не удалось проверить обновления. Код ответа сервера {response.status_code}")
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {e}")

# Функция для настройки автозапуска
def setup_autostart():
    print("Функция для настройки автозапуска бота в Termux при старте устройства.")
    boot_directory = os.path.expanduser("~/.termux/boot")
    
    # Проверяем, существует ли папка для автозапуска
    if not os.path.exists(boot_directory):
        os.makedirs(boot_directory)
        print(f"Папка {boot_directory} создана.")
    
    # Путь к скрипту автозапуска
    script_path = os.path.join(boot_directory, 'start_bot.sh')
    
    # Путь к вашему скрипту бота
    bot_script_path = '/data/data/com.termux/files/home/rade/bot.py'  # Измените на актуальный путь
    
    # Создаем скрипт для автозапуска
    with open(script_path, 'w') as f:
        f.write(f"#!/data/data/com.termux/files/usr/bin/bash\n")
        f.write(f"cd /data/data/com.termux/files/home/rade  # Путь к вашему боту\n")
        f.write(f"python3 {bot_script_path}  # Запуск бота\n")
    
    # Даем права на исполнение скрипту
    os.chmod(script_path, 0o755)
    
    print(f"Автозапуск настроен. Скрипт сохранен в {script_path}.")

# Функция для удаления автозапуска
def remove_autostart():
    print("Функция для удаления автозапуска бота в Termux.")
    boot_directory = os.path.expanduser("~/.termux/boot")
    script_path = os.path.join(boot_directory, 'start_bot.sh')
    
    if os.path.exists(script_path):
        os.remove(script_path)
        print(f"Автозапуск удален. Скрипт {script_path} больше не будет запускаться при старте.")
    else:
        print("Скрипт автозапуска не найден. Возможно, он уже был удален.")

# Выводим инструкцию по отключению автозапуска
def print_autostart_instructions():
    print("Для отключения автозапуска скрипта бота выполните следующую команду в Termux: ")
    print("Удаление автозапуска:") 
    print("  python3 путь_к_скрипту bot.py --remove-autostart")
    print("Чтобы отключить автозапуск вручную, просто удалите файл: ")
    print("  rm ~/.termux/boot/start_bot.sh")

# Проверяем наличие файла конфигурации
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        API_ID = config.get("API_ID")
        API_HASH = config.get("API_HASH")
        PHONE_NUMBER = config.get("PHONE_NUMBER")
        typing_speed = config.get("typing_speed", DEFAULT_TYPING_SPEED)
        cursor_symbol = config.get("cursor_symbol", DEFAULT_CURSOR)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Ошибка чтения конфигурации {e}. Попробуем запросить данные заново.")
        API_ID = None
        API_HASH = None
        PHONE_NUMBER = None
else:
    # Если файл не существует, запрашиваем данные у пользователя
    API_ID = None
    API_HASH = None
    PHONE_NUMBER = None

if not API_ID or not API_HASH or not PHONE_NUMBER:
    try:
        print("Пожалуйста, введите данные для авторизации в Telegram.")
        API_ID = int(input("Введите ваш API ID: "))
        API_HASH = input("Введите ваш API Hash: ").strip()
        PHONE_NUMBER = input("Введите ваш номер телефона (в формате +7XXXXXXXXXX): ").strip()

        # Сохраняем данные в файл конфигурации
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "API_ID": API_ID,
                "API_HASH": API_HASH,
                "PHONE_NUMBER": PHONE_NUMBER,
                "typing_speed": DEFAULT_TYPING_SPEED,
                "cursor_symbol": DEFAULT_CURSOR
            }, f)
        print("Данные успешно сохранены в конфигурации.")
    except Exception as e:
        print(f"Ошибка сохранения конфигурации {e}")
        exit(1)

# Уникальное имя файла для сессии
SESSION_FILE = f'session_{PHONE_NUMBER.replace("+", "").replace("-", "")}'

# Инициализация клиента
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

# Функция для отображения меню выбора анимации
async def show_animation_menu(event):
    menu_text = "Меню анимаций:\n"
    for num, animation in animations.items():
        menu_text += f"{num}. {animation['name']}\n"
    menu_text += "Выберите номер анимации для изменения."

    await event.respond(menu_text)

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
@client.on(events.NewMessage(pattern=r'\d'))
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


# Обработчик команды анимации для текста
@client.on(events.NewMessage(pattern=r'р (.+)'))
async def animated_typing(event):
    print("Команда для печатания текста с анимацией.")
    global typing_speed, cursor_symbol
    try:
        if not event.out:
            return

        text = event.pattern_match.group(1)
        typed_text = ""

        for char in text:
            typed_text += char
            await event.edit(typed_text + cursor_symbol)
            await asyncio.sleep(typing_speed)

        await event.edit(typed_text)
    except Exception as e:
        print(f"Ошибка анимации: {e}")

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
