import sys
import configparser
import logging
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit,
                             QPushButton, QLabel, QToolTip, QMessageBox, QHBoxLayout)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt

# Настройка логгирования
logging.basicConfig(filename='password_change.log', level=logging.INFO)

class PasswordChanger(QWidget):
    def __init__(self):
        super().__init__()

        # Загрузка сохраненного логина из конфигурации
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Смена пароля')
        self.setFixedSize(550, 300)
        self.setWindowIcon(QIcon('ChangePass\\assets\\icon.png'))  # Иконка приложения

        # Основной layout
        main_layout = QVBoxLayout()

        # Создание и стилизация виджетов
        self.login_label = QLabel('Логин:')
        self.login_label.setFont(QFont('Arial', 12))
        self.login_icon = QLabel()
        self.login_icon.setPixmap(QPixmap('ChangePass\\assets\\login_icon.png').scaled(16, 16))
        self.login_icon.setToolTip('Введите ваш логин, пример: "sp\\ivanov"')
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText('логин')
        self.login_input.setText(self.config.get('User', 'login', fallback=''))
        self.login_input.setFont(QFont('Arial', 12))

        self.old_password_label = QLabel('Старый пароль:')
        self.old_password_label.setFont(QFont('Arial', 12))
        self.old_password_icon = QLabel()
        self.old_password_icon.setPixmap(QPixmap('ChangePass\\assets\\old_password_icon.png').scaled(16, 16))
        self.old_password_icon.setToolTip('Введите ваш старый пароль')
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.Password)
        self.old_password_input.setFont(QFont('Arial', 12))

        self.new_password_label = QLabel('Новый пароль:')
        self.new_password_label.setFont(QFont('Arial', 12))
        self.new_password_icon = QLabel()
        self.new_password_icon.setPixmap(QPixmap('ChangePass\\assets\\new_password_icon.png').scaled(16, 16))
        self.new_password_icon.setToolTip('Введите новый пароль.')
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setFont(QFont('Arial', 12))

        self.confirm_password_label = QLabel('Подтверждение нового пароля:')
        self.confirm_password_label.setFont(QFont('Arial', 12))
        self.confirm_password_icon = QLabel()
        self.confirm_password_icon.setPixmap(QPixmap('ChangePass\\assets\\confirm_password_icon.png').scaled(16, 16))
        self.confirm_password_icon.setToolTip('Подтвердите новый пароль')
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setFont(QFont('Arial', 12))

        # Кнопки с иконками
        self.submit_btn = QPushButton('Отправить')
        self.submit_btn.setIcon(QIcon('ChangePass\\assets\\submit_icon.png'))
        self.submit_btn.setFont(QFont('Arial', 12))
        self.submit_btn.clicked.connect(self.change_password)

        self.cancel_btn = QPushButton('Отмена')
        self.cancel_btn.setIcon(QIcon('ChangePass\\assets\\cancel_icon.png'))
        self.cancel_btn.setFont(QFont('Arial', 12))
        self.cancel_btn.clicked.connect(self.close)

        # Лэйауты для размещения виджетов
        def create_field_layout(label, icon, input_field):
            layout = QHBoxLayout()
            layout.addWidget(label)
            layout.addWidget(icon)
            layout.addWidget(input_field)
            return layout

        main_layout.addLayout(create_field_layout(self.login_label, self.login_icon, self.login_input))
        main_layout.addLayout(create_field_layout(self.old_password_label, self.old_password_icon, self.old_password_input))
        main_layout.addLayout(create_field_layout(self.new_password_label, self.new_password_icon, self.new_password_input))
        main_layout.addLayout(create_field_layout(self.confirm_password_label, self.confirm_password_icon, self.confirm_password_input))

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # Стилизация
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                background-color: #5cb85c;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4cae4c;
            }
            QPushButton#cancel_btn {
                background-color: #d9534f;
            }
            QPushButton#cancel_btn:pressed {
                background-color: #c9302c;
            }
        """)

    def change_password(self):
        login = self.login_input.text()
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if new_password != confirm_password:
            QMessageBox.warning(self, 'Ошибка', 'Новый пароль и подтверждение не совпадают')
            return

        # Сохранение логина в конфигурационный файл
        self.config['User'] = {'login': login}
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

        # Логгирование попытки смены пароля
        logging.info(f'Попытка смены пароля для пользователя {login}')

        try:
            self.send_password_change_request(login, old_password, new_password)
            QMessageBox.information(self, 'Успех', 'Пароль успешно изменен')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось изменить пароль: {e}')

    def send_password_change_request(self, login, old_password, new_password):
        session = requests.Session()
        # Загрузка страницы для получения cookies
        url = 'https://change.snackprod.com/RDWeb/Pages/ua-UA/password.aspx'
        session.get(url)

        # Подготовка данных для отправки
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
            raise Exception('Ошибка при смене пароля')

# Основной запуск приложения
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PasswordChanger()
    ex.show()  # Убедитесь, что вызов show() происходит здесь
    sys.exit(app.exec_())
