ANIMATION_SCRIPT_VERSION = "0.2.6"

import asyncio
import random

typing_speed = 0.4
pixel_typing_speed = 0.2
cursor_symbol = "▮"

async def animate_text(event, text):
    """Стандартная анимация: постепенное появление текста с мигающим курсором."""
    displayed_text = ""
    msg = await event.edit(displayed_text + cursor_symbol)
    for char in text:
        displayed_text += char
        try:
            await msg.edit(displayed_text + cursor_symbol)
        except Exception:
            pass
        await asyncio.sleep(typing_speed)
    await msg.edit(displayed_text)

async def pixel_destruction(event, text):
    """Анимация 'Пиксельное разрушение': сначала пикселизация, затем разрушение текста."""
    lines_count = 4
    chunk_size = max(1, len(text) // lines_count)
    text_lines = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    previous_text = ""
    # Убираем сообщение "Начинаю анимацию..."
    # msg = await event.edit("Начинаю анимацию...")
    # await asyncio.sleep(1)  # Убираем задержку
    # Фаза 1: пикселизация
    pixelated_text = [list(" " * len(line)) for line in text_lines]
    for _ in range(3):
        for i in range(len(pixelated_text)):
            for j in range(len(pixelated_text[i])):
                if random.random() < 0.1:
                    pixelated_text[i][j] = random.choice([".", "*", "○", "⊙", "%"])
        displayed_text = "\n".join("".join(line) for line in pixelated_text)
        if displayed_text != previous_text:
            try:
                await msg.edit(displayed_text)
                previous_text = displayed_text
            except Exception:
                pass
        await asyncio.sleep(pixel_typing_speed)
    # Фаза 2: разрушение
    for _ in range(3):
        displayed_text = "\n".join(
            "".join(random.choice([".", "*", " ", "○", "⊙"]) for _ in line)
            for line in text_lines
        )
        if displayed_text != previous_text:
            try:
                await msg.edit(displayed_text)
                previous_text = displayed_text
            except Exception:
                pass
        await asyncio.sleep(pixel_typing_speed)
    await msg.edit(text)

async def shifting_pattern(event, text):
    """Анимация 'Сдвигающийся узор': текст появляется слева направо с фоном."""
    pattern = ["░", "▒", "▓", "█"]  # Изменили порядок символов
    width = len(text) + 6  # Ширина фона
    msg = await event.edit("")
    background = "".join(random.choices(pattern, k=width))
    
    for i in range(len(text)):
        # Символы текста появляются постепенно
        display_text = background[:3] + text[:i+1] + background[3:]
        try:
            await msg.edit(display_text)
        except Exception:
            pass
        await asyncio.sleep(0.3)
    
    await msg.edit(text)  # Завершаем с полным текстом

# Словарь доступных анимаций: ключ – номер, значение – кортеж (название, функция)
animations = {
    1: ("Стандартная анимация ✍️", animate_text),
    2: ("Пиксельное разрушение 💥", pixel_destruction),
    3: ("Сдвигающийся узор ▓", shifting_pattern)
}
