from playwright.sync_api import sync_playwright
from selenium_driverless.sync import webdriver as driverless_webdriver
from selenium_driverless.types.by import By
import json
import os
import csv
from dotenv import load_dotenv


class GarminLoginSession:
    def __init__(self):
        self.driver = None
        self.driver_options = None
        self.page = None

        self.email = os.getenv("GC_EMAIL")
        self.password = os.getenv("GC_PASSWORD")
        self.activities_file = os.getenv("FOLDER_PATH")

    def __enter__(self):
        self.driver_options = driverless_webdriver.ChromeOptions()
        self.driver_options.headless = False
        self.driver = driverless_webdriver.Chrome(options=self.driver_options)
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.driver:
            self.driver.quit()
        if exc_type is not None:
            print(f"Exception occurred: {exc_value}")

    def login(self):
        self.page = "https://connect.garmin.com/signin"
        self.driver.get(self.page, wait_load=True, timeout=60)
        self.driver.sleep(10)
        self.email_input = self.driver.find_element(by=By.ID, value="email", timeout=60)
        self.email_input.send_keys(self.email)
        self.driver.sleep(2)
        self.password_input = self.driver.find_element(
            by=By.ID, value="password", timeout=60
        )
        self.password_input.send_keys(self.password)
        self.driver.sleep(2)
        submit_button = self.driver.find_element(
            by=By.XPATH, value="//button[@data-testid='g__button']", timeout=60
        )
        self.driver.execute_script("arguments[0].click();", submit_button)
        self.driver.sleep(5)
        self.accept_cookies()
        self.driver.sleep(2)
        self.save_cookies()

    def accept_cookies(self):
        self.driver.sleep(5)
        cookies_accept_button = self.driver.find_element(
            by=By.ID, value="truste-consent-button", timeout=60
        )
        cookies_accept_button.click()

    def save_cookies(self):
        cookies = self.driver.get_cookies()
        with open("garmin_cookies.json", "w") as file:
            json.dump(cookies, file)
        print("cookies saved")


class GarminActionSession:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.file_path = os.getenv("FOLDER_PATH")
        self.download_path = os.path.join(self.file_path, "")

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.load_cookies()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def load_cookies(self):
        cookies_file = "garmin_cookies.json"
        with open(cookies_file, "r") as file:
            cookies = json.load(file)
            playwright_cookies = []
            for cookie in cookies:
                if "expiry" in cookie:
                    cookie["expires"] = cookie.pop("expiry")
                cookie.pop("sameSite", None)
                playwright_cookies.append(cookie)
            self.context.add_cookies(playwright_cookies)

    def delete_cookies(self):
        cookies_file = "garmin_cookies.json"
        if cookies_file:
            os.remove("garmin_cookies.json")

    def download_activities_list(self):
        url = "https://connect.garmin.com/modern/activities?activityType=cycling&activitySubType=virtual_ride"
        self.page.goto(url, wait_until="load")
        self.page.wait_for_load_state()
        self.page.wait_for_timeout(2000)
        with self.page.expect_download() as download_info:
            export_button = self.page.locator(".export-btn")
            export_button.click()
        download = download_info.value

        download.save_as(self.download_path + download.suggested_filename)
        self.page.wait_for_load_state()

    def upload_activities(self):
        upload_files = [
            os.path.join(self.download_path, file)
            for file in os.listdir(self.download_path)
            if file.endswith(".fit")
        ]
        url = "https://connect.garmin.com/modern/import-data"
        self.page.goto(url, wait_until="load")
        self.page.wait_for_selector(".dzu-input", state="attached")
        self.page.set_input_files(".dzu-input", upload_files)
        self.page.wait_for_timeout(4897)

        import_button = self.page.locator('button[class*="btnPrimary"]').nth(0)
        import_button.wait_for()
        try:
            import_button.wait_for(state="visible", timeout=10000)
            if import_button.is_enabled():
                import_button.click()
            else:
                print("Import button is disabled. Check if the file loaded correctly.")
        except Exception as e:
            print(f"Error with Import button: {e}")
        self.page.wait_for_timeout(5000)

    def get_activities_list(self):
        activities_list = []
        with open("activities/Activities.csv", mode="r", encoding="utf-8") as file:
            activities = csv.reader(file)
            print(activities)
            for row in activities:
                date = row[1].split()[0]
                time = row[6]
                activities_list.append(f"{date}, {time}")
        return activities_list
