import asyncio
import random
from telethon import events

ANIMATION_SCRIPT_VERSION = "0.2.78"

# Скорости анимаций
typing_speed = 0.4
pixel_typing_speed = 0.2
random_reveal_speed = 0.2
led_display_speed = 0.3
cursor_symbol = "▮"

async def animate_text(event, text):
    """Стандартная анимация с курсором"""
    displayed_text = ""
    msg = await event.edit(displayed_text + cursor_symbol)
    for char in text:
        displayed_text += char
        await msg.edit(displayed_text + cursor_symbol)
        await asyncio.sleep(typing_speed)
    await msg.edit(displayed_text)

async def pixel_destruction(event, text):
    """Пиксельное разрушение"""
    lines_count = 4
    chunk_size = max(1, len(text) // lines_count)
    text_lines = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    previous_text = ""
    
    # Фаза 1: Пикселизация
    pixelated_text = [list(" " * len(line)) for line in text_lines]
    for _ in range(3):
        for i in range(len(pixelated_text)):
            for j in range(len(pixelated_text[i])):
                if random.random() < 0.1:
                    pixelated_text[i][j] = random.choice([".", "*", "○", "⊙", "%"])
        displayed_text = "\n".join("".join(line) for line in pixelated_text)
        if displayed_text != previous_text:
            await event.edit(displayed_text)
            previous_text = displayed_text
        await asyncio.sleep(pixel_typing_speed)
    
    # Фаза 2: Разрушение
    for _ in range(3):
        displayed_text = "\n".join(
            "".join(random.choice([".", "*", " ", "○", "⊙"]) for _ in line)
            for line in text_lines
        )
        if displayed_text != previous_text:
            await event.edit(displayed_text)
            previous_text = displayed_text
        await asyncio.sleep(pixel_typing_speed)
    
    await event.edit(text)

async def random_reveal(event, text):
    """Случайное появление букв"""
    hidden_text = ["*" if char != " " else " " for char in text]
    msg = await event.edit("".join(hidden_text))
    
    indices = list(range(len(text)))
    random.shuffle(indices)
    
    for index in indices:
        hidden_text[index] = text[index]
        await msg.edit("".join(hidden_text))
        await asyncio.sleep(random_reveal_speed)
    
    await msg.edit(text)

async def led_display(event, text):
    """Светодиодный экран"""
    hidden_text = ["⬛" for _ in text]
    msg = await event.edit("".join(hidden_text))
    
    for i in range(len(text)):
        hidden_text[i] = text[i]
        await msg.edit("".join(hidden_text))
        await asyncio.sleep(led_display_speed)
    
    await msg.edit(text)

animations = {
    1: ("Стандартная анимация ✍️", animate_text),
    2: ("Пиксельное разрушение 💥", pixel_destruction),
    3: ("Случайное появление 🎲", random_reveal),
    4: ("Светодиодный экран 🔲", led_display)
}
