ANIMATION_SCRIPT_VERSION = "0.2.76"

import asyncio
import random

typing_speed = 0.4
pixel_typing_speed = 0.2
random_reveal_speed = 0.2
led_display_speed = 0.3
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
                await event.edit(displayed_text)
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
                await event.edit(displayed_text)
                previous_text = displayed_text
            except Exception:
                pass
        await asyncio.sleep(pixel_typing_speed)
    await event.edit(text)

async def random_reveal(event, text):
    """Анимация 'Случайное появление букв': буквы открываются в случайном порядке."""
    hidden_text = ["*" if char != " " else " " for char in text]
    msg = await event.edit("".join(hidden_text))  # Показываем скрытый текст

    indices = list(range(len(text)))  # Индексы всех символов
    random.shuffle(indices)  # Перемешиваем порядок появления букв

    for index in indices:
        hidden_text[index] = text[index]  # Открываем букву
        try:
            await msg.edit("".join(hidden_text))  # Обновляем сообщение
        except Exception:
            pass
        await asyncio.sleep(random_reveal_speed)  # Пауза между буквами

    await msg.edit(text)  # Финальный текст

async def led_display(event, text):
    """Анимация 'Светодиодный экран': буквы появляются по частям, как на табло."""
    hidden_text = ["⬛" for _ in text]  # Начальное состояние (все буквы скрыты)
    msg = await event.edit("".join(hidden_text))

    for i in range(len(text)):
        hidden_text[i] = text[i]  # Заменяем ⬛ на реальную букву
        try:
            await msg.edit("".join(hidden_text))  # Обновляем сообщение
        except Exception:
            pass
        await asyncio.sleep(led_display_speed)  # Задержка перед следующей буквой

    await msg.edit(text)  # Финальный текст

# Словарь доступных анимаций
animations = {
    1: ("Стандартная анимация ✍️", animate_text),
    2: ("Пиксельное разрушение 💥", pixel_destruction),
    3: ("Случайное появление букв 🎲", random_reveal),
    4: ("Светодиодный экран 🔲", led_display)
}

# Телеграмм клиент и другие части кода остаются неизменными

@client.on(events.NewMessage(pattern='/m'))
async def animation_menu(event):
    global animation_selection_mode
    animation_selection_mode = True
    menu_text = "Выберите анимацию:\n"
    for num, (name, _) in sorted(animations.items()):
        menu_text += f"{num}) {name}\n"
    menu_text += "\nВведите номер желаемой анимации."
    await event.reply(menu_text)  # Отправка сообщения только в текущий чат

@client.on(events.NewMessage)
async def animation_selection_handler(event):
    global animation_selection_mode, selected_animation, config
    # Проверяем, что это сообщение от того пользователя, который вызвал команду /m
    if animation_selection_mode and event.chat_id == event.sender_id:
        text = event.raw_text.strip()
        if text.isdigit():
            number = int(text)
            if number in animations:
                selected_animation = number
                config["selected_animation"] = selected_animation
                save_config(config)
                await event.reply(f"{EMOJIS['success']} Вы выбрали анимацию: {animations[selected_animation][0]}")
                # Удаляем 4 последних исходящих (своих) сообщения бота в чате
                messages = await client.get_messages(event.chat_id, limit=10)
                deleted_count = 0
                for msg in messages:
                    if msg.out:
                        try:
                            await msg.delete()
                            deleted_count += 1
                        except Exception as e:
                            print(f"{EMOJIS['error']} Ошибка удаления сообщения:", e)
                        if deleted_count >= 4:
                            break
            else:
                await event.reply(f"{EMOJIS['error']} Неверный номер анимации.")
            animation_selection_mode = False  # Сбрасываем флаг после выбора
        else:
            await event.reply(f"{EMOJIS['error']} Пожалуйста, введите корректный номер анимации.")
            animation_selection_mode = False  # Сбрасываем флаг, если введен некорректный текст
