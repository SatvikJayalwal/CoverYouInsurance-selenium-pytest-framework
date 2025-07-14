from pages.login_page import LoginPage
from pages.health_claim_page import HealthClaimPage
import traceback

def test_health_claim(driver, wait):
    login = LoginPage(driver, wait)
    health_page = HealthClaimPage(driver, wait)

    try:
        login.load()
        login.login("claimteldhi@coveryou.in", "12345678")
        health_page.navigate_to_add_request()
        health_page.submit_policy("7000262119-00")
        health_page.fill_request_details()
        health_page.dispose_claim()
        health_page.set_claim_intimation()
        health_page.click_save_next()
        health_page.fill_hospitalized_details()
        health_page.fill_hospital_details()
        health_page.fill_neft_details()
        health_page.fill_insurance_details()
        health_page.fill_assessment_details()
        health_page.mark_as_paid()
    except Exception as e:
        driver.save_screenshot("error_test_health_claim.png")
        traceback.print_exc()
        assert False, "Test failed due to an exception."

