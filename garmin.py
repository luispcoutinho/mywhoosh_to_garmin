from selenium_driverless.sync import webdriver as driverless_webdriver
from playwright.sync_api import sync_playwright
from selenium_driverless.types.by import By

from dotenv import load_dotenv
import os
import time
import json

# Load environment variables
load_dotenv()
email = os.getenv("GC_EMAIL")
password = os.getenv("GC_PASSWORD")

# File path to upload

folder_path = os.getenv("FOLDER_PATH")
upload_files = [
    os.path.join(folder_path, file)
    for file in os.listdir(folder_path)
    if file.endswith(".fit")
]

print(upload_files)
# Step 1: Use selenium-driverless to handle login and save cookies
driverless_options = driverless_webdriver.ChromeOptions()
# driverless_options.add_argument("--headless=new")
# driverless_options.add_argument("--incognito")

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


# Step 2: Use Playwright to load cookies and upload the file
def upload_with_playwright(cookie_file, upload_file):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Load cookies from JSON file
        with open(cookie_file, "r") as file:
            cookies = json.load(file)
            # Convert cookies to Playwright format if needed
            playwright_cookies = []
            for cookie in cookies:
                # Remove problematic fields that Selenium might have added
                if "expiry" in cookie:
                    cookie["expires"] = cookie.pop("expiry")
                cookie.pop("sameSite", None)
                playwright_cookies.append(cookie)

            context.add_cookies(playwright_cookies)

        # Navigate to the import page
        page.goto("https://connect.garmin.com/modern/import-data")

        # Wait for the page to load completely
        page.wait_for_load_state("networkidle")

        # Take screenshot for debugging
        page.screenshot(path="import-data-playwright.png")

        # Direct file upload to the hidden input
        # No need to click, just set the files directly
        input_selector = ".dzu-input"
        page.wait_for_selector(input_selector, state="attached")
        page.set_input_files(input_selector, upload_file)
        print("File upload initiated")

        # Wait for file to be processed
        page.wait_for_timeout(5000)  # 5 second wait

        # Take screenshot after upload
        page.screenshot(path="upload-playwright.png")
        # Click the Import Data button
        # Wait for the button to be visible and enabled
        import_button = page.locator('button[type="button"]:text("Import Data")')
        try:
            import_button.wait_for(state="visible", timeout=10000)  # 10 second timeout
            if import_button.is_enabled():
                import_button.click()
                print("Upload triggered successfully!")
            else:
                print("Import button is disabled. Check if the file loaded correctly.")
        except Exception as e:
            print(f"Error with Import button: {e}")
            page.screenshot(path="import-button-error.png")
        # Wait for confirmation and any final processing
        page.wait_for_timeout(5000)

        # Close browser
        browser.close()


# Use the function
try:
    upload_with_playwright("garmin_cookies.json", upload_files)
except Exception as e:
    print(f"Error during upload: {e}")
finally:
    # Clean up cookies file
    if os.path.exists("garmin_cookies.json"):
        os.remove("garmin_cookies.json")
        print("Cookies file deleted.")
    else:
        print("Cookies file not found.")
