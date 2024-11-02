from datetime import datetime

from playwright.sync_api import sync_playwright

from notifications.sendgrid import send_email
from op.items import get_item_field_value
from utils.logs import log

# TODO: deploy to GitHub Actions!

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


def main() -> None:
    # TODO: should this also be an environment variable? or should all credentials be pulled from op at runtime like this?
    password = get_item_field_value(OP_ITEM, "password")
    restart_time = datetime.now().strftime("on %A at %I:%M %p")

    try:
        log_in_and_restart(password)
        send_email("✅ Modem restarted", f"<p>The modem was restarted {restart_time}.</p>")
    except Exception as e:
        log("🚨 Error while restarting the modem:", e)
        send_email(
            "🚨 Modem restart failed",
            f"<p>The modem failed to restart {restart_time}:</p><br /><pre>{str(e)}</pre>",
        )


if __name__ == "__main__":
    main()
