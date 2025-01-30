import configparser
from telethon import TelegramClient, events
import sys
import asyncio

animations = [
    "Анимация 1: Пример 1",
    "Анимация 2: Пример 2",
    "Анимация 3: Пример 3"
]

async def delete_last_messages(client, chat_id, count=3):
    messages = await client.get_messages(chat_id, limit=count, from_user='me')
    if messages:
        await client.delete_messages(chat_id, messages)

async def main():
    chat_id = int(sys.argv[1]) if len(sys.argv) > 1 else "me"
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_id = config['Telegram']['api_id']
    api_hash = config['Telegram']['api_hash']
    phone_number = config['Telegram']['phone_number']
    
    client = TelegramClient('animation_session', api_id, api_hash)
    await client.start(phone=phone_number)
    
    try:
        anim_list = "Выберите анимацию:\n" + "\n".join([f"{i+1}. {anim}" for i, anim in enumerate(animations)])
        await client.send_message(chat_id, anim_list)
        
        choice = None
        while choice is None:
            event = await client.wait_for(events.NewMessage(chats=chat_id))
            try:
                choice = int(event.message.text)
                if 1 <= choice <= len(animations):
                    with open('selected_animation.txt', 'w') as f:
                        f.write(str(choice))
                    await delete_last_messages(client, chat_id, 3)
                else:
                    await event.reply("Неверный номер. Попробуйте снова.")
                    choice = None
            except ValueError:
                await event.reply("Пожалуйста, введите номер цифрой.")
                choice = None
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
