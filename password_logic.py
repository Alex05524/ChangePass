import re
from requests.exceptions import RequestException
try:
    import requests
except ImportError:
    requests = None

class PasswordChanger:
    def __init__(self, username, old_password, new_password):
        self.username = username
        self.old_password = old_password
        self.new_password = new_password
        self.session = None

    def change_password(self):
        try:
            import requests
            from requests.exceptions import RequestException
        except Exception:
            return "Сетевая библиотека недоступна. Установите requests."

        if self.session is None:
            self.session = requests.Session()

        url = "https://change.snackprod.com/RDWeb/Pages/ua-UA/password.aspx"
        payload = {
            'DomainUserName': self.username,
            'UserPass': self.old_password,
            'NewUserPass': self.new_password,
            'ConfirmNewUserPass': self.new_password
        }
        try:
            resp = self.session.post(url, data=payload, timeout=15)
            if resp.status_code == 200:
                return self.handle_response(resp.text)
            return f"Ошибка запроса: код {resp.status_code}"
        except RequestException as e:
            return f"Ошибка сети: {e}"

    def handle_response(self, html: str):
        if "Ваш пароль успішно змінено." in html:
            return "Пароль успешно изменён."
        if "Введите новый пароль." in html:
            return "Введите новый пароль."
        if "Новий пароль не відповідає вимогам домену" in html or "Новий пароль не відповідає вимогам" in html:
            return "Новый пароль не соответствует требованиям домена. Выберите другой."
        if "Введені паролі не збігаються." in html:
            return "Пароли не совпадают."
        if "Ви ввели неприпустиме ім'я користувача або пароль" in html:
            return "Неправильное имя пользователя или пароль. Повторите ввод."
        if "Ваш пароль неможливо змінити. Зверніться за допомогою до адміністратора." in html:
            return "Пароль невозможно изменить. Обратитесь к администратору."
        if "Ошибка: не удалось отобразить веб-доступ к удаленным рабочим столам." in html:
            return "Ошибка отображения страницы. Попробуйте позже или обратитесь к администратору."

        m = re.search(r'<span class="wrng">(.+?)</span>', html, re.S)
        if m:
            raw = m.group(1)
            if "успішно змінено" in raw:
                return "Пароль успешно изменён."
            if "не відповідає вимогам" in raw:
                return "Новый пароль не соответствует требованиям."
            if "не збігаються" in raw:
                return "Пароли не совпадают."
            if "ім'я користувача або пароль" in raw or "ім\u0027я користувача або пароль" in raw:
                return "Неправильное имя пользователя или пароль."
            return raw

        return "Неизвестная ошибка при смене пароля."
