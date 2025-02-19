import asyncio
import random

# === Параметры анимации ===
typing_speed = 0.4
pixel_typing_speed = 0.2
random_reveal_speed = 0.2
led_display_speed = 0.3
cursor_symbol = "▮"

async def animate_text(event, text):
    msg = await event.respond(cursor_symbol)
    displayed_text = ""
    for char in text:
        displayed_text += char
        await msg.edit(displayed_text + cursor_symbol)
        await asyncio.sleep(typing_speed)
    await msg.edit(displayed_text)

async def pixel_destruction(event, text):
    msg = await event.respond(text)
    for _ in range(5):
        scrambled_text = "".join(random.choice([".", "*", "○", "⊙", " "]) for _ in text)
        await msg.edit(scrambled_text)
        await asyncio.sleep(pixel_typing_speed)
    await msg.edit(text)

async def random_reveal(event, text):
    hidden_text = ["*" if char != " " else " " for char in text]
    msg = await event.respond("".join(hidden_text))
    indices = list(range(len(text)))
    random.shuffle(indices)
    for index in indices:
        hidden_text[index] = text[index]
        await msg.edit("".join(hidden_text))
        await asyncio.sleep(random_reveal_speed)
    await msg.edit(text)

async def led_display(event, text):
    hidden_text = ["⬛" for _ in text]
    msg = await event.respond("".join(hidden_text))
    for i in range(len(text)):
        hidden_text[i] = text[i]
        await msg.edit("".join(hidden_text))
        await asyncio.sleep(led_display_speed)
    await msg.edit(text)

animations = {
    1: ("Стандартная ✍️", animate_text),
    2: ("Пиксельное разрушение 💥", pixel_destruction),
    3: ("Случайное появление 🎲", random_reveal),
    4: ("Светодиодный экран 🔲", led_display)
}
