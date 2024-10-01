from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import psutil

class PasswordChanger:
    def __init__(self):
        # Настройки для работы с Selenium
        self.options = Options()
        self.options.add_argument("--headless")  # Запуск браузера в фоновом режиме
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")

        # Инициализация драйвера
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

    def change_password(self, domain_user, current_password, new_password):
        # Проверка системных ресурсов перед сменой пароля
        resource_check = self.check_system_resources()
        if resource_check != "Системные ресурсы в порядке.":
            return resource_check

        # Проверка пароля на сложность
        if not self.validate_password(new_password):
            return "Пароль не соответствует требованиям безопасности."

        # Открытие страницы для изменения пароля
        self.driver.get("https://change.snackprod.com/RDWeb/Pages/ua-UA/password.aspx")

        # Ожидание загрузки страницы
        time.sleep(2)

        # Ввод данных в поля формы
        domain_user_input = self.driver.find_element(By.ID, "DomainUserName")
        domain_user_input.send_keys(domain_user)

        current_password_input = self.driver.find_element(By.ID, "UserPass")
        current_password_input.send_keys(current_password)

        new_password_input = self.driver.find_element(By.ID, "NewUserPass")
        new_password_input.send_keys(new_password)

        confirm_password_input = self.driver.find_element(By.ID, "ConfirmNewUserPass")
        confirm_password_input.send_keys(new_password)

        # Отправка формы
        submit_button = self.driver.find_element(By.ID, "btnSignIn")
        submit_button.click()

        # Ожидание результата
        time.sleep(2)

        # Проверка успешности смены пароля
        try:
            success_message = self.driver.find_element(By.ID, "tr1").text
            if "Ваш пароль успішно змінено" in success_message:
                return "Пароль успешно изменен."
            else:
                return "Произошла ошибка при смене пароля."
        except Exception as e:
            return f"Не удалось проверить успешность смены пароля: {str(e)}"

    def validate_password(self, password):
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    def check_system_resources(self):
        # Проверка минимальных системных ресурсов
        memory_info = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()

        # Проверка на достаточное количество оперативной памяти
        if memory_info.available < 1 * 1024 * 1024 * 1024:  # Меньше 1 ГБ
            return "Доступно недостаточно оперативной памяти."

        # Проверка на количество ядер CPU
        if cpu_count < 2:
            return "Обратите внимание, что на вашем устройстве недостаточно процессорных ядер для оптимальной работы."

        return "Системные ресурсы в порядке."

    def close(self):
        # Закрытие браузера
        self.driver.quit()
