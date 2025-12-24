import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
TARGET_URL = "https://ppo.gov.eg/ppo/r/ppoportal/ppoportal/traffic"

# --- Load Secrets from Environment Variables ---
try:
    PLATE_CHAR_1 = os.environ["PLATE_CHAR_1"]
    PLATE_CHAR_2 = os.environ["PLATE_CHAR_2"]
    PLATE_CHAR_3 = os.environ["PLATE_CHAR_3"]
    PLATE_NUMS   = os.environ["PLATE_NUMS"]
    NATIONAL_ID  = os.environ["NATIONAL_ID"]
    PHONE_NUMBER = os.environ["PHONE_NUMBER"]
except KeyError as e:
    print(f"Error: Missing secret {e}. Make sure to set it in GitHub Secrets.")
    sys.exit(1)

# --- Selectors ---
ID_PLATE_CHAR_1 = "P14_LETER_1"
ID_PLATE_CHAR_2 = "P14_LETER_2"
ID_PLATE_CHAR_3 = "P14_LETER_3"
ID_PLATE_NUMS   = "P14_NUMBER_WITH_LETTER"
ID_BTN_SEARCH_PLATE = "GET_FIN_LETTER_NUMBERS_BTN"
ID_NAT_ID_INPUT = "P7_NATIONAL_ID_CASE_1"
ID_PHONE_INPUT  = "P7_PHONE_NUMBER_ID_CASE_1"
ID_BTN_CHECK_DETAILS = "B1776099686727570788"

def check_traffic_fines():
    # --- Headless Chrome Setup ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("1. Opening website...")
        driver.get(TARGET_URL)
        wait = WebDriverWait(driver, 20)

        # --- STEP 1: Enter License Plate ---
        print("2. Entering License Plate...")
        wait.until(EC.visibility_of_element_located((By.ID, ID_PLATE_CHAR_1))).send_keys(PLATE_CHAR_1)
        driver.find_element(By.ID, ID_PLATE_CHAR_2).send_keys(PLATE_CHAR_2)
        driver.find_element(By.ID, ID_PLATE_CHAR_3).send_keys(PLATE_CHAR_3)
        driver.find_element(By.ID, ID_PLATE_NUMS).send_keys(PLATE_NUMS)

        # --- STEP 2: Submit Plate Query ---
        print("3. Clicking 'Total Fines'...")
        search_btn = wait.until(EC.element_to_be_clickable((By.ID, ID_BTN_SEARCH_PLATE)))
        search_btn.click()

        # --- STEP 3: Enter National ID & Phone ---
        print("4. Entering National ID and Phone...")
        nat_id_field = wait.until(EC.visibility_of_element_located((By.ID, ID_NAT_ID_INPUT)))
        nat_id_field.clear()
        nat_id_field.send_keys(NATIONAL_ID)

        driver.find_element(By.ID, ID_PHONE_INPUT).send_keys(PHONE_NUMBER)

        # --- STEP 4: Click Final Details ---
        print("5. Requesting violation details...")
        driver.find_element(By.ID, ID_BTN_CHECK_DETAILS).click()

        # --- STEP 5: Parse Results ---
        print("6. Reading Result...")
        result_xpath = "//div[contains(@class, 'boxTable')][.//p[contains(text(), 'اجمالي الغرامات الشاملة')]]//span"
        result_element = wait.until(EC.visibility_of_element_located((By.XPATH, result_xpath)))
        fine_amount_text = result_element.text.strip()
        
        print(f">> REPORT: Total Fines detected: {fine_amount_text} EGP")

        # --- STEP 6: Logic ---
        try:
            fine_amount = float(fine_amount_text)
        except ValueError:
            fine_amount = 0 

        if fine_amount > 0:
            print(f"::error::FINES FOUND! Amount: {fine_amount_text} EGP")
            sys.exit(1) # This triggers the failure email
        else:
            print("No fines found. Clean record.")
            sys.exit(0)

    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)
    finally:
        driver.quit()

if __name__ == "__main__":
    check_traffic_fines()
