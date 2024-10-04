import os
import sys
import configparser
import logging
import requests
from PyQt5.QtWidgets import QMessageBox

# Настройка логгирования
logging.basicConfig(filename='password_change.log', level=logging.INFO)

class PasswordChanger:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def change_password(self, login, old_password, new_password, confirm_password):
        if not self.validate_inputs(login, old_password, new_password, confirm_password):
            return
        
        self.config['User'] = {'login': login}
        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

        logging.info(f'Попытка смены пароля для пользователя {login}')

        try:
            self.send_password_change_request(login, old_password, new_password)
            return True  # Успешное изменение пароля
        except requests.exceptions.RequestException as e:
            self.show_error(f'Не удалось изменить пароль: {e}')
            return False  # Ошибка при изменении пароля

    def validate_inputs(self, login, old_password, new_password, confirm_password):
        if not login or not old_password or not new_password or not confirm_password:
            self.show_warning('Ошибка', 'Все поля должны быть заполнены')
            return False
        if new_password != confirm_password:
            self.show_warning('Ошибка', 'Новый пароль и подтверждение не совпадают')
            return False
        return True

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

        if response.status_code != 200 or 'success' not in response.text.lower():
            logging.error(f'Ошибка при смене пароля: {response.text}')
            raise requests.exceptions.RequestException('Ошибка при смене пароля')

    def show_warning(self, title, message):
        QMessageBox.warning(None, title, message)

    def show_error(self, message):
        QMessageBox.critical(None, 'Ошибка', message)

# Пример использования
if __name__ == '__main__':
    password_changer = PasswordChanger()
    # Вы можете вызвать change_password здесь с нужными параметрами
