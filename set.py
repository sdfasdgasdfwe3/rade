import asyncio
from random import choice
from telethon import TelegramClient
from telethon.events import NewMessage

# Конфигурация клиента
APP_ID = 1252636
API_HASH = '4037e9f957f6f17d461b0c288ffa50f1'

HEART = '🤍'
COLORED_HEARTS = ['💗', '💓', '💖', '💘', '❤️', '💞']
MAGIC_PHRASES = ['magic']
EDIT_DELAY = 0.01

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

async def process_love_words(event):
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you forever')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you forever💗')

async def process_build_place(event):
    output = ''
    for i in range(8):
        output += '\n'
        for j in range(11):
            output += HEART
            await client.edit_message(event.peer_id.user_id, event.message.id, output)
            await asyncio.sleep(EDIT_DELAY / 2)

async def process_colored_parade(event):
    for i in range(50):
        text = generate_parade_colored()
        await client.edit_message(event.peer_id.user_id, event.message.id, text)
        await asyncio.sleep(EDIT_DELAY)

@client.on(NewMessage(outgoing=True))
async def handle_message(event):
    if event.message.message in MAGIC_PHRASES:
        await process_build_place(event)
        await process_colored_parade(event)
        await process_love_words(event)

if __name__ == '__main__':
    print('[*] Connect to client...')
    client.start()
    client.run_until_disconnected()
