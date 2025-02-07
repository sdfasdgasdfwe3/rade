import os
import sys
import subprocess
import asyncio
from telethon import TelegramClient, events

VERSION = "2.1"
CONFIG_FILE = 'config.ini'
SESSION_FILE = 'session_name'

async def main():
    print(f"\n🚀 Запуск бота версии {VERSION}")
    
    client = TelegramClient(
        SESSION_FILE,
        int(os.getenv('API_ID', 0)),
        os.getenv('API_HASH', '')
    )
    
    try:
        await client.start(phone=lambda: os.getenv('PHONE_NUMBER', ''))
        
        if not await client.is_user_authorized():
            print("\n🔐 Ошибка авторизации!")
            sys.exit(1)
        
        print("\n✅ Успешная авторизация!")
        print("\n🛠️ Доступные команды:")
        print("/a - Запуск анимационного скрипта")
        print("/update - Принудительная проверка обновлений")
        print("/exit - Выход из бота\n")

        @client.on(events.NewMessage(incoming=True))
        async def handle_private_message(event):
            msg_text = event.raw_text.strip().lower()
            print(f"[DEBUG] Получено сообщение: {msg_text}")
            
            if msg_text == '/exit':
                await event.respond('🛑 Останавливаю работу...')
                await client.disconnect()
                print("Бот завершил работу по команде /exit.")
                sys.exit(0)
            
            elif msg_text == '/k':
                message = await event.respond('🔄 Обновляю список команд...')
                commands = "Список команд:\n/a - запуск анимации\n/update - проверка обновлений\n/exit - выход"
                await message.edit(commands)
            
            elif msg_text == '/a':
                script_name = "animation_script.py"
                if os.path.exists(script_name):
                    await event.respond('🚀 Запускаю анимацию...')
                    await client.disconnect()
                    subprocess.Popen([sys.executable, script_name])
                    sys.exit(0)
                else:
                    await event.respond(f'❌ Скрипт {script_name} не найден!')
        
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
