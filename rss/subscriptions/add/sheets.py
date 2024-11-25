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
from typing import Literal, cast

from google.oauth2.service_account import Credentials
from gspread.auth import authorize
from gspread.client import Client
from gspread.worksheet import Worksheet

# from oauth2client.service_account import ServiceAccountCredentials
from pydantic import BaseModel

from common.logs import log
from rss.entities import EntryId, FeedId, FeedUrl, Subscription, SubscriptionId
from rss.entries.list.feedbin import GetFeedEntriesResult
from rss.entries.list.main import main as get_feed_entries
from rss.entries.mark_unread.feedbin import CreateUnreadEntriesResult
from rss.entries.mark_unread.main import main as mark_entries_unread
from rss.subscriptions.add.feedbin import CreateSubscriptionResult
from rss.subscriptions.add.main import main as add_subscription
from rss.subscriptions.get.feedbin import GetSubscriptionResult
from rss.subscriptions.update.feedbin import UpdateSubscriptionResult
from rss.subscriptions.update.main import main as update_subscription

GOOGLE_CLOUD_CREDENTIALS_JSON = Path.cwd() / "rss/subscriptions/add/.secrets/google-cloud-service-account.json"
GOOGLE_CLOUD_SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

SHEET_NAME = "RSS Feed Wish List 🔖"
DETAILS_COLUMN_NAME = "Details"
FEED_ID_COLUMN_NAME = "Feed ID"
STATUS_COLUMN_NAME = "Status"
SUBSCRIPTION_ID_COLUMN_NAME = "Subscription ID"
URL_COLUMN_NAME = "URL to subscribe to"


class Status(Enum):
    ERROR = "Error"
    NOT_FOUND = "No Feed Found"
    MULTIPLE_CHOICES = "Multiple Feed URLs"
    SUBSCRIBED = "Subscribed"
    BACKLOG_UNREAD = "Backlog Marked Unread"
    SUFFIX_ADDED = "Suffix Added"
    TAG_ADDED = "Tag Added"


class Row(BaseModel):
    index: int
    details: str
    feed_id: FeedId | Literal[""]
    status: Status | Literal[""]
    subscription_id: SubscriptionId | Literal[""]
    url: FeedUrl


def get_authenticated_sheets_client(
    credentials_json: Path = GOOGLE_CLOUD_CREDENTIALS_JSON,
    scopes: list[str] = GOOGLE_CLOUD_SCOPES,
) -> Client:
    # TODO: get keyfile from 1Password?
    credentials = Credentials.from_service_account_file(credentials_json)  # type: ignore
    scoped_credentials = credentials.with_scopes(scopes)
    client = authorize(scoped_credentials)
    return client


def get_worksheet(client: Client, sheet_name: str = SHEET_NAME) -> Worksheet:
    return client.open(sheet_name).sheet1


def get_rows(
    sheet: Worksheet,
    *,
    details_col_name: str = DETAILS_COLUMN_NAME,
    feed_id_col_name: str = FEED_ID_COLUMN_NAME,
    status_col_name: str = STATUS_COLUMN_NAME,
    subscription_id_col_name: str = SUBSCRIPTION_ID_COLUMN_NAME,
    url_col_name: str = URL_COLUMN_NAME,
) -> list[Row]:
    data = sheet.get_all_records()

    return [
        Row(
            index=i,
            details=str(row.get(details_col_name, "")),
            feed_id=FeedId(id=cast(int, row.get(feed_id_col_name))) if row.get(feed_id_col_name) else "",
            status=Status(row.get(status_col_name)) if row.get(status_col_name) else "",
            subscription_id=SubscriptionId(id=cast(int, row.get(subscription_id_col_name)))
            if row.get(subscription_id_col_name)
            else "",
            url=FeedUrl(url=str(row.get(url_col_name, ""))),
        )
        for i, row in enumerate(data, start=2)  # skip header row
    ]


def subscribe_and_return_updated_row(row: Row) -> Row:
    """Subscribe to a URL and return the updated row."""
    if row.status in {Status.SUBSCRIBED, Status.BACKLOG_UNREAD, Status.SUFFIX_ADDED}:
        return row

    result, data = add_subscription(url=row.url)

    match result:
        case CreateSubscriptionResult.CREATED | CreateSubscriptionResult.EXISTS:
            return row.model_copy(
                update={
                    "status": Status.SUBSCRIBED,
                    "details": "",
                    "feed_id": data.feed_id if isinstance(data, Subscription) else "",
                    "subscription_id": data.id if isinstance(data, Subscription) else "",
                }
            )
        case CreateSubscriptionResult.MULTIPLE_CHOICES:
            return row.model_copy(update={"status": Status.MULTIPLE_CHOICES, "details": data})
        case CreateSubscriptionResult.NOT_FOUND:
            return row.model_copy(update={"status": Status.NOT_FOUND, "details": f"{result}: {data}"})
        case (
            CreateSubscriptionResult.HTTP_ERROR
            | CreateSubscriptionResult.UNEXPECTED_ERROR
            | CreateSubscriptionResult.UNEXPECTED_STATUS_CODE
        ):
            return row.model_copy(update={"status": Status.ERROR, "details": f"{result}: {data}"})


def mark_backlog_unread_and_return_updated_row(row: Row, entry_ids: list[EntryId]) -> Row:
    """Mark subscription's entire backlog as unread and return the updated row."""
    if row.status in {Status.BACKLOG_UNREAD, Status.SUFFIX_ADDED} or not isinstance(entry_ids, list):
        return row

    result, data = mark_entries_unread(entry_ids)

    match result:
        case CreateUnreadEntriesResult.OK:
            return row.model_copy(update={"status": Status.BACKLOG_UNREAD, "details": ""})
        case (
            CreateUnreadEntriesResult.HTTP_ERROR
            | CreateUnreadEntriesResult.UNEXPECTED_ERROR
            | CreateUnreadEntriesResult.UNEXPECTED_STATUS_CODE
        ):
            return row.model_copy(update={"status": Status.ERROR, "details": f"{result}: {data}"})


def append_suffix_to_title_and_return_updated_row(row: Row) -> Row:
    """Append 📖 or 📺 to subscription title and return the updated row."""
    if row.status == Status.SUFFIX_ADDED or not isinstance(row.subscription_id, SubscriptionId):
        return row

    result, data = update_subscription(subscription_id=row.subscription_id)

    match result:
        case GetSubscriptionResult.OK | UpdateSubscriptionResult.OK:
            return row.model_copy(
                update={"status": Status.SUFFIX_ADDED, "details": data.title if isinstance(data, Subscription) else ""}
            )
        case (
            GetSubscriptionResult.FORBIDDEN
            | UpdateSubscriptionResult.FORBIDDEN
            | GetSubscriptionResult.NOT_FOUND
            | UpdateSubscriptionResult.NOT_FOUND
        ):
            return row.model_copy(update={"status": Status.NOT_FOUND, "details": f"{result}: {data}"})
        case (
            GetSubscriptionResult.UNEXPECTED_STATUS_CODE
            | UpdateSubscriptionResult.UNEXPECTED_STATUS_CODE
            | GetSubscriptionResult.HTTP_ERROR
            | UpdateSubscriptionResult.HTTP_ERROR
            | GetSubscriptionResult.UNEXPECTED_ERROR
            | UpdateSubscriptionResult.UNEXPECTED_ERROR
        ):
            return row.model_copy(update={"status": Status.ERROR, "details": f"{result}: {data}"})


# TODO: return what happened
def update_row(
    *,
    row: Row,
    row_index: int,
    sheet: Worksheet,
) -> None:
    row_range = f"C{row_index}:F{row_index}"  # columns C to F of the row
    row_values = [
        [
            row.status.value if isinstance(row.status, Status) else row.status,
            row.subscription_id.id if isinstance(row.subscription_id, SubscriptionId) else row.subscription_id,
            row.feed_id.id if isinstance(row.feed_id, FeedId) else row.feed_id,
            str(row.details),
        ]
    ]

    sheet.update(row_values, row_range)


def main() -> None:
    """Subscribe to URLs saved in a Google Sheet and update the sheet with the result."""
    client = get_authenticated_sheets_client()
    sheet = get_worksheet(client)
    rows = get_rows(sheet)
    log.debug(f"🔍 rows: {rows}")

    # TODO: sort/separate by status first? append to next list when ready?
    # TODO: call out multiple choices in terminal at end of run?

    for row in rows:
        if row.status == Status.SUFFIX_ADDED:
            continue

        if row.status not in {Status.SUBSCRIBED, Status.BACKLOG_UNREAD, Status.SUFFIX_ADDED}:
            row_after_subscribing = subscribe_and_return_updated_row(row)
            log.debug(f"🔍 row_after_subscribing: {row_after_subscribing}")
            update_row(row=row_after_subscribing, row_index=row_after_subscribing.index, sheet=sheet)

        if row.status not in {Status.BACKLOG_UNREAD, Status.SUFFIX_ADDED} and isinstance(
            row_after_subscribing.feed_id, FeedId
        ):
            result, entries = get_feed_entries(feed_id=row_after_subscribing.feed_id)
            if result != GetFeedEntriesResult.OK or not isinstance(entries, list):
                log.error(f"Expected list of entries, got {entries}")
                return

            entry_ids = [EntryId(id=entry.id) for entry in entries]
            row_after_marking_backlog_unread = mark_backlog_unread_and_return_updated_row(
                row_after_subscribing, entry_ids
            )
            log.debug(f"🔍 row_after_marking_backlog_unread: {row_after_marking_backlog_unread}")
            update_row(
                row=row_after_marking_backlog_unread, row_index=row_after_marking_backlog_unread.index, sheet=sheet
            )

        if isinstance(row_after_subscribing.subscription_id, SubscriptionId):
            row_after_appending_suffixes = append_suffix_to_title_and_return_updated_row(
                row_after_marking_backlog_unread
            )
            log.debug(f"🔍 row_after_appending_suffixes: {row_after_appending_suffixes}")
            update_row(row=row_after_appending_suffixes, row_index=row_after_appending_suffixes.index, sheet=sheet)


if __name__ == "__main__":
    main()
