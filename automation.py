from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import logging

def change_password_via_selenium(login, old_password, new_password):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Запуск браузера в фоновом режиме

    service = Service('path_to_chromedriver')  # Укажите путь к chromedriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get('https://change.snackprod.com/RDWeb/Pages/ua-UA/password.aspx')

        # Ввод логина
        login_input = driver.find_element(By.ID, 'login_field')
        login_input.send_keys(f'sp\\{login}')

        # Ввод старого пароля
        old_password_input = driver.find_element(By.ID, 'old_password_field')
        old_password_input.send_keys(old_password)

        # Ввод нового пароля
        new_password_input = driver.find_element(By.ID, 'new_password_field')
        new_password_input.send_keys(new_password)

        # Ввод подтверждения нового пароля
        confirm_password_input = driver.find_element(By.ID, 'confirm_password_field')
        confirm_password_input.send_keys(new_password)

        # Отправка формы
        submit_btn = driver.find_element(By.ID, 'submit_button')
        submit_btn.click()

        # Ожидание и проверка результата
        time.sleep(5)
        # Здесь можно добавить проверку успешного завершения операции

    except Exception as e:
        logging.error(f'Ошибка при смене пароля: {e}')
        raise
    finally:
        driver.quit()
