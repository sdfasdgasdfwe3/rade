# set.py
import asyncio
from random import choice
from telethon import TelegramClient
from telethon.events import NewMessage

# Конфигурация клиента
HEART = '🤍'
COLORED_HEARTS = ['💗', '💓', '💖', '💘', '❤️', '💞']
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
EDIT_DELAY = 0.01

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
    await event.edit('i')
    await asyncio.sleep(1)
    await event.edit('i love')
    await asyncio.sleep(1)
    await event.edit('i love you')
    await asyncio.sleep(1)
    await event.edit('i love you forever')
    await asyncio.sleep(1)
    await event.edit('i love you forever💗')

async def process_build_place(event):
    output = ''
    for i in range(8):
        output += '\n'
        for j in range(11):
            output += HEART
            await event.edit(output)
            await asyncio.sleep(EDIT_DELAY / 2)

async def process_colored_parade(event):
    for i in range(50):
        text = generate_parade_colored()
        await event.edit(text)
        await asyncio.sleep(EDIT_DELAY)

# Функция для выполнения всех анимаций
async def magic_script(client, event):
    # Вызываем все анимации
    await process_build_place(event)
    await process_colored_parade(event)
    await process_love_words(event)
