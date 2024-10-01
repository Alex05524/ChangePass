from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QColorDialog, QFontDialog, QInputDialog, QMessageBox, QShortcut, QCheckBox, QDialog
from PyQt5.QtGui import QKeySequence, QFont  # Добавьте QFont сюда
from PyQt5 import QtCore
from admin_panel import AdminPanel
from password_logic import PasswordChanger
import re
import platform
import psutil  # Убедитесь, что psutil установлен

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

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Смена пароля")
        self.setGeometry(100, 100, 400, 300)
        self.password_visible = False
        self.auto_resize_enabled = True
        self.previous_passwords = []  # Список для хранения ранее использованных паролей
        self.default_bg_color = "#2e2e2e"  # Цвет фона по умолчанию
        self.default_font = "Arial"  # Шрифт по умолчанию
        self.check_system_resources()  # Проверка системных ресурсов
        self.initUI()
        self.setStyle()
        
    def change_font(self, font):
        """Метод для изменения шрифта интерфейса."""
        self.setFont(font)

    def resize_interface(self, width, height):
        """Метод для изменения размера интерфейса."""
        self.resize(width, height)

    def initUI(self):
        layout = QVBoxLayout()

        self.label_login = QLabel("Логин:")
        layout.addWidget(self.label_login)

        self.input_login = QLineEdit()
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

        # Общий флажок для отображения паролей
        self.show_passwords_checkbox = QCheckBox("Показать пароли")
        self.show_passwords_checkbox.stateChanged.connect(self.toggle_all_passwords_visibility)
        layout.addWidget(self.show_passwords_checkbox)

        # Кнопка для просмотра истории паролей
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
        self.admin_panel = AdminPanel(self)
        self.admin_panel.exec_()

    def toggle_all_passwords_visibility(self, state):
        if state == QtCore.Qt.Checked:
            self.input_old_password.setEchoMode(QLineEdit.Normal)
            self.input_new_password.setEchoMode(QLineEdit.Normal)
            self.input_confirm_password.setEchoMode(QLineEdit.Normal)
        else:
            self.input_old_password.setEchoMode(QLineEdit.Password)
            self.input_new_password.setEchoMode(QLineEdit.Password)
            self.input_confirm_password.setEchoMode(QLineEdit.Password)

    def change_password(self):
        old_password = self.input_old_password.text()
        new_password = self.input_new_password.text()
        confirm_password = self.input_confirm_password.text()
        domain_user = f"Домен\\{self.input_login.text()}"  # Получение доменного пользователя из поля ввода

        # Проверка на длину пароля и его сложность
        if len(new_password) < 8:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 8 символов.")
            return
        if not re.search(r"[A-Z]", new_password):
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать хотя бы одну заглавную букву.")
            return
        if not re.search(r"[a-z]", new_password):
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать хотя бы одну строчную букву.")
            return
        if not re.search(r"[0-9]", new_password):
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать хотя бы одну цифру.")
            return
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
            QMessageBox.warning(self, "Предупреждение", "Рекомендуется использовать специальные символы для повышения безопасности.")

        # Проверка на совпадение с предыдущими паролями
        if new_password in self.previous_passwords:
            QMessageBox.warning(self, "Ошибка", "Пароль уже использовался ранее. Пожалуйста, выберите другой.")
            return

        if new_password == confirm_password:
            password_changer = PasswordChanger()  # Создание экземпляра PasswordChanger
            result_message = password_changer.change_password(domain_user, old_password, new_password)  # Вызов метода
            if "успешно" in result_message:
                self.previous_passwords.append(new_password)  # Сохраняем новый пароль
                QMessageBox.information(self, "Успех", result_message)
            else:
                QMessageBox.warning(self, "Ошибка", result_message)
        else:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают.")

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

    def reset_to_defaults(self):
        # Сброс всех настроек к значениям по умолчанию
        self.change_background_color(self.default_bg_color)
        self.setFont(QFont(self.default_font, 10))  # Устанавливаем шрифт по умолчанию
        self.previous_passwords.clear()
        QMessageBox.information(self, "Сброс настроек", "Настройки были сброшены к значениям по умолчанию.")

    def change_background_color(self, color):
        self.setStyleSheet(f"background-color: {color};")

    def check_system_resources(self):
        # Проверка минимальных системных ресурсов
        memory_info = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()

        # Проверка на достаточное количество оперативной памяти
        if memory_info.available < 2 * 1024 * 1024 * 1024:  # Меньше 2 ГБ
            QMessageBox.warning(self, "Предупреждение", "Доступно недостаточно оперативной памяти. Некоторые функции могут быть ограничены.")
        
        # Проверка на количество ядер CPU
        if cpu_count < 2:
            QMessageBox.warning(self, "Предупреждение", "Обратите внимание, что на вашем устройстве недостаточно процессорных ядер для оптимальной работы.")

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
