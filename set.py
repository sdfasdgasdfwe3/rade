import os
import sys
from telethon import TelegramClient
import bot  # Импортируем bot.py для доступа к глобальной переменной

# Функция, которая будет вызываться из bot.py
async def magic_script(client: TelegramClient, event):
    # Отключаем анимацию перед переходом в set.py
    bot.is_typing_enabled = False

    # Здесь вы используете уже авторизованный клиент, выполняете необходимые действия
    # Например, отправляем сообщение или выполняем логику

    # Пример выполнения действия:
    await client.send_message(event.chat_id, "Выполнил команду magic!")

    # Переход обратно в bot.py после выполнения действия
    os.execv(sys.executable, ['python'] + sys.argv)  # Это вызовет перезапуск bot.py
