import os
import re
import sys
import asyncio
import aiohttp
import subprocess
import shutil
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from configparser import ConfigParser

VERSION = "2.5"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3/rade/main/bot.py"
GITHUB_ANIMATION_URL = "https://raw.githubusercontent.com/yourusername/yourrepo/main/animation_script.py"  # Замените на актуальный URL
CONFIG_FILE = 'config.ini'
SESSION_FILE = 'session_name'
CHOICE_FILE = 'animation_choice.txt'
ANIMATION_FILE = "animation_script.py"

# Словарь с настройками доступных анимаций
AVAILABLE_ANIMATIONS = {
    "1": {"name": "Медленный набор текста", "typing_speed": 0.3, "cursor_symbol": "|"},
    "2": {"name": "Быстрый набор текста", "typing_speed": 0.1, "cursor_symbol": "_"},
    # Можно добавить другие варианты
}

# Если пользователь ранее выбирал анимацию, читаем её из файла, иначе – используем вариант "1"
if os.path.exists(CHOICE_FILE):
    with open(CHOICE_FILE, 'r', encoding='utf-8') as f:
        chosen = f.read().strip()
else:
    chosen = "1"  # значение по умолчанию

animation_settings = AVAILABLE_ANIMATIONS.get(chosen, AVAILABLE_ANIMATIONS["1"])


def get_input(prompt, validation_regex=None, error_message="Неверный формат!"):
    while True:
        value = input(prompt).strip()
        if not value:
            print("⚠️ Это поле обязательно для заполнения!")
            continue
        if validation_regex and not re.match(validation_regex, value):
            print(f"⚠️ {error_message}")
            continue
        return value


def create_or_read_config():
    config = ConfigParser()
    
    if not os.path.exists(CONFIG_FILE):
        print("\n🔧 Первоначальная настройка бота:")
        
        api_id = get_input(
            "Введите API ID: ",
            r'^\d+$',
            "API ID должен состоять только из цифр!"
        )
        
        api_hash = get_input(
            "Введите API HASH: ",
            r'^[a-f0-9]{32}$',
            "API HASH должен содержать 32 символа (a-f, 0-9)!"
        )
        
        phone_number = get_input(
            "Введите номер телефона: ",
            r'^\+\d{10,15}$',
            "Номер должен быть в международном формате!"
        )
        
        config['Telegram'] = {
            'api_id': api_id,
            'api_hash': api_hash,
            'phone_number': phone_number
        }
        
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
            
        print("\n✅ Конфигурация сохранена в config.ini")
    
    config.read(CONFIG_FILE)
    if not config.has_section('Telegram'):
        print("❌ Ошибка в конфиге: отсутствует секция [Telegram]!")
        sys.exit(1)
        
    return config['Telegram']


async def self_update():
    print("🔍 Проверка обновлений основного файла бота...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GITHUB_RAW_URL) as response:
                if response.status == 200:
                    new_content = await response.text()
                    version_match = re.search(r'VERSION\s*=\s*"([\d.]+)"', new_content)
                    
                    if not version_match:
                        print("⚠️ Не удалось определить версию в обновлении.")
                        return
                        
                    new_version = version_match.group(1)
                    current_parts = list(map(int, VERSION.split('.')))
                    new_parts = list(map(int, new_version.split('.')))
                    
                    if new_parts > current_parts:
                        print(f"🆕 Обнаружена новая версия {new_version}, обновление...")
                        temp_file = 'bot_temp.py'
                        script_path = os.path.abspath(__file__)
                        
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                            
                        shutil.move(temp_file, script_path)
                        print("✅ Обновление завершено. Перезапуск бота...")
                        os.execv(sys.executable, [sys.executable] + sys.argv)
                    else:
                        print(f"✅ Установлена актуальная версия {VERSION}.")
                else:
                    print(f"⚠️ Ошибка проверки обновлений. Код: {response.status}")
    except Exception as e:
        print(f"⚠️ Ошибка при обновлении: {str(e)}")


async def update_animation_script():
    print("🔍 Проверка обновлений для animation_script.py...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GITHUB_ANIMATION_URL) as response:
                if response.status == 200:
                    new_content = await response.text()
                    # Если в файле animation_script.py есть версия, можно добавить проверку версии.
                    temp_file = 'animation_temp.py'
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    shutil.move(temp_file, ANIMATION_FILE)
                    print("✅ Файл animation_script.py успешно обновлён.")
                else:
                    print(f"⚠️ Ошибка при проверке обновлений для animation_script.py. Код: {response.status}")
    except Exception as e:
        print(f"⚠️ Ошибка обновления animation_script.py: {str(e)}")


async def authenticate(client, phone):
    try:
        await client.send_code_request(phone)
        code = get_input("Введите код подтверждения из Telegram: ", r'^\d+$', "Код должен содержать только цифры!")
        return await client.sign_in(phone=phone, code=code)
    except PhoneCodeInvalidError:
        print("Неверный код подтверждения!")
        return await authenticate(client, phone)
    except SessionPasswordNeededError:
        password = get_input("Введите пароль двухфакторной аутентификации: ")
        return await client.sign_in(password=password)


async def async_input(prompt: str = "> ") -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, prompt)


async def console_input_task(client):
    while True:
        cmd = (await async_input()).strip().lower()
        if cmd == '/update':
            await self_update()
        elif cmd == '/update_animation':
            await update_animation_script()
        elif cmd == '/a':
            if not os.path.exists(ANIMATION_FILE):
                print(f"⛔ Скрипт {ANIMATION_FILE} не найден!")
            else:
                print(f"🚀 Запускаем {ANIMATION_FILE} для выбора анимации...")
                await client.disconnect()
                subprocess.Popen([sys.executable, ANIMATION_FILE])
                sys.exit(0)
        elif cmd == '/exit':
            await client.disconnect()
            print("\n🛑 Завершение работы бота...")
            sys.exit(0)
        else:
            print("⚠️ Неизвестная команда. Доступные команды: /a, /update, /update_animation, /exit")


async def main():
    print(f"\n🚀 Запуск бота версии {VERSION}")
    await self_update()
    
    config = create_or_read_config()
    
    client = TelegramClient(
        SESSION_FILE,
        int(config['api_id']),
        config['api_hash']
    )
    
    try:
        await client.start(phone=lambda: config['phone_number'])
        
        if not await client.is_user_authorized():
            print("\n🔐 Начинаем процесс авторизации...")
            await authenticate(client, config['phone_number'])
        
        print("\n✅ Успешная авторизация!")
        print("\n🛠️ Доступные команды:")
        print("/a - запуск скрипта выбора анимации")
        print("/update - принудительная проверка обновлений основного файла")
        print("/update_animation - проверка обновлений для animation_script.py")
        print("/exit - выход из бота")
        print("/p Текст - анимация выбранным стилем.\n")

        # Обработчик для анимации текста по команде /p
        @client.on(events.NewMessage(pattern=r'/p (.+)'))
        async def handle_animation(event):
            # Обрабатываем команду только для исходящих сообщений (от бота)
            if not event.out:
                return
            try:
                text = event.pattern_match.group(1)
                typed_text = ""
                for char in text:
                    typed_text += char
                    await event.edit(typed_text + animation_settings["cursor_symbol"])
                    await asyncio.sleep(animation_settings["typing_speed"])
                await event.edit(typed_text)
            except Exception as e:
                print(f"Ошибка анимации: {e}")
                await event.reply("<b>Произошла ошибка во время выполнения команды.</b>", parse_mode='html')
        
        # Обработчик для входящих сообщений в личных чатах
        @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
        async def handle_private_message(event):
            try:
                msg_text = event.raw_text.strip().lower()
                
                if msg_text == '/exit':
                    await event.respond('🛑 Останавливаю работу...')
                    await client.disconnect()
                    print("Бот завершил работу по команде /exit из сообщения.")
                    sys.exit(0)
                
                elif msg_text == '/k':
                    message = await event.respond('🔄 Обновляю список команд...')
                    commands = "Список команд:\n/a - запуск выбора анимации\n/update - проверка обновлений основного файла\n/update_animation - проверка обновлений animation_script.py\n/exit - выход"
                    await message.edit(commands)
            except Exception as e:
                print(f"Ошибка при обработке сообщения: {e}")

        # Обработчик для исходящих сообщений бота
        @client.on(events.NewMessage(outgoing=True))
        async def handle_own_messages(event):
            msg_text = event.raw_text.strip().lower()
            
            if msg_text == '/exit':
                await event.respond('🛑 Останавливаю работу...')
                await client.disconnect()
                print("Бот завершил работу по команде /exit из своего сообщения.")
                sys.exit(0)
            
            elif msg_text == '/update':
                await self_update()
                await event.respond('✅ Проверка обновлений основного файла завершена')
            
            elif msg_text == '/update_animation':
                await update_animation_script()
                await event.respond('✅ Проверка обновлений для animation_script.py завершена')
            
            elif msg_text == '/a':
                if os.path.exists(ANIMATION_FILE):
                    await event.respond('🚀 Запускаю скрипт выбора анимации...')
                    await client.disconnect()
                    subprocess.Popen([sys.executable, ANIMATION_FILE])
                    sys.exit(0)
                else:
                    await event.respond(f'❌ Скрипт {ANIMATION_FILE} не найден!')

        # Запускаем задачу для обработки консольного ввода
        asyncio.create_task(console_input_task(client))
        
        # Оставляем клиента работать до отключения
        await client.run_until_disconnected()
                
    except Exception as e:
        print(f"\n⛔ Критическая ошибка: {str(e)}")
        await client.disconnect()
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Работа бота завершена пользователем.")
