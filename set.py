import asyncio
from random import choice

HEART = '🤍'
COLORED_HEARTS = ['💗', '💓', '💖', '💘', '❤️', '💞']
EDIT_DELAY = 0.05  # Задержка для более плавной анимации

# Пример парада, где строки не обрезаются, но изменяется количество видимых строк
PARADE_MAP = '''
00000000000
00111011100
01111111110
01111111110
00111111100
00011111000
00001110000
00000100000
00000000000
'''

# Функция для генерации анимации с цветными сердечками
def generate_parade_colored():
    output = ''
    for c in PARADE_MAP:
        if c == '0':
            output += HEART  # Пустое место - обычное сердце
        elif c == '1':
            output += choice(COLORED_HEARTS)  # Цветное сердце
        elif c == '\n':  # Если символ - новая строка, просто добавляем новую строку
            output += '\n'
    return output

# Функция для вывода слов "Я люблю тебя"
async def process_love_words(client, event):
    await client.edit_message(event.chat_id, event.message.id, 'i')
    await asyncio.sleep(1)
    await client.edit_message(event.chat_id, event.message.id, 'i love')
    await asyncio.sleep(1)
    await client.edit_message(event.chat_id, event.message.id, 'i love you')
    await asyncio.sleep(1)
    await client.edit_message(event.chat_id, event.message.id, 'i love you forever')
    await asyncio.sleep(1)
    await client.edit_message(event.chat_id, event.message.id, 'i love you forever💗')

# Функция для анимации парада
async def animate_parade(client, event):
    for _ in range(50):  # Сделаем 50 шагов анимации
        text = generate_parade_colored()  # Генерируем новый вариант парада
        # Здесь мы можем динамически обрезать только часть строк для мобильных устройств
        # Например, ограничим 6 строками, но сохраняем сам рисунок
        text = '\n'.join(text.splitlines()[:6])  # Ограничиваем 6 строками для мобильных устройств
        await client.edit_message(event.chat_id, event.message.id, text)  # Обновляем сообщение
        await asyncio.sleep(EDIT_DELAY)  # Задержка для анимации

# Главная функция, которая управляет всем процессом
async def main(client, event):
    await asyncio.gather(
        animate_parade(client, event),  # Анимация парада сердечек
        process_love_words(client, event)  # Выводим текст "I love you"
    )

async def process_build_place(client, event):
    output = ''
    for i in range(8):
        output += '\n'
        for j in range(11):  # Уменьшаем количество символов в каждой строке
            output += HEART
        await client.edit_message(event.chat_id, event.message.id, output)
        await asyncio.sleep(EDIT_DELAY / 2)

async def process_colored_parade(client, event):
    for i in range(50):
        text = generate_parade_colored()
        await client.edit_message(event.chat_id, event.message.id, text)
        await asyncio.sleep(EDIT_DELAY)

async def magic_script(client, event):
    await process_build_place(client, event)
    await process_colored_parade(client, event)
    await process_love_words(client, event)
