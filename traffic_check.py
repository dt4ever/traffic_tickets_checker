import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from plyer import notification

# --- Configuration ---
TARGET_URL = "https://ppo.gov.eg/ppo/r/ppoportal/ppoportal/traffic"

# User Data
PLATE_CHAR_1 = "ب"
PLATE_CHAR_2 = "س"
PLATE_CHAR_3 = "ف"
PLATE_NUMS   = "4176"
NATIONAL_ID  = "29301301803574"
PHONE_NUMBER = "01142939127"

# --- Selectors (Extracted from your inputs) ---

# Page 14: License Plate Inputs
ID_PLATE_CHAR_1 = "P14_LETER_1"
ID_PLATE_CHAR_2 = "P14_LETER_2"
ID_PLATE_CHAR_3 = "P14_LETER_3"
ID_PLATE_NUMS   = "P14_NUMBER_WITH_LETTER"

# Page 14: The "Total Fines" Button (Transitions to next step)
ID_BTN_SEARCH_PLATE = "GET_FIN_LETTER_NUMBERS_BTN"

# Page 7: National ID & Details Inputs
ID_NAT_ID_INPUT = "P7_NATIONAL_ID_CASE_1"
ID_PHONE_INPUT  = "P7_PHONE_NUMBER_ID_CASE_1"

# Page 7: The Final "Check Details" Button
ID_BTN_CHECK_DETAILS = "B1776099686727570788"

def check_traffic_fines():
    # Setup Chrome Driver
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Uncomment this to run invisibly in the background
    
    # Initialize Driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("1. Opening website...")
        driver.get(TARGET_URL)
        wait = WebDriverWait(driver, 15)

        # --- STEP 1: Enter License Plate (4 Fields) ---
        print("2. Entering License Plate...")
        
        # We wait for the first input to be ready
        wait.until(EC.visibility_of_element_located((By.ID, ID_PLATE_CHAR_1))).send_keys(PLATE_CHAR_1)
        driver.find_element(By.ID, ID_PLATE_CHAR_2).send_keys(PLATE_CHAR_2)
        driver.find_element(By.ID, ID_PLATE_CHAR_3).send_keys(PLATE_CHAR_3)
        driver.find_element(By.ID, ID_PLATE_NUMS).send_keys(PLATE_NUMS)

        # --- STEP 2: Submit Plate Query ---
        print("3. Clicking 'Total Fines' to proceed...")
        search_btn = wait.until(EC.element_to_be_clickable((By.ID, ID_BTN_SEARCH_PLATE)))
        search_btn.click()

        # --- STEP 3: Enter National ID & Phone ---
        print("4. Entering National ID and Phone...")
        
        # Wait for the National ID field (Page 7) to become visible
        nat_id_field = wait.until(EC.visibility_of_element_located((By.ID, ID_NAT_ID_INPUT)))
        nat_id_field.clear()
        nat_id_field.send_keys(NATIONAL_ID)

        phone_field = driver.find_element(By.ID, ID_PHONE_INPUT)
        phone_field.clear()
        phone_field.send_keys(PHONE_NUMBER)

        # --- STEP 4: Click Final Details Button ---
        print("5. Requesting violation details...")
        details_btn = driver.find_element(By.ID, ID_BTN_CHECK_DETAILS)
        details_btn.click()

        # --- STEP 5: Parse Results ---
        print("6. Reading Result...")
        
        # Find the specific box containing 'اجمالي الغرامات الشاملة'
        # XPath logic: Find div with class 'boxTable' -> Find 'p' inside it with specific text -> Find sibling 'span'
        result_xpath = "//div[contains(@class, 'boxTable')][.//p[contains(text(), 'اجمالي الغرامات الشاملة')]]//span"
        
        result_element = wait.until(EC.visibility_of_element_located((By.XPATH, result_xpath)))
        fine_amount_text = result_element.text.strip()
        
        print(f">> REPORT: Total Fines detected: {fine_amount_text} EGP")

        # --- STEP 6: Desktop Notification ---
        # Convert text to number for logic check
        try:
            fine_amount = float(fine_amount_text)
        except ValueError:
            fine_amount = 0 

        if fine_amount > 0:
            notification.notify(
                title='⚠️ Traffic Fine Alert',
                message=f'Vehicle {PLATE_CHAR_1}{PLATE_CHAR_2}{PLATE_CHAR_3} {PLATE_NUMS} has {fine_amount_text} EGP in fines.',
                app_name='TrafficBot',
                timeout=10
            )
        else:
            print("No fines found. Clean record.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        # Helpful debugging: print the current URL if it fails to see if we got redirected
        try:
            print(f"Current Page: {driver.current_url}")
        except:
            pass
            
    finally:
        # Keep browser open for 5 seconds to let you verify visually
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    check_traffic_fines()