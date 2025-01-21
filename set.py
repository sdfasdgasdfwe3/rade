import asyncio
from random import choice

HEART = '🤍'
COLORED_HEARTS = [
    '💗', '💓', '💖', '💘', '❤️', '💞',  # Сердечки
    '✨', '🌟', '💫', '🌈', '🔥', '🌹',  # Звезды, огонь, роза
    '🌸', '🌺', '💐', '🥰', '😍', '😘'   # Цветы, лица
]
EDIT_DELAY = 0.05  # Задержка для более плавной анимации

# Каркас парада с правильным выравниванием
PARADE_MAP = '''
00000000000000000000000000
00000011100000000111000000
00001111110000001111110000
00011111111100111111111000
00111111111111111111111100
01111111111111111111111110
01111111111111111111111110
00111111111111111111111100
00111111111111111111111100
00011111111111111111111000
00001111111111111111110000
00000111111111111111100000
00000011111111111111000000
00000001111111111110000000
00000000011111111000000000
00000000001111110000000000
00000000000111100000000000
00000000000000000000000000
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
        # Чтобы текст корректно отображался на мобильном устройстве, добавим <code> для моноширинного шрифта (для Telegram)
        text = f"<code>{text}</code>"
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
    # Используем моноширинный шрифт для корректного отображения
    output = f"<code>{output}</code>"
    await client.edit_message(event.chat_id, event.message.id, output)
    await asyncio.sleep(EDIT_DELAY / 2)

async def process_colored_parade(client, event):
    for i in range(50):
        text = generate_parade_colored()
        # Используем моноширинный шрифт для корректного отображения
        text = f"<code>{text}</code>"
        await client.edit_message(event.chat_id, event.message.id, text)
        await asyncio.sleep(EDIT_DELAY)

async def magic_script(client, event):
    await process_build_place(client, event)
    await process_colored_parade(client, event)
    await process_love_words(client, event)
