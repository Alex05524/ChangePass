import os
import configparser
import logging
import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt
from ChangePass.admin_panel import AdminPanel

logging.basicConfig(filename='password_change.log', level=logging.INFO)

ADMIN_LOGIN = 'admin'

class PasswordChanger(QWidget):
    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Смена пароля')
        self.setFixedSize(600, 350)
        self.setWindowIcon(QIcon(self.resource_path('assets/icon.png')))
        
        # Set dark background color
        self.setStyleSheet("background-color: #2a2e38;")

        main_layout = QVBoxLayout()

        self.login_label, self.login_icon, self.login_input = self.create_input_with_icon(
            'Логин:', 'assets/login_icon.png', 'Введите ваш логин', self.config.get('User', 'login', fallback='')
        )
        self.old_password_label, self.old_password_icon, self.old_password_input = self.create_password_input_with_icon(
            'Старый пароль:', 'assets/old_password_icon.png', 'Введите ваш старый пароль'
        )
        self.new_password_label, self.new_password_icon, self.new_password_input = self.create_password_input_with_icon(
            'Новый пароль:', 'assets/new_password_icon.png', 'Введите новый пароль.'
        )
        self.confirm_password_label, self.confirm_password_icon, self.confirm_password_input = self.create_password_input_with_icon(
            'Подтверждение нового пароля:', 'assets/confirm_password_icon.png', 'Подтвердите новый пароль'
        )

        self.submit_btn = self.create_button_with_icon('Отправить', 'assets/submit_icon.png', self.change_password)
        self.cancel_btn = self.create_button_with_icon('Отмена', 'assets/cancel_icon.png', self.close, object_name='cancel_btn')

        widgets = [
            (self.login_label, self.login_icon, self.login_input),
            (self.old_password_label, self.old_password_icon, self.old_password_input),
            (self.new_password_label, self.new_password_icon, self.new_password_input),
            (self.confirm_password_label, self.confirm_password_icon, self.confirm_password_input)
        ]
        for widget in widgets:
            main_layout.addLayout(self.create_field_layout(*widget))

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        self.set_styles()

    def create_field_layout(self, label, icon, input_field):
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(icon)
        layout.addWidget(input_field)
        return layout

    def create_input_with_icon(self, label_text, icon_path, tooltip_text, default_text=''):
        label = QLabel(label_text)
        label.setFont(QFont('Arial', 12))
        label.setStyleSheet("color: #ffffff;")

        icon = QLabel()
        icon.setPixmap(QPixmap(self.resource_path(icon_path)).scaled(18, 18))
        icon.setToolTip(tooltip_text)

        input_field = QLineEdit()
        input_field.setPlaceholderText(label_text.lower())
        input_field.setText(default_text)
        input_field.setFont(QFont('Arial', 12))
        input_field.setStyleSheet("""
            background-color: #383e4a;
            color: #dfe6ed;
            padding: 5px;
            border: 1px solid #555;
            border-radius: 6px;
        """)

        return label, icon, input_field

    def create_password_input_with_icon(self, label_text, icon_path, tooltip_text):
        label, icon, input_field = self.create_input_with_icon(label_text, icon_path, tooltip_text)
        input_field.setEchoMode(QLineEdit.Password)
        return label, icon, input_field

    def create_button_with_icon(self, button_text, icon_path, callback, object_name=None):
        button = QPushButton(button_text)
        button.setIcon(QIcon(self.resource_path(icon_path)))
        button.setFont(QFont('Arial', 12))
        button.clicked.connect(callback)
        button.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                padding: 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
            QPushButton:pressed {
                background-color: #3d8b3d;
            }
            QPushButton#cancel_btn {
                background-color: #d9534f;
            }
            QPushButton#cancel_btn:hover {
                background-color: #c9302c;
            }
        """)
        if object_name:
            button.setObjectName(object_name)
        return button

    def set_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2a2e38;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #555;
                border-radius: 6px;
                background-color: #383e4a;
                color: #dfe6ed;
            }
        """)

    def resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def change_password(self):
        login = self.login_input.text()
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if login == ADMIN_LOGIN:
            self.open_admin_panel()
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, 'Ошибка', 'Новый пароль и подтверждение не совпадают')
            return

        self.config['User'] = {'login': login}
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

        logging.info(f'Попытка смены пароля для пользователя {login}')

        try:
            self.send_password_change_request(login, old_password, new_password)
            QMessageBox.information(self, 'Успех', 'Пароль успешно изменен')
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить пароль: {e}')

    def send_password_change_request(self, login, old_password, new_password):
        session = requests.Session()
        url = 'https://change.snackprod.com/RDWeb/Pages/ua-UA/password.aspx'
        session.get(url)

        payload = {
            'DomainUserName': f'sp\\{login}',
            'UserPass': old_password,
            'NewUserPass': new_password,
            'ConfirmNewUserPass': new_password
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = session.post(url, data=payload, headers=headers)

        if response.status_code != 200:
            logging.error(f'Ошибка при смене пароля: {response.text}')
            raise requests.exceptions.RequestException('Ошибка при смене пароля')

    def open_admin_panel(self):
        admin_dialog = AdminPanel(self)
        admin_dialog.exec_()
