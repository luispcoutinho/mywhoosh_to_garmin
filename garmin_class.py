from playwright.sync_api import sync_playwright, expect
from selenium_driverless.sync import webdriver as driverless_webdriver
from selenium_driverless.types.by import By
import json
import os
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
        # self.driver_options.add_argument("--headless=new")
        self.driver = driverless_webdriver.Chrome(options=self.driver_options)
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.driver:
            self.driver.quit()
        # Handle any exceptions if needed
        if exc_type is not None:
            print(f"Exception occurred: {exc_value}")

    def login(self):
        self.page = "https://connect.garmin.com/signin"
        self.driver.get(self.page)
        self.driver.sleep(5)
        self.email_input = self.driver.find_element(By.ID, "email")
        self.email_input.send_keys(self.email)
        self.driver.sleep(2)
        self.password_input = self.driver.find_element(By.ID, "password")
        self.password_input.send_keys(self.password)
        self.driver.sleep(2)
        submit_button = self.driver.find_element(
            By.XPATH, "//button[@data-testid='g__button']"
        )
        self.driver.execute_script("arguments[0].click();", submit_button)
        print("logged in")
        self.driver.sleep(2)
        print("slept 2s")
        print("trying to accept cookies")
        self.accept_cookies()
        self.driver.sleep(2)
        self.save_cookies()

    def accept_cookies(self):
        print("inside accept_cookies")
        self.driver.sleep(5)
        # trvá, než se to načte, tak je potřeba počkat - časem pořešit pomocí WebDriverWait
        cookies_accept_button = self.driver.find_element(By.ID, "truste-consent-button")
        print("button found")

        cookies_accept_button.click()

    def save_cookies(self):
        cookies = self.driver.get_cookies()
        with open("garmin_cookies.json", "w") as file:
            json.dump(cookies, file)
        print("cookies saved")


class GarminActionSession:
    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def load_cookies(self):
        pass

    def download_activities_list(self):
        pass

    def upload_activities(self):
        pass


with GarminLoginSession() as garmin_login:
    print("run")
