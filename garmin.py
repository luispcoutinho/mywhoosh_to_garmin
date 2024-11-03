from selenium_driverless.sync import webdriver as driverless_webdriver
from selenium import webdriver as standard_webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from dotenv import load_dotenv
import os
import time
import json

# Load environment variables
load_dotenv()
email = os.getenv("GC_EMAIL")
password = os.getenv("GC_PASSWORD")

# File path to upload
upload_file = r"C:\Users\marek\dev\mywhoosh_to_garmin\mywhoosh_to_garmin\media\NBBNE0KLHKKud0VfbR6WhSPEs9CaiGK5aAuSW8a5.fit"

# Step 1: Use selenium-driverless to handle login and save cookies
driverless_options = driverless_webdriver.ChromeOptions()
driverless_options.add_argument("--headless=new")
driverless_options.add_argument("--incognito")

# Log in using selenium-driverless and save cookies
with driverless_webdriver.Chrome(options=driverless_options) as driverless:
    driverless.get("https://connect.garmin.com/signin")
    time.sleep(5)

    # Login process
    email_input = driverless.find_element(By.ID, "email")
    email_input.send_keys(email)

    password_input = driverless.find_element(By.ID, "password")
    password_input.send_keys(password)

    submit_button = driverless.find_element(
        By.XPATH, "//button[@data-testid='g__button']"
    )
    driverless.execute_script("arguments[0].click();", submit_button)

    time.sleep(10)
    driverless.save_screenshot("login.png")
    # Accept the cookie bar
    try:
        cookies_accept_button = driverless.find_element(By.ID, "truste-consent-button")
        cookies_accept_button.click()
        print("Accepted cookies.")

    except Exception as e:
        print("Cookie bar not found or already accepted")
    time.sleep(2)
    driverless.save_screenshot("cookies.png")
    # Save cookies to a JSON file after login
    cookies = driverless.get_cookies()
    with open("garmin_cookies.json", "w") as file:
        json.dump(cookies, file)

# Step 2: Use standard Selenium to load cookies and upload the file
# Standard Selenium browser options
standard_options = standard_webdriver.ChromeOptions()
standard_options.add_argument("--headless=new")
standard_options.add_argument("--incognito")
# Start a new Selenium browser session and load the saved cookies
with standard_webdriver.Chrome(options=standard_options) as driver:
    driver.get("https://connect.garmin.com/modern/import-data")

    # Load cookies from JSON and add them to the Selenium session
    with open("garmin_cookies.json", "r") as file:
        cookies = json.load(file)
        for cookie in cookies:
            # Add each cookie to the driver
            # Adjust the domain for cross-domain cookies if necessary
            if "sameSite" in cookie:
                cookie.pop("sameSite")  # Remove sameSite attribute if present
            driver.add_cookie(cookie)

    # Refresh to apply cookies and ensure session is active
    driver.get("https://connect.garmin.com/modern/import-data")

    # Wait for the file input and upload elements to be ready
    time.sleep(5)
    driver.save_screenshot("import-data.png")

    time.sleep(3)

    # Wait for the file input element to be present
    try:
        file_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dzu-input"))
        )
        file_input.send_keys(upload_file)
        print("File uploaded successfully.")
    except Exception as e:
        print("File input element not found:", e)
        driver.save_screenshot("file_input_error.png")

    driver.save_screenshot("upload.png")

    # Wait briefly to ensure the file is recognized
    time.sleep(5)

    # Find and click the Import Data button
    import_button = driver.find_element(
        By.XPATH, "//button[contains(text(), 'Import Data')]"
    )

    # Ensure the button is enabled
    if import_button.is_enabled():
        import_button.click()
        print("Upload triggered successfully!")
    else:
        print("Import button is still disabled. Check if the file loaded correctly.")

    # Wait for confirmation of upload
    time.sleep(5)

if os.path.exists("garmin_cookies.json"):
    os.remove("garmin_cookies.json")
    print("Cookies file deleted.")
else:
    print("Cookies file not found.")
