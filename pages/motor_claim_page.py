from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from utils.helpers import safe_click
import time


class MotorClaimPage:
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

    def fill_rc_details(self):
        """Step 7: Fill in RC details and click Update."""        
        # Open RC Details tab
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='RC Details']"))))

        time.sleep(1)  # allow modal to render
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tabRcDetails']//a[@class='form-submit-btn mb-0 float-right'][contains(text(),'Update')]"))))

        # Fill all RC fields
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='motor_claim_vehicle_number_id']")))
        self.driver.find_element(By.XPATH, "//input[@id='motor_claim_vehicle_number_id']").send_keys("KA05MJ6789")
        self.driver.find_element(By.XPATH, "//input[@id='motor_claim_vehicle_make_id']").send_keys("Honda")
        self.driver.find_element(By.XPATH, "//input[@id='motor_claim_vehicle_model_id']").send_keys("Activa 6G")
        reg_date_input = self.driver.find_element(By.ID, "motor_claim_vehicle_reg_date_id")
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", reg_date_input)
        reg_date_input.send_keys("01-01-2020")

        self.driver.find_element(By.XPATH, "//input[@id='motor_claim_vehicle_chassis_no_id']").send_keys("MA1TA2BL7K2C12345")
        self.driver.find_element(By.XPATH, "//input[@id='motor_claim_vehicle_engine_no_id']").send_keys("ENG987654321")
        
        # Select vehicle type
        Select(self.driver.find_element(By.ID, "motor_claim_vehicle_vehicle_type_id")).select_by_index(2)

        # Click Update
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//button[@id='update-claim-rc-details-model-form-submit-btn']"))
        print("✓ RC Details filled and updated successfully.")
        time.sleep(2)

    def fill_surveyor_details(self):
        """Step 8: Fill in Surveyor Details and click Update."""
        # Open the Surveyor Details tab
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Surveyor Details']"))))
        
        time.sleep(1)  # allow modal/tab to load

        # Click the Update Details button
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tabSurveyourDetails']//a[@class='form-submit-btn mb-0 float-right'][normalize-space()='Update Details']"))))

        # Wait until the fields are interactable
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='motor_surveyor_name_id']")))

        # Fill external surveyor details
        self.driver.find_element(By.ID, "motor_surveyor_name_id").send_keys("Ravi Kumar")
        self.driver.find_element(By.ID, "motor_surveyor_mobile_id").send_keys("9876543210")
        self.driver.find_element(By.ID, "motor_surveyor_email_id").send_keys("ravi@gmail.com")

        # Fill internal surveyor details
        self.driver.find_element(By.ID, "motor_in_surveyor_name_id").send_keys("Anita Sharma")
        self.driver.find_element(By.ID, "motor_in_surveyor_mobile_id").send_keys("9123456789")
        self.driver.find_element(By.ID, "motor_in_surveyor_email_id").send_keys("anita@gmail.com")

        # Click the Update button
        safe_click(self.driver, lambda d: d.find_element(By.ID, "update-claim-surveyor-details-model-form-submit-btn"))

        print("✓ Surveyor Details filled and updated successfully.")
        time.sleep(2)

    def fill_commercial_details(self):
        """Step 9: Fill in Commercial Details and click Update."""

        # Open the Commercial Details tab
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Commercial Details']"))))

        time.sleep(1)  # allow modal/tab to load

        # Click the Update Details button
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tabComDetails']//a[@class='form-submit-btn mb-0 float-right'][normalize-space()='Update Details']"))))

        # Wait for the first input to become interactable
        self.wait.until(EC.element_to_be_clickable((By.ID, "motor_claim_vehicle_fit_start_date_id")))

        # Fill all commercial detail fields
        # Remove 'readonly' attributes from date fields
        # Fill Fitness Start Date
        start_date = self.driver.find_element(By.ID, "motor_claim_vehicle_fit_start_date_id")
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", start_date)
        start_date.clear()
        start_date.send_keys("01-01-2020")

        # Fill Fitness End Date (must be after start date)
        end_date = self.driver.find_element(By.ID, "motor_claim_vehicle_fit_end_date_id")
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", end_date)
        end_date.clear()
        end_date.send_keys("01-01-2025")  # Must be after start

        # Permit Valid Upto
        valid_upto = self.driver.find_element(By.ID, "motor_claim_vehicle_valid_upto_date_id")
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", valid_upto)
        valid_upto.clear()
        valid_upto.send_keys("01-01-2025")


        # Road Tax
        self.driver.find_element(By.ID, "motor_claim_vehicle_road_tax_id").send_keys("15000")

        # No of Occupants
        self.driver.find_element(By.ID, "motor_claim_vehicle_occupants_no_id").send_keys("4")

        # Load Weight
        self.driver.find_element(By.ID, "motor_claim_vehicle_load_weight_id").send_keys("700")

        # Click Update button
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//button[@id='update-claim-commercial-details-model-form-submit-btn']"))

        print("✓ Commercial Details filled and updated successfully.")
        time.sleep(2)

    def fill_driver_details(self):
        """Step 10: Fill in Driver Details and click Update."""

        # Open Driver Details tab
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Driver Details']"))))
        
        time.sleep(1)  # Allow modal/tab to load

        # Click Update button
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tabDriverDetails']//a[@class='form-submit-btn mb-0 float-right'][normalize-space()='Update Details']"))))

        # Fill in driver details
        self.wait.until(EC.element_to_be_clickable((By.ID, "motor_claim_driver_name_id")))

        self.driver.find_element(By.ID, "motor_claim_driver_name_id").send_keys("Suresh Mehra")
        self.driver.find_element(By.ID, "motor_claim_driver_adress_on_dl_id").send_keys("123 Driver Lane, Delhi")
        self.driver.find_element(By.ID, "motor_claim_driver_dl_no_id").send_keys("DL0420210001234")
        self.driver.find_element(By.ID, "motor_claim_driver_issuing_auth_id").send_keys("RTO Delhi")
        self.driver.find_element(By.ID, "motor_claim_driver_licence_type_id").send_keys("LMV")

        # Handle expiry date (remove readonly and enter date)
        expiry_input = self.driver.find_element(By.ID, "motor_claim_driver_dl_expiry_date_id")
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", expiry_input)
        expiry_input.send_keys("31-12-2030")

        # Submit
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//button[@id='update-claim-driver-details-model-form-submit-btn']"))

        print("✓ Driver Details filled and updated successfully.")
        time.sleep(2)

    def fill_accident_details(self):
        """Step 11: Fill in Accident Details and click Update."""

        # Open Accident Details tab
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Accident Details']"))))
        
        time.sleep(1)  # Allow modal/tab to load

        # Click Update Details button
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tabAccidentDetails']//a[@class='form-submit-btn mb-0 float-right'][normalize-space()='Update Details']"))))
        

        # Fill Accident Date (remove readonly and input)
        date_input = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='motor_claim_accident_date_id']")))
        time.sleep(2)
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", date_input) 
        date_input.send_keys("01-01-2024")
        

        # Select Accident Time from dropdown
        accident_time_select = Select(self.driver.find_element(By.XPATH, "//select[@id='motor_claim_accident_time']"))
        accident_time_select.select_by_visible_text("03:00 Am")

        # Fill Accident Location
        self.driver.find_element(By.XPATH, "//input[@id='motor_claim_accident_location_id']").send_keys("Outer Ring Road, Delhi")

        # Fill Tp Injury
        self.driver.find_element(By.XPATH, "//input[@id='motor_claim_accident_tp_injury_id']").send_keys("Multipule fractures in head and spine")


        # Fill Accident FIR details
        self.driver.find_element(By.XPATH, "//textarea[@id='motor_claim_accident_fir_id']").send_keys("FIR No. 12345, filed at Delhi Police Station")

        # Fill Loss Details
        self.driver.find_element(By.XPATH, "//textarea[@id='motor_claim_accident_loss_detail_id']").send_keys("Front bumper and headlights damaged")

        # Click Submit
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//button[@id='update-claim-accident-details-model-form-submit-btn']"))
        print("✓ Accident Details filled and updated successfully.")
        time.sleep(2)


    def fill_garage_details(self):
        """Step 12: Fill in Garage Details and Preferred Workshop Details."""

        # Step 1: Open Garage Details tab
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Garage Details']"))))
        time.sleep(1)

        # Step 2: Click Update Garage Details button
        safe_click(self.driver, lambda d: self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Update Garage')]"))))

        # Step 3: Fill Garage Details form
        self.wait.until(EC.element_to_be_clickable((By.ID, "motor_claim_garage_name_id")))
        self.driver.find_element(By.ID, "motor_claim_garage_name_id").send_keys("ABC Auto Garage")
        self.driver.find_element(By.ID, "motor_claim_garage_contact_person_name_id").send_keys("Rohit Sharma")
        self.driver.find_element(By.ID, "motor_claim_garage_contact_person_mobile_id").send_keys("9876543210")
        Select(self.driver.find_element(By.NAME, "motor_claim_garage_claim_type_id")).select_by_index(1)  # Selecting first option
        self.driver.find_element(By.ID, "motor_claim_garage_adress_id").send_keys("123 Industrial Area, Pune")

        # Step 4: Submit Garage Details form
        safe_click(self.driver, lambda d: d.find_element(By.ID, "update-claim-garage-details-model-form-submit-btn"))
        print("✓ Garage Details filled and submitted.")
        time.sleep(2)

        #wait the form to be invisible 
        self.wait.until(EC.invisibility_of_element((By.ID, "motor_claim_garage_name_id")))

        # Step 5: Click Update Preferred Workshop button
        safe_click(self.driver, lambda d: d.find_element(By.XPATH, "//a[@class='form-submit-btn mb-0 float-left']"))
        time.sleep(1)

        # Step 6: Fill Preferred Workshop form
        self.wait.until(EC.element_to_be_clickable((By.ID, "motor_claim_preferred_workshop_name_id")))
        self.driver.find_element(By.ID, "motor_claim_preferred_workshop_name_id").send_keys("XYZ Motors Workshop")
        self.driver.find_element(By.ID, "motor_claim_preferred_workshop_ctp_name_id").send_keys("Amit Verma")
        self.driver.find_element(By.ID, "motor_claim_preferred_workshop_ctp_mobile_id").send_keys("9988776655")
        self.driver.find_element(By.ID, "motor_claim_preferred_workshop_ctp_email_id").send_keys("amit@xyzworkshop.com")
        self.driver.find_element(By.ID, "motor_claim_preferred_workshop_address_id").send_keys("Phase 2, Auto Zone, Mumbai")

        # Step 7: Submit Preferred Workshop form
        safe_click(self.driver, lambda d: d.find_element(By.ID, "update-claim-workshop-details-model-form-submit-btn"))
        print("✓ Preferred Workshop Details filled and submitted.")
        time.sleep(2)











        

        
        

        