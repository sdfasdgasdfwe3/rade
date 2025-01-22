# an_2.py

import asyncio
import random

async def run_animation(client, event, text):
    # Преобразуем текст на 4 строки для эффекта
    lines_count = 4
    chunk_size = len(text) // lines_count
    text_lines = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    # Инициализация переменной для предыдущего текста
    previous_text = ""

    # Шаг 1: Инициализация (пиксельное разрешение)
    pixelated_text = [list(" " * len(line)) for line in text_lines]
    for _ in range(3):  # Количество шагов разрешения
        for i in range(len(pixelated_text)):
            for j in range(len(pixelated_text[i])):
                if random.random() < 0.1:  # С вероятностью 10% заменяем символ
                    pixelated_text[i][j] = random.choice([".", "*", "○", "⊙", "%"])
        # Объединяем строки и отправляем
        displayed_text = "\n".join(["".join(line) for line in pixelated_text])

        # Проверяем, изменился ли текст и отправляем только если есть изменения
        if displayed_text != previous_text and displayed_text.strip() != "":
            try:
                await client.edit_message(event.chat_id, event.message.id, displayed_text)
                previous_text = displayed_text
            except ValueError:  # Обработка ошибки, если текст не может быть отредактирован
                pass

        await asyncio.sleep(0.10)  # Используем уменьшенную скорость

    # Шаг 2: Постепенное исчезновение (разрушение)
    for _ in range(5):  # Количество шагов разрушения
        displayed_text = "\n".join(["".join([random.choice([".", "*", " ", "○", "⊙"]) for _ in range(len(line))]) for line in text_lines])

        # Проверяем, изменился ли текст и отправляем только если есть изменения
        if displayed_text != previous_text and displayed_text.strip() != "":
            try:
                await client.edit_message(event.chat_id, event.message.id, displayed_text)
                previous_text = displayed_text
            except ValueError:  # Обработка ошибки, если текст не может быть отредактирован
                pass

        await asyncio.sleep(0.10)  # Используем уменьшенную скорость

    # Завершаем разрушение с использованием пустого символа
    await client.edit_message(event.chat_id, event.message.id, text)  # Оставляем исходное сообщение пользователя

