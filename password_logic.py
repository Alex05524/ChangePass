import logging
import requests

logging.basicConfig(filename='password_change.log', level=logging.INFO)

class PasswordChangerLogic:
    def __init__(self, config):
        self.config = config

    def change_password(self, login, old_password, new_password, confirm_password):
        if new_password != confirm_password:
            return False, 'Пароли не совпадают'

        self.config['User'] = {'login': login}
        self.config.save()

        logging.info(f'Попытка смены пароля для пользователя {login}')

        try:
            self.send_password_change_request(login, old_password, new_password)
            return True, 'Пароль успешно изменен'
        except requests.exceptions.RequestException as e:
            return False, f'Ошибка при смене пароля: {e}'

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
