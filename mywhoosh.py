from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import csv

load_dotenv()


with sync_playwright() as p:
    # Get credentials
    email = os.getenv("MW_EMAIL")
    password = os.getenv("MW_PASSWORD")

    # Initiate browser and page
    browser = p.chromium.launch(headless=False)  # headless=False
    page = browser.new_page()
    # Create context to accept downloads

    context = browser.new_context(accept_downloads=True)

    # Go to login page and login with credentials
    page = context.new_page()
    page.goto("https://event.mywhoosh.com/auth/login")
    page.fill("#email", value=email)
    page.fill("#password", value=password)
    page.click("button.btn-universal")
    page.wait_for_timeout(2000)  # ?

    # Handle the cookie bar
    page.wait_for_selector('button[data-testid="uc-accept-all-button"]')
    page.click('button[data-testid="uc-accept-all-button"]')
    page.screenshot(path="login.png")

    # Go to activities
    page.goto("https://event.mywhoosh.com/user/activities#activities")

    # Get the download element and download the file
    page.wait_for_selector("button.btnDownload", timeout=30000)
    with page.expect_download() as download_info:
        page.click("button.btnDownload")

    download = download_info.value
    download_path = r"C:\Users\marek\dev\sync_mywhoosh_garmin\activities"
    download.save_as(f"{download_path}\\{download.suggested_filename}")
