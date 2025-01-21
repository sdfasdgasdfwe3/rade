import asyncio
from random import choice

from telethon import TelegramClient
from telethon.events import NewMessage

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

# Функция для генерации анимации с цветными сердечками
def generate_parade_colored():
    output = ''
    for c in PARADE_MAP:
        if c == '0':
            output += HEART  # Пустое место - обычный смайлик
        elif c == '1':
            output += choice(COLORED_HEARTS)  # Цветное сердце или другой смайлик
        else:
            output += c  # Если это символ новой строки, добавляем его
    return output


# Функция для вывода фразы "Я люблю тебя"
async def process_love_words(event: NewMessage.Event):
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you forever')
    await asyncio.sleep(1)
    await client.edit_message(event.peer_id.user_id, event.message.id, 'i love you forever💗')


# Функция для построения местоположения (шаблона)
async def process_build_place(event: NewMessage.Event):
    output = ''
    for i in range(8):  # Количество строк
        output += '\n'
        for j in range(11):  # Количество символов в строке
            output += HEART
        await client.edit_message(event.peer_id.user_id, event.message.id, output)
        await asyncio.sleep(EDIT_DELAY / 2)  # Плавное отображение


# Функция для анимации парада с цветными сердечками
async def process_colored_parade(event: NewMessage.Event):
    for i in range(50):  # Количество итераций для анимации
        text = generate_parade_colored()  # Генерация нового шаблона
        await client.edit_message(event.peer_id.user_id, event.message.id, text)
        await asyncio.sleep(EDIT_DELAY)  # Плавное обновление


# Обработчик командных сообщений
@client.on(NewMessage(outgoing=True))
async def handle_message(event: NewMessage.Event):
    if event.message.message in MAGIC_PHRASES:  # Если сообщение соответствует магическим фразам
        await process_build_place(event)  # Построение местоположения
        await process_colored_parade(event)  # Показ анимации парада
        await process_love_words(event)  # Вывод фразы "I love you"


if __name__ == '__main__':
    print('[*] Connect to client...')
    client.start()  # Запуск клиента
    client.run_until_disconnected()  # Ожидание отключения
