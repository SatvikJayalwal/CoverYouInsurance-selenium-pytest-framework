import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()   

@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 10)
