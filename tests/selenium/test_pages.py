"""Selenium tests for page rendering and navigation."""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.selenium.conftest import BASE_URL


class TestHomepage:

    def test_homepage_headline_visible(self, driver, live_server):
        driver.get(f'{live_server}/')
        body = driver.find_element(By.TAG_NAME, 'body').text
        assert 'PRECISION' in body

    def test_homepage_play_now_button_links_to_segmentation(self, driver, live_server):
        driver.get(f'{live_server}/')
        play_btn = driver.find_element(By.PARTIAL_LINK_TEXT, 'PLAY NOW')
        assert '/segmentation' in play_btn.get_attribute('href')


class TestNavigation:

    def test_nav_contains_leaderboard_link(self, driver, live_server):
        driver.get(f'{live_server}/')
        nav_links = [a.text for a in driver.find_elements(By.CSS_SELECTOR, 'nav a')]
        assert 'Leaderboard' in nav_links

    def test_leaderboard_loads_when_authenticated(self, logged_in, live_server):
        logged_in.get(f'{live_server}/leaderboard')
        assert 'Global Ranking' in logged_in.find_element(By.TAG_NAME, 'body').text

    def test_leaderboard_has_global_and_friends_tabs(self, logged_in, live_server):
        logged_in.get(f'{live_server}/leaderboard')
        buttons = [b.text for b in logged_in.find_elements(By.CSS_SELECTOR, 'button')]
        assert 'GLOBAL' in buttons
        assert 'FRIENDS' in buttons
