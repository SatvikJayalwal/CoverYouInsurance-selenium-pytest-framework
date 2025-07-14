from selenium.webdriver.common.by import By
from utils.helpers import safe_click

class LoginPage:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def load(self):
        self.driver.get("https://claims.netcrm.in/")

    def login(self, email, password):
        self.wait.until(lambda d: d.find_element(By.ID, "email")).send_keys(email)
        self.driver.find_element(By.ID, "login_password_id").send_keys(password)
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//button[@type='submit']"))
