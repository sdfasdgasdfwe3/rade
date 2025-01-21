import asyncio
from random import choice

HEART = '🤍'
COLORED_HEARTS = ['💗', '💓', '💖', '💘', '❤️', '💞']
EDIT_DELAY = 0.05  # Задержка между обновлениями

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
        else:
            output += c
    return output

async def animate_parade(client, event):
    # Анимация парада: будем генерировать и обновлять картину
    for _ in range(50):  # Сделаем 50 шагов анимации
        text = generate_parade_colored()  # Генерируем новый вариант парада
        await client.edit_message(event.chat_id, event.message.id, text)  # Обновляем сообщение
        await asyncio.sleep(EDIT_DELAY)  # Задержка для анимации

# Важно, чтобы этот код работал в асинхронной среде с библиотеками для Telegram
# Например, Telethon или aiogram. Вот пример запуска с Telethon:

async def main(client, event):
    await animate_parade(client, event)  # Запускаем анимацию парада
