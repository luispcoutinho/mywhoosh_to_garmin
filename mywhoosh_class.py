from playwright.sync_api import sync_playwright, expect
from dotenv import load_dotenv
import os
import csv

load_dotenv()


class MyWhooshSession:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.email = os.getenv("MW_EMAIL")
        self.password = os.getenv("MW_PASSWORD")
        self.download_path = os.getenv("FOLDER_PATH")
        self.headless = True

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def login(self):
        url = "https://event.mywhoosh.com/auth/login"

        self.page.goto(url, wait_until="load")
        self.accept_cookies()
        self.page.wait_for_selector("#email", state="visible")
        self.page.fill("#email", self.email)

        self.page.wait_for_selector("#password", state="visible")
        self.page.fill("#password", self.password)
        self.page.wait_for_timeout(2000)

        self.page.wait_for_selector("button.btn-universal", state="visible")
        self.page.click("button.btn-universal")
        self.page.wait_for_timeout(2000)
        print("Logged into MyWhoosh.")

    def accept_cookies(self):
        self.page.wait_for_selector(
            'button[data-testid="uc-accept-all-button"]', state="visible"
        )
        self.page.click('button[data-testid="uc-accept-all-button"]')
        self.page.wait_for_timeout(2000)
        print("MyWhoosh cookies accepted.")

    def download_activities(self, activities_list):
        url = "https://event.mywhoosh.com/user/activities#activities"
        self.page.goto(url, wait_until="load")
        self.page.wait_for_timeout(2000)
        while True:
            try:
                load_more_button = self.page.locator("button.ldmore")
                expect(load_more_button).to_be_visible()
                load_more_button.click()
                self.page.wait_for_timeout(333)
            except:
                print("MyWhoosh - All activities loaded.")
                break
        self.page.wait_for_timeout(2000)
        data = []
        self.page.wait_for_selector(
            "div.results.table-responsive.container table.table.align-middle tbody",
            state="visible",
        )
        rows = self.page.query_selector_all(
            "div.results.table-responsive.container table.table.align-middle tbody tr"
        )

        activities_download_counter = 0
        for row in rows:
            cells = row.query_selector_all("td")
            row_data = [cell.inner_text() for cell in cells]
            date = row_data[0].split("/")
            date = f"{date[2]}-{date[1]}-{date[0]}"
            time = row_data[7].split(".")
            activity = f"{date}, {time[0]}"
            data.append(activity)
            print(activity)
            if activity in activities_list:
                print("Activity already synced.")
            else:
                print("New activity.")
                with self.page.expect_download() as download_info:
                    download_button = row.query_selector("button.btnDownload")
                    download_button.click()
                download = download_info.value
                download.save_as(f"{self.download_path}\\{download.suggested_filename}")
                activities_download_counter += 1
                self.page.wait_for_timeout(2000)
        if activities_download_counter:
            return True
        else:
            return False
