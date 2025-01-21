import asyncio
from random import choice

from telethon import TelegramClient
from telethon.events import NewMessage

APP_ID = 1252636
API_HASH = '4037e9f957f6f17d461b0c288ffa50f1'

HEART = '🤍'
COLORED_HEARTS = ['💗', '💓', '💖', '💘', '❤️', '💞']
MAGIC_PHRASES = ['magic']
EDIT_DELAY = 0.05  # Меньшая задержка для более плавной анимации

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


async def process_love_words(event: NewMessage.Event):
    await client.edit_message(event.peer_id.user_id, event.message.id, 'Я')
    await asyncio.sleep(0.5)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'Я люблю')
    await asyncio.sleep(0.5)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'Я люблю тебя')
    await asyncio.sleep(0.5)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'Я люблю тебя на всегда')
    await asyncio.sleep(0.5)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'Я люблю тебя на всегда 💗')


async def process_build_place(event: NewMessage.Event):
    output = ''
    for i in range(8):
        output += '\n'
        for j in range(11):
            output += HEART
            await client.edit_message(event.peer_id.user_id, event.message.id, output)
            await asyncio.sleep(EDIT_DELAY / 2)


async def process_colored_parade(event: NewMessage.Event):
    # Увеличим количество повторений и более плавно отображаем каждый цвет
    for i in range(50):  # Увеличиваем число итераций для более длительной анимации
        text = generate_parade_colored()
        await client.edit_message(event.peer_id.user_id, event.message.id, text)
        await asyncio.sleep(EDIT_DELAY)


@client.on(NewMessage(outgoing=True))
async def handle_message(event: NewMessage.Event):
    if event.message.message in MAGIC_PHRASES:
        await process_build_place(event)
        await process_colored_parade(event)
        await process_love_words(event)


if __name__ == '__main__':
    print('[*] Connect to client...')
    client.start()
    client.run_until_disconnected()
