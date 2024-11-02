# TODO: singleton client

import os

from sendgrid.helpers.mail import Mail  # type: ignore
from sendgrid.sendgrid import SendGridAPIClient  # type: ignore

from utils.logs import log

# Docs:
# - https://github.com/sendgrid/sendgrid-python/blob/main/use_cases/README.md
# - https://github.com/sendgrid/sendgrid-python/blob/main/use_cases/send_a_single_email_to_a_single_recipient.md

_client = None


def get_client() -> SendGridAPIClient:
    global _client

    if _client:
        return _client

    # TODO: locally and in GitHub Actions, should these pull from the op cli instead of the environment for safety?
    _client = SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))

    return _client


def send_email(subject: str, html: str) -> None:
    log("subject:", subject)
    log("html:", html)

    html_heading = "<h1>Script notification:</h1>"
    html = f"{html_heading}{html}"

    message = Mail(
        from_email=os.environ.get("SENDGRID_FROM_EMAIL"),
        to_emails=os.environ.get("SENDGRID_TO_EMAIL"),
        subject=subject,
        html_content=html,
    )

    try:
        client = get_client()
        response = client.send(message)
        log(response.status_code)
        log(response.body)
        log(response.headers)
    except Exception as e:
        log("There was a problem sending that email:", e)
