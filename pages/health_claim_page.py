from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from utils.helpers import safe_click
import time


class HealthClaimPage:
    def __init__(self, driver, wait):
        # Initialize with WebDriver and WebDriverWait
        self.driver = driver
        self.wait = wait

    def navigate_to_add_request(self):
        """Step 1: Navigate to the Add Request page under Claim Requests."""
        safe_click(self.driver, lambda d: self.wait.until(
            lambda d: d.find_element(By.XPATH, "//a[contains(@href,'claim-request')]//p[contains(text(),'Requests')]")))
        safe_click(self.driver, lambda d: self.wait.until(
            lambda d: d.find_element(By.XPATH, "//a[contains(@href,'claim-request/create') and contains(text(),'Add Request')]")))

    def submit_policy(self, policy_no):
        """Step 2: Submit policy number and perform search."""
        Select(self.wait.until(lambda d: d.find_element(By.ID, "poicy_fetch_by"))).select_by_value("1")
        self.wait.until(lambda d: d.find_element(By.ID, "policy_number")).send_keys(policy_no)
        safe_click(self.driver, lambda d: d.find_element(By.ID, "policy_number_search"))
        time.sleep(2)

    def fill_request_details(self):
        """Step 3: Fill in claim request details and submit the form."""
        Select(self.wait.until(lambda d: d.find_element(By.XPATH, "//select[@id='status']"))).select_by_value("2")
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//button[@id='create-claim-request-form-submit-btn-id']"))
        self.wait.until(lambda d: d.find_element(By.XPATH, "//a[contains(text(),'Dispose')]"))
        time.sleep(2)

    def dispose_claim(self):
        """Step 4: Dispose the claim by selecting disposition values and submitting."""
        dispose_btn = self.wait.until(lambda d: d.find_element(By.XPATH, "//a[contains(text(),'Dispose')]"))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dispose_btn)
        time.sleep(1)
        dispose_btn.click()
        time.sleep(1)

        main_disp = self.wait.until(lambda d: d.find_element(By.ID, "main_disposition"))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", main_disp)
        Select(main_disp).select_by_value("1")  # Connected

        def wait_for_sub_disposition(driver):
            try:
                sub_disp = driver.find_element(By.ID, "sub_disposition")
                if not sub_disp.is_enabled():
                    return False
                options = sub_disp.find_elements(By.TAG_NAME, "option")
                return any(opt.get_attribute("value") == "2" for opt in options)
            except:
                return False

        try:
            self.wait.until(wait_for_sub_disposition)
            sub_disp = self.driver.find_element(By.ID, "sub_disposition")
            Select(sub_disp).select_by_value("2")  # Query Resolved
        except TimeoutException:
            self.driver.save_screenshot("error_sub_disposition_timeout.png")
            raise Exception("Sub Disposition 'Query Resolved' not loaded in time")

        # Click follow-up checkbox and submit
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//label[@for='follow_up_initiated_by_agent']"))))
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@id='lead_dispostion_update_form_submit_btn_id']"))))

        print("✓ Disposition saved")
        self.wait.until(EC.invisibility_of_element_located(
            (By.XPATH, "//button[@id='lead_dispostion_update_form_submit_btn_id']")))
        time.sleep(2)

    def set_claim_intimation(self):
        """Step 5: Set claim status to 'Intimated' (value = 4)."""
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        try:
            element = self.wait.until(lambda d: d.find_element(By.XPATH, "//a[contains(@onclick,'update-claim-status-model-id')]"))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            self.driver.save_screenshot("error_update_claim_status_button.png")
            raise Exception("Update Claim Status button not clickable.") from e

        def dropdown_loaded(driver):
            try:
                dropdown = driver.find_element(By.ID, "claim_status_lead_view")
                return any(opt.get_attribute("value") == "4" for opt in dropdown.find_elements(By.TAG_NAME, "option"))
            except:
                return False

        self.wait.until(dropdown_loaded)

        self.driver.execute_script("""
            var select = document.getElementById('claim_status_lead_view');
            select.value = '4';
            var event = new Event('change', { bubbles: true });
            select.dispatchEvent(event);
        """)
        safe_click(self.driver, lambda d: d.find_element(By.ID, "update_status_claim_model_submit_btn"))
        time.sleep(2)

    def click_save_next(self):
        """Step 6: Click the 'Save & Next' button."""
        button = self.wait.until(lambda d: d.find_element(By.ID, "health_claim_create_first_form_btn_id"))
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
        time.sleep(1)

        if not button.is_displayed():
            self.driver.save_screenshot("error_save_next_invisible.png")
            raise Exception("Save & Next button is not visible")

        try:
            button.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", button)

        time.sleep(2)

    def mark_as_paid(self):
        """Step 7: Mark the claim status as Paid (value = 9)."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        safe_click(self.driver, lambda d: d.find_element(
            By.XPATH, "//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'update status')]"))

        self.driver.execute_script("""
            var select = document.getElementById('claim_status_lead_view');
            select.value = '9';
            var event = new Event('change', { bubbles: true });
            select.dispatchEvent(event);
        """)
        safe_click(self.driver, lambda d: d.find_element(By.ID, "update_status_claim_model_submit_btn"))
        time.sleep(2)

    def fill_hospitalized_details(self):
        """Step 8: Fill Hospitalized Details in modal form."""
        try:
            hosp_tab = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Hospitalized Details']")))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", hosp_tab)
            hosp_tab.click()
            time.sleep(1)
        except Exception as e:
            self.driver.save_screenshot("error_click_hospitalized_tab.png")
            raise Exception("Could not click the 'Hospitalized Details' tab.") from e

        try:
            update_btn_xpath = "//div[@id='tabhospitalized']//a[contains(text(),'Update')]"
            self.wait.until(EC.presence_of_element_located((By.XPATH, update_btn_xpath)))
            update_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, update_btn_xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", update_btn)
            update_btn.click()
            time.sleep(1)
        except Exception as e:
            self.driver.save_screenshot("error_click_update_details.png")
            raise Exception("Could not click 'Update Details' button under Hospitalized tab.") from e

        try:
            # Fill modal form fields
            self.wait.until(EC.visibility_of_element_located((By.ID, "health_patient_name_id"))).send_keys(
                "fortis memorial corpororte hospital and institute")

            Select(self.wait.until(EC.element_to_be_clickable((By.ID, "health_patient_gender_id")))).select_by_value("1")
            dob = self.wait.until(EC.element_to_be_clickable((By.ID, "health_patient_dob_id")))
            self.driver.execute_script("arguments[0].removeAttribute('readonly')", dob)
            dob.clear(); dob.send_keys("13-Aug-2000")
            self.driver.find_element(By.ID, "health_patient_relation_id").send_keys("parth")
            self.driver.find_element(By.ID, "health_patient_diagnosis_name_id").send_keys("sumit batra")
            self.driver.find_element(By.ID, "health_patient_treating_dr_id").send_keys("dr sumit batra")
            Select(self.wait.until(EC.element_to_be_clickable((By.ID, "health_patient_treatment_type_id")))).select_by_value("4")

            # Submit the form
            safe_click(self.driver, lambda d: self.wait.until(
                EC.element_to_be_clickable((By.ID, "update-claim-hospitallized-details-model-form-submit-btn"))))
            time.sleep(2)
        except Exception as e:
            self.driver.save_screenshot("error_fill_hospitalized_form.png")
            raise Exception("Failed while filling Hospitalized Details form.") from e

    def fill_hospital_details(self):
        """Step 9: Fill Hospital Details modal."""
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//a[@href='#tabhospital']"))
        time.sleep(1)
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//a[@data-target='#update-claim-hospital-details-modal']"))
        time.sleep(1)

        self.wait.until(lambda d: d.find_element(By.XPATH, "//input[@placeholder='Hospital Name']")).send_keys("Fortis Hospital")
        self.wait.until(lambda d: d.find_element(By.XPATH, "//select[@name='health_hospital_state_id']/option[@value='6']"))
        Select(self.driver.find_element(By.XPATH, "//select[@name='health_hospital_state_id']")).select_by_value("6")

        self.wait.until(lambda d: d.find_element(By.XPATH, "//select[@name='health_hospital_city_id']/option[contains(text(),'GURGAON')]"))
        Select(self.driver.find_element(By.XPATH, "//select[@name='health_hospital_city_id']")).select_by_visible_text("GURGAON")
        self.driver.find_element(By.XPATH, "//input[@name='health_hospital_pincode']").send_keys("122002")

        adm_input = self.wait.until(lambda d: d.find_element(By.XPATH, "//input[@placeholder='Admission Date']"))
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", adm_input)
        adm_input.clear(); adm_input.send_keys("10-Aug-2025")

        dis_input = self.wait.until(lambda d: d.find_element(By.XPATH, "//input[@placeholder='Discharge Date']"))
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", dis_input)
        dis_input.clear(); dis_input.send_keys("15-Aug-2025")

        Select(self.driver.find_element(By.XPATH, "//select[@name='health_hospital_room_category_id']")).select_by_visible_text("Private")
        self.driver.find_element(By.XPATH, "//textarea[@placeholder='Address']").send_keys("Sector 44, Gurgaon")

        safe_click(self.driver, lambda d: d.find_element(By.ID, "update-claim-hospital-details-model-form-submit-btn"))
        time.sleep(2)

    def fill_neft_details(self):
        """Step 10: Fill NEFT / Bank details form."""
        try:
            safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//a[normalize-space()='NEFT Details']"))
            time.sleep(1)

            update_btn_xpath = "//div[@id='tabneft']//a[contains(text(),'Update')]"
            update_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, update_btn_xpath)))
            update_btn.click()
            time.sleep(1)

            self.wait.until(EC.presence_of_element_located((By.ID, "health_neft_name_id"))).send_keys("Satvik Jayalwal")
            self.driver.find_element(By.ID, "health_neft_pan_no_id").send_keys("AFZPK7686K")
            self.driver.find_element(By.ID, "health_neft_bank_name_id").send_keys("SBI")
            self.driver.find_element(By.ID, "health_neft_bank_addess_id").send_keys("Gurgaon Sector 49 Haryana")
            self.driver.find_element(By.ID, "health_neft_pincode_id").send_keys("122001")
            self.driver.find_element(By.ID, "health_neft_ifsc_code_id").send_keys("SBIN0001234")
            self.driver.find_element(By.ID, "health_neft_account_no_id").send_keys("123456789012")

            submit_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "update-claim-neft-details-model-form-submit-btn")))
            submit_btn.click()
            time.sleep(2)
        except Exception as e:
            self.driver.save_screenshot("error_fill_neft_details.png")
            raise Exception("Failed to fill NEFT details.") from e

    def fill_insurance_details(self):
        """Step 11: Fill Insurance Company Details form."""
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//a[normalize-space()='Insurance Company Details']"))
        time.sleep(1)
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//div[@id='tabInsComp']//a[contains(text(),'Update')]"))
        time.sleep(1)

        self.driver.find_element(By.ID, "hospital_insurence_company_name_id").send_keys("National Insurance Co.")
        self.driver.find_element(By.ID, "hospital_insurence_mobile_id").send_keys("9876543210")
        self.driver.find_element(By.ID, "hospital_insurence_email_id").send_keys("support@insco.com")

        safe_click(self.driver, lambda d: d.find_element(By.ID, "update-claim-insurence-company-details-model-form-submit-btn"))
        time.sleep(2)

    def fill_assessment_details(self):
        """Step 12: Fill claim Assessment form."""
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//a[normalize-space()='Assesment Details']"))
        time.sleep(1)
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//div[@id='tabAssesment']//a[contains(text(),'Update Details')]"))
        time.sleep(1)

        self.driver.find_element(By.ID, "health_claim_requested_claim_amount_id").send_keys("150000")
        self.driver.find_element(By.ID, "health_claim_approved_claim_amount_id").send_keys("125000")

        date_input = self.driver.find_element(By.ID, "health_claim_app_rej_date_id")
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", date_input)
        date_input.send_keys("08-Jul-2025")

        self.driver.find_element(By.ID, "health_claim_reopen_amount_id").send_keys("0")

        safe_click(self.driver, lambda d: d.find_element(By.ID, "update-claim-commercial-details-model-form-submit-btn"))
        time.sleep(2)

    def final_submit(self):
        """Step 13: Perform final submission of claim."""
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//a[@href='#tab6']"))
        time.sleep(1)
        self.driver.find_element(By.ID, "final_submit_btn").click()
        time.sleep(3)

        alert = self.wait.until(lambda d: d.switch_to.alert)
        alert.accept()
        
