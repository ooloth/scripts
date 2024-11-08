import os

from sendgrid.helpers.mail import Mail  # type: ignore
from sendgrid.sendgrid import SendGridAPIClient  # type: ignore

from op.secrets import get_secret
from utils.logs import log

OP_ITEM = "SendGrid"
OP_FIELD = "api key"

_client = None


def get_client() -> SendGridAPIClient:
    """Return a reusable SendGrid client."""
    global _client

    if _client is None:
        _client = SendGridAPIClient(api_key=get_secret(OP_ITEM, OP_FIELD))

    return _client


def send_email(subject: str, html: str, *, dry_run: bool = False) -> None:
    """
    Send an email with a standard heading and the given subject and HTML content.
    See: https://github.com/sendgrid/sendgrid-python/blob/main/use_cases/send_a_single_email_to_a_single_recipient.md
    """
    dry_run = os.getenv("DRY_RUN") == "true" or dry_run

    message = Mail(
        from_email=get_secret(OP_ITEM, "from email"),
        to_emails=get_secret(OP_ITEM, "to email"),
        subject=subject,
        html_content=html,
    )

    try:
        client = get_client()

        if dry_run:
            log.info(f"🌵 Skipping '{subject}' email (dry run)")
            return

        client.send(message)
        log.info("✅ Email sent successfully.")
    except Exception:
        log.error(f"🚨 There was a problem sending the '{subject}' email")
