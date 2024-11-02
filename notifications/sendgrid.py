from sendgrid.helpers.mail import Mail  # type: ignore
from sendgrid.sendgrid import SendGridAPIClient  # type: ignore

from op.secrets import get_secret
from utils.logs import log

OP_ITEM = "SendGrid"

_client = None


def get_client() -> SendGridAPIClient:
    global _client

    if _client:
        return _client

    _client = SendGridAPIClient(api_key=get_secret(OP_ITEM, "api key"))

    return _client


def send_email(subject: str, html: str) -> None:
    """
    Send an email with a standard heading and the given subject and HTML content.
    See: https://github.com/sendgrid/sendgrid-python/blob/main/use_cases/send_a_single_email_to_a_single_recipient.md
    """
    message = Mail(
        from_email=get_secret(OP_ITEM, "from email"),
        to_emails=get_secret(OP_ITEM, "to email"),
        subject=subject,
        html_content=html,
    )

    try:
        client = get_client()
        client.send(message)
        log("✅ Email sent successfully.")
    except Exception as e:
        log("🚨 There was a problem sending that email:", e)
