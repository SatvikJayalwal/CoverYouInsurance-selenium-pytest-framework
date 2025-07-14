from pages.login_page import LoginPage
from pages.motor_claim_page import MotorClaimPage
import traceback


def test_motor_claim(driver, wait):
    login = LoginPage(driver, wait)
    motor_page = MotorClaimPage(driver, wait)

    try:
        login.load()
        login.login("claimmotoruser@coveryou.in", "12345678")
        motor_page.navigate_to_add_request()
        motor_page.submit_policy("3001/O/396658184/00/000")
        motor_page.fill_request_details()
        motor_page.dispose_claim()
        motor_page.set_claim_intimation()
        motor_page.click_save_next()
        motor_page.fill_rc_details()
        motor_page.fill_surveyor_details()
        motor_page.fill_commercial_details()
        motor_page.fill_driver_details()
        motor_page.fill_accident_details()
        motor_page.fill_garage_details()
    except Exception as e:
        driver.save_screenshot("error_test_motor_claim.png")
        traceback.print_exc()
        assert False, "Test failed due to an exception."




