import os

import typer
from playwright.sync_api import sync_playwright

from common.logs import log
from common.pushover import send_notification
from common.secrets import get_secret
from common.typer import DryRun

app = typer.Typer(no_args_is_help=True)


def _log_in_and_restart(url: str, password: str, *, dry_run: bool) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        log.info("🔐 Logging into modem settings")

        page.goto(url)
        page.click("button[id=headerLogin]")
        page.wait_for_selector("input[name=admin-password]")
        page.fill("input[name=admin-password]", password)
        page.click("button[id=loginButton]")

        log.info("🗺️  Navigating to reset options")

        page.wait_for_selector("a[href=advancedtools]")
        page.click("a[href=advancedtools]")
        page.wait_for_selector("a[href='advancedtools/resets']")
        page.click("a[href='advancedtools/resets']")

        if dry_run:
            log.info("🌵 Skipping modem restart (dry run)")
            return

        log.info("🔄 Restarting modem")

        page.wait_for_selector("button[id=restart]")
        page.click("button[id=restart]")
        page.wait_for_selector("button[id=yes]")
        page.click("button[id=yes]")
        page.wait_for_selector("button[id=yes]")
        page.click("button[id=yes]")

        log.info("✅ Modem is restarting.")

        browser.close()


@app.command("restart")
def restart(dry_run: DryRun = False) -> None:
    modem_url = get_secret("Modem", "website")
    modem_password = get_secret("Modem", "password")
    dry_run = os.getenv("DRY_RUN") == "true" or dry_run

    try:
        _log_in_and_restart(modem_url, modem_password, dry_run=dry_run)
        send_notification(
            title="✅ Modem restarted",
            html="<p>Modem restarted. 📡 ↪️</p>",
            dry_run=dry_run,
        )
    except Exception as e:
        log.error("🚨 Modem restart failed")
        send_notification(
            title="🚨 Modem restart failed",
            html=f"<p>Modem restart failed.</p><p><strong>Error:</strong></p><hr /><pre>{e}</pre>",
            dry_run=dry_run,
        )


if __name__ == "__main__":
    # This is the GitHub Actions entrypoint
    restart()
