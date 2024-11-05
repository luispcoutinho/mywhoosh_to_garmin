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

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.login_to_mywhoosh()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Clean up Playwright resources
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def login_to_mywhoosh(self):
        self.page.goto("https://event.mywhoosh.com/auth/login")
        self.page.fill("#email", self.email)
        self.page.fill("#password", self.password)
        self.page.click("button.btn-universal")
        self.page.wait_for_timeout(2000)
        self.page.screenshot(path="login.png")
        print("Logged in!")
        self.accept_cookies()

    def accept_cookies(self):
        self.page.wait_for_selector('button[data-testid="uc-accept-all-button"]')
        self.page.click('button[data-testid="uc-accept-all-button"]')
        self.page.wait_for_timeout(2000)
        self.page.screenshot(path="AcceptedCookies.png")
        print("Accepted Cookies!")

    def get_list_of_activities(self):
        """
        Předělat tak, abych to neukládal do csv, ale rovnou když iteruju mezi řádkama aktivity, tak aby stahoval aktivitu,
        která bude splňovat podmínku, tedy stejná aktivita nebude v seznamu aktivit Garmin Connect
        """
        self.page.goto("https://event.mywhoosh.com/user/activities#activities")
        self.page.wait_for_timeout(2000)
        while True:
            try:
                # Locate the "LOAD MORE" button and check if it's visible
                load_more_button = self.page.locator("button.ldmore")
                print(load_more_button)
                expect(load_more_button).to_be_visible(timeout=2000)
                load_more_button.click()
                self.page.wait_for_timeout(
                    1000
                )  # Wait a moment after each click if needed
            except:
                # Break loop if "LOAD MORE" button is no longer visible
                print("All data loaded.")
                break
        self.page.wait_for_timeout(2000)
        data = []
        rows = self.page.query_selector_all(
            "div.results.table-responsive.container table.table.align-middle tbody tr"
        )
        for row in rows:
            cells = row.query_selector_all("td")
            row_data = [cell.inner_text() for cell in cells]
            data.append(row_data)

        with open("whoosh_activities_list.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "DATE",
                    "RIDE",
                    "DIST",
                    "ELEV",
                    "W (avg)",
                    "W/KG (avg)",
                    "HEART (avg)",
                    "TIME",
                    "ANALYSIS",
                    "DOWNLOAD",
                ]
            )
            writer.writerows(data)

    def download_activities(self):
        """
        sloučit s funkcí get_list_of_activities
        """
        self.page.goto("https://event.mywhoosh.com/user/activities#activities")

        # Get the download element and download the file
        self.page.wait_for_selector("button.btnDownload", timeout=30000)
        with self.page.expect_download() as download_info:
            self.page.click("button.btnDownload")

        download = download_info.value
        download_path = r"C:\Users\marek\dev\sync_mywhoosh_garmin\activities"
        download.save_as(f"{download_path}\\{download.suggested_filename}")
