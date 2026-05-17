"""
Selenium test fixtures.

The Flask server runs as a subprocess so it gets its own Python process and
reads the real .env config (production DB already seeded with liver CT data).
This avoids any config-sharing conflict with the in-memory DB used by unit tests.

Run Selenium tests separately:
    pytest tests/selenium/ -v
"""
import os
import subprocess
import sys
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

PORT     = 5055
BASE_URL = f'http://localhost:{PORT}'

SEL_EMAIL    = 'selenium_tester@example.com'
SEL_PASSWORD = 'SeleniumTest1!'

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(scope='session')
def live_server():
    env = {**os.environ, 'FLASK_APP': 'app', 'FLASK_DEBUG': '0'}
    proc = subprocess.Popen(
        [sys.executable, '-m', 'flask', 'run', '--port', str(PORT), '--no-reload'],
        cwd=PROJECT_DIR,
        env=env,
    )
    time.sleep(2)  # wait for server to be ready
    yield BASE_URL
    proc.terminate()
    proc.wait()


@pytest.fixture(scope='session')
def driver(live_server):
    opts = Options()
    opts.add_argument('--headless')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--window-size=1920,1080')
    d = webdriver.Chrome(options=opts)
    d.implicitly_wait(5)
    yield d
    d.quit()


@pytest.fixture(scope='session')
def registered_user(driver, live_server):
    """Ensure the Selenium test user exists by registering via the UI."""
    driver.get(f'{live_server}/login')
    driver.find_element(By.ID, 'newname').send_keys(SEL_EMAIL)
    driver.find_element(By.ID, 'newpassword').send_keys(SEL_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, 'form#new button[type="submit"]').click()
    # Wait briefly — either we land on homepage (registered) or stay on login (already exists)
    time.sleep(1)
    return {'email': SEL_EMAIL, 'password': SEL_PASSWORD}


@pytest.fixture(autouse=True)
def clear_cookies(driver):
    """Reset auth state before every test so session doesn't bleed between tests."""
    driver.delete_all_cookies()
    yield


@pytest.fixture()
def logged_in(driver, live_server, registered_user):
    """Navigate to login and authenticate before each test that needs it."""
    driver.delete_all_cookies()
    driver.get(f'{live_server}/login')
    driver.find_element(By.ID, 'username').clear()
    driver.find_element(By.ID, 'username').send_keys(registered_user['email'])
    driver.find_element(By.ID, 'userpassword').clear()
    driver.find_element(By.ID, 'userpassword').send_keys(registered_user['password'])
    driver.find_element(By.CSS_SELECTOR, 'form#user button[type="submit"]').click()
    WebDriverWait(driver, 8).until(EC.url_changes(f'{live_server}/login'))
    return driver
