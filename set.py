import asyncio
from random import choice

HEART = '🤍'
COLORED_HEARTS = [
    '💗', '💓', '💖', '💘', '❤️', '💞',  # Сердечки
    '✨', '🌟', '💫', '🌈', '🔥', '🌹',  # Звезды, огонь, роза
    '🌸', '🌺', '💐', '🥰', '😍', '😘',  # Цветы, лица
    '🌿', '🍃', '🍀', '🍏', '🌳'   # Зеленые стикеры (листва, дерево, растения)
]
EDIT_DELAY = 0.6  # Задержка для более плавной анимации

# Каркас парада с правильным выравниванием (11 на 13)
PARADE_MAP = '''
0000000000000
0011100111100
0111111111110
0111111111110
0111111111110
0111111111110
0111111111110
001111111110
000111111100
000011111000
000001110000
000000100000
000000000000
'''

# Функция для генерации анимации с цветными сердечками
def generate_parade_colored():
    output = ''
    for c in PARADE_MAP:
        if c == '0':
            output += HEART  # Пустое место - обычное сердце
        elif c == '1':
            output += choice(COLORED_HEARTS)  # Цветное сердце или другой смайлик
        elif c == '\n':  # Если символ - новая строка, просто добавляем новую строку
            output += '\n'

    # Разбиваем на строки для правильного выравнивания
    lines = output.split('\n')
    centered_output = ''
    
    # Центрируем каждую строку, добавляя пробелы с обеих сторон
    for line in lines:
        # Добавляем недостающие пробелы справа, чтобы длина строки была ровно 13
        if len(line) < 13:
            line = line + ' ' * (13 - len(line))  # Заполняем пробелами справа
        # Рассчитываем количество пустых символов для центрирования
        left_padding = (13 - len(line)) // 2
        right_padding = 13 - len(line) - left_padding
        centered_output += '\u200b' * left_padding + line + '\u200b' * right_padding + '\n'
    
    # Убираем лишний невидимый символ перед первой строкой
    return centered_output.strip()

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
    for _ in range(15):  # Сделаем 50 шагов анимации
        text = generate_parade_colored()  # Генерируем новый вариант парада
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
    # Добавляем невидимый символ для сохранения выравнивания
    output = '\u200b' + output.replace('\n', '\n\u200b')
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
