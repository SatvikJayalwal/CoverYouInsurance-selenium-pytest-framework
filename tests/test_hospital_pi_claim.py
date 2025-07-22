from pages.login_page import LoginPage
from pages.hospital_pi_claim_page import HOSPITALPIClaimPage
import traceback


def test_hospital_pi_claim(driver, wait):
    login = LoginPage(driver, wait)
    hospital_pi_page = HOSPITALPIClaimPage(driver, wait)

    try:
        login.load()
        login.login("claimTelHPI@COVERYOU.IN", "12345678")
        hospital_pi_page.navigate_to_add_request()
        hospital_pi_page.submit_policy("4161/400012542/00/000")
        hospital_pi_page.fill_request_details()
        hospital_pi_page.dispose_claim()
        hospital_pi_page.set_claim_intimation()
        hospital_pi_page.click_save_next()
        hospital_pi_page.fill_lawyer_details()
        hospital_pi_page.fill_insurance_company_details()
        hospital_pi_page.fill_case_details()
        hospital_pi_page.update_status()
                
    except Exception as e:
        driver.save_screenshot("error_test_hospital_pi_claim.png")
        traceback.print_exc()
        assert False, "Test failed due to an exception."




