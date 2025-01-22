import os
import shutil
import subprocess
import sys

# Путь, где файл должен находиться (домашняя директория Termux)
target_path = os.path.expanduser("~") + "/Mer.py"

# Проверка текущего местоположения файла
current_path = os.path.abspath(__file__)

# Функция для перемещения файла в целевую директорию
def move_self():
    try:
        if current_path != target_path:
            print(f"Перемещаем файл из {current_path} в {target_path}...")
            shutil.move(current_path, target_path)
            print("Файл успешно перемещён. Пожалуйста, запустите его снова из Termux.")
            sys.exit()  # Завершаем выполнение после перемещения
        else:
            print("Файл уже находится в целевой директории.")
    except Exception as e:
        print(f"Ошибка при перемещении файла: {e}")

# Функция для установки зависимостей
def install_dependencies():
    try:
        print("Проверяем наличие библиотеки 'requests'...")
        import requests
        print("Библиотека 'requests' уже установлена.")
    except ImportError:
        print("Библиотека 'requests' не найдена. Устанавливаем...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("Библиотека 'requests' успешно установлена.")

# Основная задача
def main_task():
    print("Запускаем основную логику скрипта...")
    try:
        import requests
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            print("Интернет соединение активно.")
        else:
            print("Не удалось подключиться к интернету.")
    except requests.ConnectionError:
        print("Нет подключения к интернету.")

# Основная логика
def main():
    # Перемещаем файл, если требуется
    move_self()

    # Устанавливаем зависимости
    install_dependencies()

    # Выполняем основную задачу
    main_task()

if __name__ == "__main__":
    main()

