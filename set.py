import asyncio
from random import choice

HEART = '🤍'
COLORED_HEARTS = [ '💗', '💓', '💖', '💘', '❤️', '💞',  # Сердечки
    '✨', '🌟', '💫', '🌈', '🔥', '🌹',  # Звезды, огонь, роза
                 ]
EDIT_DELAY = 1.0  # Задержка для более плавной анимации

# Каркас парада с правильным выравниванием
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
    await client.edit_message(event.chat_id, event.message.id, 'Я')
    await asyncio.sleep(1)
    await client.edit_message(event.chat_id, event.message.id, 'Я люблю')
    await asyncio.sleep(1)
    await client.edit_message(event.chat_id, event.message.id, 'Я люблю тебя💗')

# Функция для выравнивания текста по центру
def center_text(text, width=50):
    # Рассчитываем количество невидимых символов для выравнивания по центру
    lines = text.split('\n')
    centered_text = ''
    for line in lines:
        # Вычисляем отступы слева и справа
        spaces = (width - len(line)) // 2
        centered_line = '\u200B' * spaces + line + '\u200B' * spaces  # Невидимые пробелы с обеих сторон
        centered_text += centered_line + '\n'
    return centered_text

# Функция для анимации парада
async def animate_parade(client, event):
    for _ in range(7):  # Сделаем 50 шагов анимации
        text = generate_parade_colored()  # Генерируем новый вариант парада
        centered_text = center_text(text)  # Центрируем текст
        await client.edit_message(event.chat_id, event.message.id, centered_text)  # Обновляем сообщение
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
    # Центрируем текст
    centered_output = center_text(output)  # Центрируем текст
    await client.edit_message(event.chat_id, event.message.id, centered_output)
    await asyncio.sleep(EDIT_DELAY / 2)

async def process_colored_parade(client, event):
    for i in range(50):
        text = generate_parade_colored()
        centered_text = center_text(text)  # Центрируем текст
        await client.edit_message(event.chat_id, event.message.id, centered_text)
        await asyncio.sleep(EDIT_DELAY)

async def magic_script(client, event):
    await process_build_place(client, event)
    await process_colored_parade(client, event)
    await process_love_words(client, event)
