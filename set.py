from telethon import TelegramClient

# Функция, которая будет вызываться из bot.py
async def magic_script(client: TelegramClient, event):
    # Здесь вы используете уже авторизованный клиент
    await event.respond("Скрипт magic был выполнен из set.py!")
    # Можно продолжить с использованием клиента для любых действий
    # Например, отправить сообщение
    await client.send_message(event.chat_id, "Выполнил команду magic!")
