"""Selenium tests for authentication flows (login / register)."""
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.selenium.conftest import BASE_URL, SEL_EMAIL, SEL_PASSWORD


class TestLoginPage:

    def test_login_page_has_expected_form_fields(self, driver, live_server):
        driver.get(f'{live_server}/login')
        assert driver.find_element(By.ID, 'username')
        assert driver.find_element(By.ID, 'userpassword')

    def test_login_with_correct_credentials_redirects_to_homepage(
            self, driver, live_server, registered_user):
        driver.get(f'{live_server}/login')
        driver.find_element(By.ID, 'username').clear()
        driver.find_element(By.ID, 'username').send_keys(registered_user['email'])
        driver.find_element(By.ID, 'userpassword').clear()
        driver.find_element(By.ID, 'userpassword').send_keys(registered_user['password'])
        driver.find_element(By.CSS_SELECTOR, 'form#user button[type="submit"]').click()

        WebDriverWait(driver, 8).until(EC.url_changes(f'{live_server}/login'))
        assert driver.current_url == f'{live_server}/'

    def test_login_with_wrong_password_shows_error(self, driver, live_server, registered_user):
        driver.get(f'{live_server}/login')
        driver.find_element(By.ID, 'username').clear()
        driver.find_element(By.ID, 'username').send_keys(registered_user['email'])
        driver.find_element(By.ID, 'userpassword').clear()
        driver.find_element(By.ID, 'userpassword').send_keys('WrongPass999!')
        driver.find_element(By.CSS_SELECTOR, 'form#user button[type="submit"]').click()

        time.sleep(1)
        error_el = driver.find_element(By.ID, 'login_error')
        assert error_el.text != ''
