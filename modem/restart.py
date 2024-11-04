import os
from datetime import datetime

from playwright.sync_api import sync_playwright

from notifications.sendgrid import send_email
from op.secrets import get_secret
from utils.logs import log


def _log_in_and_restart(url: str, password: str) -> None:
    dry_run = os.getenv("DRY_RUN", False)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Log in
        page.goto(url)
        page.click("button[id=headerLogin]")
        page.wait_for_selector("input[name=admin-password]")
        page.fill("input[name=admin-password]", password)
        page.click("button[id=loginButton]")

        # Navigate to reset options
        page.wait_for_selector("a[href=advancedtools]")
        page.click("a[href=advancedtools]")
        page.wait_for_selector("a[href='advancedtools/resets']")
        page.click("a[href='advancedtools/resets']")

        if dry_run == "true":
            log("🌵 Dry run: skipped restarting modem.")
            return

        # Restart modem and confirm twice
        page.wait_for_selector("button[id=restart]")
        page.click("button[id=restart]")
        page.wait_for_selector("button[id=yes]")
        page.click("button[id=yes]")
        page.wait_for_selector("button[id=yes]")
        page.click("button[id=yes]")

        log("✅ Modem is restarting.")

        browser.close()


def main() -> None:
    modem_url = get_secret("Modem", "website")
    modem_password = get_secret("Modem", "password")
    restart_time = datetime.now().strftime("%A at %I:%M %p")

    try:
        _log_in_and_restart(modem_url, modem_password)
        send_email("✅ Modem restarted", f"<p>Modem restarted {restart_time}.</p>")
    except Exception as e:
        log("🚨 Modem restart failed:", e)
        send_email(
            "🚨 Modem restart failed",
            f"<p>Modem restart failed {restart_time}.</p><hr /><p><strong>Error:</strong></p><pre>{e}</pre>",
        )


if __name__ == "__main__":
    main()
