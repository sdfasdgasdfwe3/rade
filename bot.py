import asyncio
import os
import logging
import requests
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError

# Получаем API ID и API Hash из переменных окружения или вводим вручную
api_id = int(os.environ.get("TELEGRAM_API_ID") or input("Введите API ID: "))
api_hash = os.environ.get("TELEGRAM_API_HASH") or input("Введите API Hash: ")

# Название сессии (файла, где будет храниться информация об авторизации)
session_name = "my_telegram_session"  # Имя файла сессии

# Ссылка на raw-файл в GitHub
GITHUB_RAW_URL = "https://raw.githubusercontent.com/sdfasdgasdfwe3ra/de/main/bot.py"

# Создаем клиент Telethon
client = TelegramClient(session_name, api_id, api_hash)

async def check_for_updates():
    """
    Проверяет наличие обновлений на GitHub.
    Если найдена новая версия, возвращает её содержимое.
    """
    try:
        response = requests.get(GITHUB_RAW_URL)
        response.raise_for_status()  # Проверяем, что запрос успешен
        remote_content = response.text

        # Читаем текущий файл скрипта
        with open(__file__, "r", encoding="utf-8") as file:
            local_content = file.read()

        # Сравниваем содержимое
        if remote_content != local_content:
            logger.info("Обнаружена новая версия скрипта!")
            return remote_content
        else:
            logger.info("У вас актуальная версия скрипта.")
            return None

    except Exception as e:
        logger.error(f"Ошибка при проверке обновлений: {e}")
        return None

async def update_script(new_content):
    """
    Обновляет текущий скрипт новой версией.
    """
    try:
        with open(__file__, "w", encoding="utf-8") as file:
            file.write(new_content)
        logger.info("Скрипт успешно обновлен!")
    except Exception as e:
        logger.error(f"Ошибка при обновлении скрипта: {e}")

async def main():
    try:
        # Проверяем обновления
        new_version = await check_for_updates()
        if new_version:
            logger.info("Найдена новая версия. Обновляюсь...")
            await update_script(new_version)
            logger.info("Перезапустите скрипт для применения обновлений.")
            return  # Завершаем выполнение, чтобы пользователь перезапустил скрипт

        # Запуск клиента и проверка авторизации
        await client.start()

        if not await client.is_user_authorized():
            logger.info("Не авторизованы, запускаем процесс авторизации...")
            phone_number = input("Введите номер телефона: ")
            await client.send_code_request(phone_number)

            try:
                code = input('Введите код из Telegram: ')
                await client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                logger.info("Требуется пароль двухфакторной аутентификации:")
                password = input("Пароль: ")
                await client.sign_in(password=password)
            logger.info("Авторизация прошла успешно!")
        else:
            logger.info("Вы уже авторизованы!")

        # Пример использования клиента после авторизации (отправка сообщения самому себе)
        me = await client.get_me()
        await client.send_message(me.id, "Привет, это тестовое сообщение!")
        logger.info(f"Сообщение отправлено пользователю {me.username}!")

    except FloodWaitError as e:
        logger.error(f"Превышено количество попыток. Попробуйте снова через {e.seconds} секунд.")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
    finally:
        # Отключение клиента (важно для корректного сохранения сессии)
        await client.disconnect()

if __name__ == '__main__':
    # Запуск асинхронного цикла
    asyncio.run(main())
