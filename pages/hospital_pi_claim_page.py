from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from utils.helpers import safe_click
import time


class HOSPITALPIClaimPage:
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
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='form-submit-btn mb-1 mr-2 mb-md-0']"))))
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

        
    def fill_lawyer_details(self):
        """Step 7: Fill Lawyer Details from all three modal forms."""

        # Open Lawyer Details tab
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Lawyer Details']"))
        ))
        time.sleep(1)

        # --- Form 1: Update Details ---
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Update Details')]"))
        ))

        # Select Lawyer
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@name='hpi_laywer_id']")))
        Select(self.wait.until(EC.presence_of_element_located((By.XPATH, "//select[@name='hpi_laywer_id']")))).select_by_index(1)

        # Select Appointment Type
        Select(self.wait.until(EC.presence_of_element_located((By.XPATH, "//select[@id='hpi_laywer_appointmnet_type_id']")))).select_by_index(1)

        # Submit Lawyer Details Form
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//button[@id='update-claim-lawyer-details-model-form-submit-btn']"))
        time.sleep(1)

        #wait for the form to dissapear
        self.wait.until(EC.invisibility_of_element((By.XPATH, "//select[@name='hpi_laywer_id']")))

        # --- Form 2: Update Assessment ---
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Update Assessment')]"))
        ))

        # Fill Assessment Form
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='hpi_assesment_invoice_amt_id']"))).send_keys("50000")
        self.driver.find_element(By.XPATH, "//input[@id='hpi_assesment_actual_amt_id']").send_keys("45000")
        self.driver.find_element(By.XPATH, "//input[@id='hpi_assesment_reserve_amt_id']").send_keys("40000")
        self.driver.find_element(By.XPATH, "//input[@id='hpi_assesment_approved_amt_id']").send_keys("35000")
        self.driver.find_element(By.XPATH, "//input[@id='hpi_assesment_deductible_amt_id']").send_keys("1000")
        self.driver.find_element(By.XPATH, "//input[@id='hpi_assesment_defence_cost_id']").send_keys("2000")
        Select(self.driver.find_element(By.XPATH, "//select[@name='payment_adv_status_id']")).select_by_index(1)

        # Submit Assessment Form
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//button[@id='update-claim-assessment-details-model-form-submit-btn']"))
        time.sleep(1)

        #wait for the form to dissapear
        self.wait.until(EC.invisibility_of_element((By.XPATH, "//input[@id='hpi_assesment_invoice_amt_id']")))

        # --- Form 3: Add Hearing ---
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Update Hearing')]"))
        ))

        # Fill Hearing Form
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='hearing_lawyer_name_id']"))).clear()
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='hearing_lawyer_name_id']"))).send_keys("Ravi Kumar")
        self.driver.find_element(By.XPATH, "//input[@id='hearing_lawyer_mobile_id']").send_keys("9876543210")
        self.driver.find_element(By.XPATH, "//input[@id='hearing_lawyer_email_id']").clear()
        self.driver.find_element(By.XPATH, "//input[@id='hearing_lawyer_email_id']").send_keys("ravi@gmail.com")

        hearing_date = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='hearing_date_id']")))
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", hearing_date)
        hearing_date.clear()
        hearing_date.send_keys("01-08-2024")

        next_date = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='hearing_next_date_id']")))
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", next_date)
        next_date.clear()
        next_date.send_keys("15-08-2024")

        self.driver.find_element(By.XPATH, "//textarea[@id='hearing_remark_id']").send_keys("Next hearing scheduled as per court notice.")

        # Submit Hearing Form
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//button[@id='update-claim-hearing-details-model-form-submit-btn']"))
        time.sleep(2)

        #wait for the form to dissapear
        self.wait.until(EC.invisibility_of_element((By.XPATH, "//input[@id='hearing_lawyer_name_id']")))

        print("✓ Lawyer Details (all 3 forms) submitted successfully.")

        
    def fill_insurance_company_details(self):
        """Step 8: Fill Insurance Company Details and submit the form."""

        # Open Insurance Company Details tab
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Insurance Company Details']"))
        ))
        time.sleep(1)

        # --- Update Details ---        
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tabInsurenceCompetails']//a[@class='form-submit-btn mb-0 float-right'][contains(text(),'Update')]"))
        ))

        # Fill form fields
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='hpi_insurence_company_name_id']"))).send_keys("New India Assurance")
        self.driver.find_element(By.XPATH, "//input[@id='hpi_insurence_mobile_id']").send_keys("9999988888")
        self.driver.find_element(By.XPATH, "//input[@id='hpi_insurence_email_id']").send_keys("nia@email.com")

        # Submit
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//button[@id='update-claim-insurence-company-details-model-form-submit-btn']"))
        time.sleep(2)

        #wait for the form to dissapear
        self.wait.until(EC.invisibility_of_element((By.XPATH, "//input[@id='hpi_loss_date_id']")))

        print("✓ Insurance Company Details submitted.")


    def fill_case_details(self):
        """Step 9: Fill Case Details and submit."""

        # Open 'Case Details' tab
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Case Details']"))
        ))
        time.sleep(1)

        # Click the 'Update' button inside the Case Details tab
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tabCaseDetails']//a[contains(text(),'Update')]"))
        ))
        time.sleep(1)

        # 1. Date of Loss
        date_of_loss = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='hpi_loss_date_id']")))
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", date_of_loss)
        date_of_loss.send_keys("01-07-2024")

        # 2. Type of Loss Cause & Notice Received
        Select(self.wait.until(EC.presence_of_element_located((By.XPATH, "//select[@name='hpi_loss_cause_id']")))).select_by_visible_text("Death")
        Select(self.wait.until(EC.presence_of_element_located((By.XPATH, "//select[@name='hpi_notice_type_id']")))).select_by_visible_text("Legal Notice")

        # 3. Date of Notice Received
        notice_date = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='hpi_date_of_notice_recieved_id']")))
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", notice_date)
        notice_date.send_keys("05-07-2024")

        # Close the calendar popup by clicking outside
        self.driver.find_element(By.XPATH, "//label[contains(text(),'Loss Description')]").click()
        time.sleep(1)

        # Wait for calendar to disappear
        try:
            self.wait.until(EC.invisibility_of_element_located(
                (By.XPATH, "//div[contains(@class,'datepicker') and contains(@style,'display: block')]")
            ))
        except TimeoutException:
            print("Warning: Calendar popup invisibility wait failed, continuing...")

        # 4. Loss Description
        self.driver.find_element(By.XPATH, "//textarea[@id='hpi_loss_desc_id']").send_keys("Vehicle severely damaged in accident.")

        # 5. Loss Estimate
        self.driver.find_element(By.XPATH, "//textarea[@id='hpi_loss_eastimate_id']").send_keys("150000")

        # 6. Case Category
        Select(self.wait.until(EC.presence_of_element_located((By.XPATH, "//select[@name='case_cateory_id']")))).select_by_visible_text("LEGAL NOTICE")

        # 7. Case Status
        Select(self.wait.until(EC.presence_of_element_located((By.XPATH, "//select[@name='case_status_id']")))).select_by_visible_text("LEGAL NOTICE (Pre-Litigation)")

        # --- Submit ---
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//button[@id='update-claim-case-details-model-form-submit-btn']"))
        time.sleep(2)

        # Wait for modal to close
        self.wait.until(EC.invisibility_of_element_located((By.ID, "edit_case_modal")))

        print("✓ Case Details filled and submitted.")
 

    def update_status(self):
        """Step 10: Update claim status to 'Claim Paid' with full form fields."""

        # 1. Click the 'Update Status' button
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Update') and contains(@class, 'form-submit-btn')]"))
        ))
        print("✓ Update Status button clicked")

        # 2. Wait for modal to appear
        modal_xpath = "//form[@id='update-claim-status-form-id']"
        self.wait.until(EC.visibility_of_element_located((By.XPATH, modal_xpath)))
        print("✓ Update Status modal is visible")

        # 3. Select "Claim Paid" in dropdown
        status_dropdown_xpath = "//select[@id='claim_status_lead_view']"
        status_dropdown = self.wait.until(EC.visibility_of_element_located((By.XPATH, status_dropdown_xpath)))
        Select(status_dropdown).select_by_visible_text("Claim Paid")
        print("✓ Selected 'Claim Paid'")

        # 4. Wait for Claim Number field
        claim_number_input = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@id='claim_number_id']")))
        claim_number_input.send_keys("CLM-00123")
        print("✓ Entered Claim Number")

        # 5. Upload Claim Document
        claim_doc_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='claim_issue_doc_id']")))
        claim_doc_input.send_keys("C:\\python_codes\\CoverYouAutomation\\images\\test_image.jpg")
        print("✓ Claim document uploaded")

        # 6. Submit the form
        update_btn = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='update_status_claim_model_submit_btn']")))
        update_btn.click()
        print("✓ Submitted status update")

        # 7. Wait for modal to disappear
        self.wait.until(EC.invisibility_of_element_located((By.XPATH, modal_xpath)))
        print("✓ Status updated and modal closed")
