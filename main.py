from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QCheckBox, QDialog, QMessageBox, QShortcut
)
from PyQt5 import QtCore
from PyQt5.QtGui import QKeySequence, QIcon
import os, sys, re, ctypes
try:
    import resources_rc  # ресурсы Qt (если есть resources.qrc -> resources_rc.py)
except ImportError:
    resources_rc = None
from password_logic import PasswordChanger

def resource_path(rel_path: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)

def get_app_icon() -> QIcon:
    # 1) QRC-ресурсы
    for res in (":/assets/lock.ico", ":/assets/lock.png"):
        ic = QIcon(res)
        if not ic.isNull():
            return ic
    # 2) Файлы рядом/в _MEIPASS
    for rel in ("assets/lock.ico", "assets/lock.png"):
        full = resource_path(rel)
        if os.path.exists(full):
            ic = QIcon(full)
            if not ic.isNull():
                return ic
    return QIcon()

class PasswordHistoryDialog(QDialog):
    def __init__(self, previous_passwords):
        super().__init__()
        self.setWindowTitle("История паролей")
        self.setGeometry(100, 100, 300, 200)
        layout = QVBoxLayout()
        self.label = QLabel("Ранее использованные пароли:")
        layout.addWidget(self.label)
        for password in previous_passwords:
            layout.addWidget(QLabel(password))
        self.setLayout(layout)

def _available_ram_gb() -> float:
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]
    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    return stat.ullAvailPhys / (1024**3)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Смена пароля")

        # Иконка окна — сначала из файла assets/lock.ico, затем из ресурса :/assets/lock.ico
        ico_fs = resource_path(r"assets\lock.ico")
        icon = QIcon(ico_fs) if os.path.exists(ico_fs) else QIcon(":/assets/lock.ico")
        if not icon.isNull():
            self.setWindowIcon(icon)

        self.setGeometry(100, 100, 400, 300)
        self.previous_passwords = []
        # Предупреждение при низком объёме свободной памяти (< 512 МБ)
        try:
            if _available_ram_gb() < 0.5:
                QMessageBox.warning(
                    self,
                    "Недостаточно памяти",
                    "На этом ПК менее 512 МБ свободной ОЗУ. Возможны задержки работы."
                )
        except Exception:
            pass
        self.initUI()
        self.setStyle()

    def change_password(self):
        login = self.input_login.text().strip()
        old_password = self.input_old_password.text()
        new_password = self.input_new_password.text()
        confirm_password = self.input_confirm_password.text()

        # Нормализуем логин: добавляем префикс sp\ если его нет
        def normalize_login(u: str) -> str:
            u = u.strip()
            # если уже введено sp\user — не трогаем
            if u.lower().startswith("sp\\"):
                return u
            return f"sp\\{u}"

        login_prefixed = normalize_login(login)

        # Проверка на длину пароля и его сложность
        if self.validate_new_password(new_password, confirm_password):
            changer = PasswordChanger(login_prefixed, old_password, new_password)
            success = changer.change_password()
            if success:
                self.previous_passwords.append(new_password)
                QMessageBox.information(self, "Успех", "Пароль успешно изменен.")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось изменить пароль. Проверьте данные.")

    def initUI(self):
        layout = QVBoxLayout()

        self.label_login = QLabel("Логин:")
        layout.addWidget(self.label_login)

        self.input_login = QLineEdit()
        self.input_login.setText("sp\\")  # префикс при старте
        layout.addWidget(self.input_login)

        self.label_old_password = QLabel("Старый пароль:")
        layout.addWidget(self.label_old_password)

        self.input_old_password = QLineEdit()
        self.input_old_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_old_password)

        self.label_new_password = QLabel("Новый пароль:")
        layout.addWidget(self.label_new_password)

        self.input_new_password = QLineEdit()
        self.input_new_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_new_password)

        self.label_confirm_password = QLabel("Подтверждение нового пароля:")
        layout.addWidget(self.label_confirm_password)

        self.input_confirm_password = QLineEdit()
        self.input_confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_confirm_password)

        self.show_passwords_checkbox = QCheckBox("Показать пароли")
        self.show_passwords_checkbox.stateChanged.connect(self.toggle_all_passwords_visibility)
        layout.addWidget(self.show_passwords_checkbox)

        self.history_button = QPushButton("История паролей")
        self.history_button.clicked.connect(self.show_password_history)
        layout.addWidget(self.history_button)

        self.submit_button = QPushButton("Изменить пароль")
        self.submit_button.clicked.connect(self.change_password)
        layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.close)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)
        self.setShortcut()

    def setShortcut(self):
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        shortcut.activated.connect(self.open_admin_panel)

    def open_admin_panel(self):
        QMessageBox.information(self, "Админ-панель", "Функционал админ-панели не реализован.")

    def toggle_all_passwords_visibility(self, state):
        mode = QLineEdit.Normal if state == QtCore.Qt.Checked else QLineEdit.Password
        self.input_old_password.setEchoMode(mode)
        self.input_new_password.setEchoMode(mode)
        self.input_confirm_password.setEchoMode(mode)

    def change_password(self):
        login = self.input_login.text().strip()
        old_password = self.input_old_password.text()
        new_password = self.input_new_password.text()
        confirm_password = self.input_confirm_password.text()

        # Префикс без дублирования
        if not login.lower().startswith("sp\\"):
            login = f"sp\\{login}"

        if self.validate_new_password(new_password, confirm_password):
            changer = PasswordChanger(login, old_password, new_password)
            result = changer.change_password()
            if isinstance(result, str):
                if "успешно" in result:
                    self.previous_passwords.append(new_password)
                    QMessageBox.information(self, "Результат", result)
                else:
                    QMessageBox.warning(self, "Ошибка", result)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось изменить пароль. Проверьте данные.")

    def validate_new_password(self, new_password, confirm_password):
        if len(new_password) < 8:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 8 символов.")
            return False
        if not re.search(r"[A-Z]", new_password):
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать хотя бы одну заглавную букву.")
            return False
        if not re.search(r"[a-z]", new_password):
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать хотя бы одну строчную букву.")
            return False
        if not re.search(r"[0-9]", new_password):
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать хотя бы одну цифру.")
            return False
        if new_password in self.previous_passwords:
            QMessageBox.warning(self, "Ошибка", "Пароль уже использовался ранее. Пожалуйста, выберите другой.")
            return False
        if new_password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return False
        return True

    def show_password_history(self):
        dlg = PasswordHistoryDialog(self.previous_passwords)
        dlg.exec_()

    def setStyle(self):
        self.setStyleSheet(""" 
            QWidget {
                background-color: #2e2e2e;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }
            QLabel { font-size: 14px; }
            QLineEdit {
                background-color: #3e3e3e;
                border: 1px solid #0078d7;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d7;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #0056a3; }
        """)

if __name__ == '__main__':
    app = QApplication([])

    # Иконка приложения (таскбар) — тот же assets/lock.ico
    app_ico_fs = resource_path(r"assets\lock.ico")
    app_icon = QIcon(app_ico_fs) if os.path.exists(app_ico_fs) else QIcon(":/assets/lock.ico")
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    window = MainWindow()
    window.show()
    app.exec_()
