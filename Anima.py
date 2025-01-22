import asyncio
import random

async def run_animation(client, event, text, animation_choice):
    """Выбор анимации и выполнение соответствующего эффекта"""
    
    # Если выбран эффект анимации текста
    if animation_choice == 1:
        await run_text_animation(client, event, text)
    # Если выбран эффект пиксельного разрушения
    elif animation_choice == 2:
        await run_pixelation_animation(client, event, text)

    # Удаляем последние три сообщения бота
    await delete_last_bot_messages(client, event)

async def run_text_animation(client, event, text):
    """Стандартная анимация текста"""
    typing_speed = 0.5  # скорость печатания
    cursor_symbol = "▮"  # Символ курсора

    displayed_text = ""
    for char in text:
        displayed_text += char
        await client.edit_message(event.chat_id, event.message.id, displayed_text + cursor_symbol)
        await asyncio.sleep(typing_speed)
    await client.edit_message(event.chat_id, event.message.id, displayed_text)

async def run_pixelation_animation(client, event, text):
    """Пиксельная анимация текста"""
    lines_count = 4
    chunk_size = len(text) // lines_count
    text_lines = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    previous_text = ""

    # Шаг 1: Инициализация (пиксельное разрешение)
    pixelated_text = [list(" " * len(line)) for line in text_lines]
    for _ in range(3):  # Количество шагов разрешения
        for i in range(len(pixelated_text)):
            for j in range(len(pixelated_text[i])):
                if random.random() < 0.1:
                    pixelated_text[i][j] = random.choice([".", "*", "○", "⊙", "%"])
        displayed_text = "\n".join(["".join(line) for line in pixelated_text])

        if displayed_text != previous_text and displayed_text.strip() != "":
            try:
                await client.edit_message(event.chat_id, event.message.id, displayed_text)
                previous_text = displayed_text
            except ValueError:
                pass
        await asyncio.sleep(0.10)

    # Шаг 2: Постепенное исчезновение (разрушение)
    for _ in range(5):  # Количество шагов разрушения
        displayed_text = "\n".join(["".join([random.choice([".", "*", " ", "○", "⊙"]) for _ in range(len(line))]) for line in text_lines])

        if displayed_text != previous_text and displayed_text.strip() != "":
            try:
                await client.edit_message(event.chat_id, event.message.id, displayed_text)
                previous_text = displayed_text
            except ValueError:
                pass
        await asyncio.sleep(0.10)

    # Завершаем разрушение с использованием пустого символа
    await client.edit_message(event.chat_id, event.message.id, text)

async def delete_last_bot_messages(client, event):
    """Удаляем последние три сообщения бота"""
    messages = await client.get_chat_history(event.chat_id, limit=5)  # Получаем последние 5 сообщений
    bot_messages = [msg for msg in messages if msg.sender_id == client.user_id]
    for msg in bot_messages[:3]:  # Удаляем 3 последние сообщения бота
        try:
            await client.delete_messages(event.chat_id, msg.id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

# Пример использования
async def handle_animation_command(client, event, text, animation_choice):
    await run_animation(client, event, text, animation_choice)
