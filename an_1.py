import asyncio

async def run_animation(client, event, text):
    """Стандартная анимация текста"""
    typing_speed = 0.5  # скорость печатания
    cursor_symbol = "▮"  # Символ курсора

    displayed_text = ""
    for char in text:
        displayed_text += char
        await client.edit_message(event.chat_id, event.message.id, displayed_text + cursor_symbol)
        await asyncio.sleep(typing_speed)
    await client.edit_message(event.chat_id, event.message.id, displayed_text)
