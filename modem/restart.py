from playwright.sync_api import sync_playwright

from op.credentials import get_password
from utils.logs import log

OP_ITEM = "Modem & Router"
MODEM_URL = "http://192.168.2.1"


def log_in_and_restart(password: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Log in
        page.goto(MODEM_URL)
        page.click("button[id=headerLogin]")
        page.wait_for_selector("input[name=admin-password]")
        page.fill("input[name=admin-password]", password)
        page.click("button[id=loginButton]")

        # Navigate to reset options
        page.wait_for_selector("a[href=advancedtools]")
        page.click("a[href=advancedtools]")
        page.wait_for_selector("a[href='advancedtools/resets']")
        page.click("a[href='advancedtools/resets']")

        # Restart modem and confirm twice
        page.wait_for_selector("button[id=restart]")
        page.click("button[id=restart]")
        page.wait_for_selector("button[id=yes]")
        page.click("button[id=yes]")
        page.wait_for_selector("button[id=yes]")
        page.click("button[id=yes]")

        log("✅ Modem is restarting.")

        browser.close()


if __name__ == "__main__":
    password = get_password(OP_ITEM)
    log_in_and_restart(password)
