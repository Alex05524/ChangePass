from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QCheckBox, QDialog, QMessageBox, QShortcut
)
from PyQt5.QtGui import QKeySequence
from PyQt5 import QtCore
from admin_panel import AdminPanel
import re
import psutil


class PasswordHistoryDialog(QDialog):
    def __init__(self, previous_passwords):
        super().__init__()
        self.setWindowTitle("История паролей")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ранее использованные пароли:"))

        for password in previous_passwords:
            layout.addWidget(QLabel(password))

        self.setLayout(layout)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Смена пароля")
        self.setGeometry(100, 100, 400, 300)
        self.previous_passwords = []
        self.initUI()
        self.check_system_resources()

    def initUI(self):
        layout = QVBoxLayout()

        self.input_login = self.create_labeled_input(layout, "Логин:")
        self.input_old_password = self.create_labeled_input(layout, "Старый пароль:", True)
        self.input_new_password = self.create_labeled_input(layout, "Новый пароль:", True)
        self.input_confirm_password = self.create_labeled_input(layout, "Подтверждение нового пароля:", True)

        self.show_passwords_checkbox = QCheckBox("Показать пароли")
        self.show_passwords_checkbox.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_passwords_checkbox)

        self.create_button(layout, "История паролей", self.show_password_history)
        self.create_button(layout, "Изменить пароль", self.change_password)
        self.create_button(layout, "Отмена", self.close)

        self.setLayout(layout)
        self.setStyle()
        self.set_shortcut()

    def create_labeled_input(self, layout, label_text, is_password=False):
        layout.addWidget(QLabel(label_text))
        input_field = QLineEdit()
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        layout.addWidget(input_field)
        return input_field

    def create_button(self, layout, button_text, callback):
        button = QPushButton(button_text)
        button.clicked.connect(callback)
        layout.addWidget(button)

    def set_shortcut(self):
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        shortcut.activated.connect(self.open_admin_panel)

    def open_admin_panel(self):
        admin_panel = AdminPanel(self)
        admin_panel.exec_()

    def toggle_password_visibility(self, state):
        echo_mode = QLineEdit.Normal if state == QtCore.Qt.Checked else QLineEdit.Password
        self.input_old_password.setEchoMode(echo_mode)
        self.input_new_password.setEchoMode(echo_mode)
        self.input_confirm_password.setEchoMode(echo_mode)

    def change_password(self):
        old_password = self.input_old_password.text()
        new_password = self.input_new_password.text()
        confirm_password = self.input_confirm_password.text()

        if self.validate_new_password(new_password, confirm_password):
            self.previous_passwords.append(new_password)
            QMessageBox.information(self, "Успех", "Пароль успешно изменен.")
            # Здесь можно добавить логику для обновления пароля в системе

    def validate_new_password(self, new_password, confirm_password):
        if len(new_password) < 8:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 8 символов.")
            return False

        password_checks = [
            (r"[A-Z]", "Пароль должен содержать хотя бы одну заглавную букву."),
            (r"[a-z]", "Пароль должен содержать хотя бы одну строчную букву."),
            (r"[0-9]", "Пароль должен содержать хотя бы одну цифру."),
            (r"[!@#$%^&*(),.?\":{}|<>]", "Рекомендуется использовать специальные символы для повышения безопасности.")
        ]

        for pattern, message in password_checks:
            if not re.search(pattern, new_password):
                QMessageBox.warning(self, "Ошибка", message)
                return False

        if new_password in self.previous_passwords:
            QMessageBox.warning(self, "Ошибка", "Пароль уже использовался ранее. Пожалуйста, выберите другой.")
            return False

        if new_password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")
            return False

        return True

    def show_password_history(self):
        history_dialog = PasswordHistoryDialog(self.previous_passwords)
        history_dialog.exec_()

    def setStyle(self):
        self.setStyleSheet(""" 
            QWidget {
                background-color: #2e2e2e;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
            }
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
            QPushButton:hover {
                background-color: #0056a3;
            }
        """)

    def check_system_resources(self):
        memory_info = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()

        if memory_info.available < 2 * 1024 * 1024 * 1024:  # Меньше 2 ГБ
            QMessageBox.warning(self, "Предупреждение", "Доступно недостаточно оперативной памяти. Некоторые функции могут быть ограничены.")

        if cpu_count < 2:
            QMessageBox.warning(self, "Предупреждение", "Обратите внимание, что на вашем устройстве недостаточно процессорных ядер для оптимальной работы.")


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
