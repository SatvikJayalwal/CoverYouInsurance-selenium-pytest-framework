from pages.login_page import LoginPage
from pages.dpi_claim_page import DPIClaimPage
import traceback


def test_dpi_claim(driver, wait):
    login = LoginPage(driver, wait)
    dpi_page = DPIClaimPage(driver, wait)

    try:
        login.load()
        login.login("claimuser2@coveryou.in", "12345678")
        dpi_page.navigate_to_add_request()
        dpi_page.submit_policy("4021/325238129/00/000")
        dpi_page.fill_request_details()
        dpi_page.dispose_claim()
        dpi_page.set_claim_intimation()
        dpi_page.click_save_next()
        dpi_page.fill_lawyer_details()
        dpi_page.fill_insurance_company_details()
        dpi_page.fill_case_details()
        dpi_page.update_status()
        
    except Exception as e:
        driver.save_screenshot("error_test_dpi_claim.png")
        traceback.print_exc()
        assert False, "Test failed due to an exception."




