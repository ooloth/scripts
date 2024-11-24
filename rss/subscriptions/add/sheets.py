"""
Handler for bulk subscribing to URLs saved to a Google Sheet.

SETUP:

Step 1: Set Up Google Cloud Project
- Go to the Google Cloud Console: https://console.cloud.google.com/
- Create a new project.
- Enable the Google Sheets API for the project: https://console.cloud.google.com/apis/dashboard
- See: https://docs.gspread.org/en/latest/oauth2.html

Step 2: Create Service Account
- In the Google Cloud Console, go to IAM & Admin > Service Accounts.
- Create a new service account.
- Download the JSON key file for the service account.

Step 3: Share Google Sheet
- Open the Google Sheet you want to interact with.
- Share the sheet with the service account email (found in the JSON key file).
"""

from enum import Enum
from pathlib import Path
from typing import Literal

from gspread.auth import authorize
from gspread.client import Client
from gspread.worksheet import Worksheet
from oauth2client.service_account import ServiceAccountCredentials
from pydantic import BaseModel

from common.logs import log

GOOGLE_CLOUD_CREDENTIALS_JSON = Path.cwd() / "rss/subscriptions/add/.secrets/google-cloud-service-account.json"
GOOGLE_CLOUD_SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "RSS Feed Wish List 🔖"
STATUS_COLUMN_INDEX = 3
URL_COLUMN_NAME = "URL to subscribe to"


class Status(Enum):
    SUBSCRIBED = "Subscribed"
    ERROR = "Error"


class Row(BaseModel):
    index: int
    url: str
    status: Status | Literal[""]


# Authenticate and create a client
def get_authenticated_sheets_client(
    credentials_json: Path = GOOGLE_CLOUD_CREDENTIALS_JSON,
    scopes: list[str] = GOOGLE_CLOUD_SCOPES,
) -> Client:
    # TODO: get keyfile from 1Password?
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_json, scopes)
    client = authorize(creds)
    return client


def get_worksheet(client: Client, sheet_name: str = SHEET_NAME) -> Worksheet:
    return client.open(sheet_name).sheet1


def get_rows(sheet: Worksheet) -> list[Row]:
    data = sheet.get_all_records()

    return [
        Row(
            index=i,
            url=str(row[URL_COLUMN_NAME]),
            status=Status(row["Status"]) if row["Status"] else "",
        )
        for i, row in enumerate(data, start=1)
    ]


# TODO: return what happened
def update_row_status(
    *,
    sheet: Worksheet,
    row: int,
    col: int = STATUS_COLUMN_INDEX,
    status: Status,
) -> None:
    sheet.update_cell(row, col, status.value)


def main() -> None:
    client = get_authenticated_sheets_client()
    sheet = get_worksheet(client)
    rows = get_rows(sheet)
    log.debug(f"🔍 rows: {rows}")

    # TODO: Subscribe to URLs

    # Update status for the first URL
    # update_row_status(sheet=sheet, row=2, status=Status.SUBSCRIBED)


if __name__ == "__main__":
    main()

# TODO: get URLs from sheet
# TODO: subscribe to URLs
# TODO: update status in sheet
# TODO: for multiple choices, add options to sheet
# TODO: for errors, add error message to sheet
# TODO: for successful subscriptions, mark backlog unread
# TODO: for successful subscriptions, append correct suffix to title
# TODO: for successful subscriptions, add feed title to sheet
