from cx_Freeze import setup, Executable
import os
import PyQt5.QtCore

# Получение путей к QML2 и плагинам Qt
qml_imports_path = os.path.join(PyQt5.QtCore.QLibraryInfo.location(PyQt5.QtCore.QLibraryInfo.Qml2ImportsPath))
qt_plugins_path = os.path.join(PyQt5.QtCore.QLibraryInfo.location(PyQt5.QtCore.QLibraryInfo.PluginsPath))

# Определение файлов и папок для включения в сборку
include_files = [
    'main.py',
    'password_logic.py',
    (qml_imports_path, 'qml'),  # Включение пути к QML2 библиотекам
    (qt_plugins_path, 'qt/plugins')  # Включение пути к плагинам Qt
]

# Опции сборки
build_exe_options = {
    'packages': ['os', 're', 'platform', 'psutil', 'PyQt5'],  # Необходимые пакеты
    'excludes': ['tkinter', 'PyQt5.QtQml', 'PyQt5.QtQuick'],  # Исключение ненужных пакетов (например, Tkinter)
    'include_files': include_files,  # Включенные дополнительные файлы и папки
    'optimize': 2  # Оптимизация кода
}

# Определение исполняемого файла
executables = [
    Executable(
        script='main.py',  # Основной скрипт приложения
        base='Win32GUI' if os.name == 'nt' else None,  # Использование 'Win32GUI' для оконных приложений на Windows
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
