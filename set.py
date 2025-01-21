import asyncio
from random import choice
from telethon import TelegramClient

HEART = '🤍'
COLORED_HEARTS = ['💗', '💓', '💖', '💘', '❤️', '💞']
MAGIC_PHRASES = ['/magic']
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

async def process_build_place(client, event):
    output = ''
    for i in range(8):
        output += '\n'
        for j in range(11):
            output += HEART
            await client.edit_message(event.peer_id.user_id, event.message.id, output)
            await asyncio.sleep(EDIT_DELAY / 2)

async def process_colored_parade(client, event):
    for _ in range(100):
        text = ''.join([choice(COLORED_HEARTS) if c == '1' else HEART for c in PARADE_MAP])
        await client.edit_message(event.peer_id.user_id, event.message.id, text)
        await asyncio.sleep(EDIT_DELAY)

async def process_love_words(client, event):
    messages = ['i', 'i love', 'i love you', 'i love you forever💗']
    for msg in messages:
        await client.edit_message(event.peer_id.user_id, event.message.id, msg)
        await asyncio.sleep(1)

async def magic_script(client, event):
    print("[INFO] Начало выполнения анимации.")
    await process_build_place(client, event)
    await process_colored_parade(client, event)
    await process_love_words(client, event)
    print("[INFO] Анимация завершена.")

