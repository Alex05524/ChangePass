from cx_Freeze import setup, Executable
import os

# Определите, какие файлы и папки включить в сборку
include_files = [
    'admin_panel.py',  # Включить файл automation.py
    'config_manager.py',
    'main.py',
    'password_logic.py',
    'ui_module.py',
]

# Опции сборки
build_exe_options = {
    'packages': ['os', 're', 'platform', 'psutil', 'PyQt5'],  # Необходимые пакеты
    'excludes': ['tkinter'],  # Исключить ненужные пакеты (например, Tkinter, если он не используется)
    'include_files': include_files,  # Включенные дополнительные файлы и папки
    'optimize': 2  # Оптимизация кода (можно 0, 1 или 2)
}

# Определение исполняемого файла
executables = [
    Executable(
        script='main.py',  # Основной скрипт вашего приложения
        base='Win32GUI' if os.name == 'nt' else None,  # Используйте 'Win32GUI' для оконных приложений на Windows
        target_name='ChangePass.exe',  # Имя создаваемого исполняемого файла
    )
]

# Настройка сборки
setup(
    name='ChangePass',
    version='1.0',
    description='Приложение для смены пароля',
    options={'build_exe': build_exe_options},
    executables=executables
)

# Вывод информации о текущей директории и файлах в ней
print("Current directory:", os.getcwd())
print("Files in current directory:", os.listdir(os.getcwd()))
