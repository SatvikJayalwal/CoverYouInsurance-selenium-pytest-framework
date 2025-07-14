import time
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

def safe_click(driver, locator_func, timeout=10):
    """Safely clicks an element using JS after waiting for it and scrolling into view."""
    end = time.time() + timeout
    while time.time() < end:
        try:
            element = locator_func(driver)
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            driver.execute_script("arguments[0].click();", element)
            return
        except StaleElementReferenceException:
            time.sleep(0.5)
    raise TimeoutException("Element not clickable after retries")

def js_click(driver, selector, timeout=10):
    """Click element using JavaScript by CSS selector."""
    end = time.time() + timeout
    while time.time() < end:
        el = driver.execute_script(f"return document.querySelector('{selector}');")
        if el:
            driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", el)
            return
        time.sleep(0.5)
    raise TimeoutException(f"Element {selector} not clickable in time")
