import asyncio
from random import choice
from telethon import TelegramClient
from telethon.events import NewMessage

# Ваши настройки и переменные для анимации
HEART = '🤍'
COLORED_HEARTS = ['💗', '💓', '💖', '💘', '❤️', '💞']
MAGIC_PHRASES = ['magic']
EDIT_DELAY = 0.05

PARADE_MAP = '''
00000000000
00111011100
01111111110
01111111110
00111111100
00011111000
00001110000
00000100000
'''

client = TelegramClient('tg-account', APP_ID, API_HASH)

# Функция, которая будет вызываться из bot.py
async def magic_script(client, event):
    # Начинаем анимацию
    await process_build_place(event)
    await process_colored_parade(event)
    await process_love_words(event)

def generate_parade_colored():
    output = ''
    for c in PARADE_MAP:
        if c == '0':
            output += HEART
        elif c == '1':
            output += choice(COLORED_HEARTS)
        else:
            output += c
    return output


async def process_love_words(event: NewMessage.Event):
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i')
    await asyncio.sleep(0.5)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love')
    await asyncio.sleep(0.5)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you')
    await asyncio.sleep(0.5)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you forever')
    await asyncio.sleep(0.5)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you forever💗')


async def process_build_place(event: NewMessage.Event):
    output = ''
    for i in range(8):
        output += '\n'
        for j in range(11):
            output += HEART
            await client.edit_message(event.peer_id.user_id, event.message.id, output)
            await asyncio.sleep(EDIT_DELAY / 2)


async def process_colored_parade(event: NewMessage.Event):
    for i in range(100):
        text = generate_parade_colored()
        await client.edit_message(event.peer_id.user_id, event.message.id, text)
        await asyncio.sleep(EDIT_DELAY)


# Обработчик для команды magic
@client.on(NewMessage(outgoing=True))
async def handle_message(event: NewMessage.Event):
    if event.message.message in MAGIC_PHRASES:
        await magic_script(client, event)
