"""
Handler for bulk subscribing to URLs saved to a Google Sheet.

TODO:
- Run in Github Actions on a schedule?

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

from google.oauth2.service_account import Credentials
from gspread.auth import authorize
from gspread.client import Client
from gspread.worksheet import Worksheet
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

from common.logs import log
from rss.domain import EntryId, FeedId, FeedUrl, Subscription, SubscriptionId
from rss.entries.list.feedbin import GetFeedEntriesResult, get_feed_entries
from rss.entries.mark_unread.feedbin import CreateUnreadEntriesResult, create_unread_entries
from rss.subscriptions.add.feedbin import CreateSubscriptionResult, create_subscription
from rss.subscriptions.update.feedbin import UpdateSubscriptionResult, update_subscription
from rss.subscriptions.update.main import generate_new_title

GOOGLE_CLOUD_CREDENTIALS_JSON = Path.cwd() / "rss/.secrets/google-cloud-service-account.json"
GOOGLE_CLOUD_SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "RSS Feed Wish List 🔖"


class ColumnName(str, Enum):
    DETAILS = "Details"
    FEED_ID = "Feed ID"
    STATUS = "Status"
    SUBSCRIPTION_ID = "Subscription ID"
    URL = "URL to subscribe to"


class Status(str, Enum):
    NEW = "New"
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
    status: Status
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
    details_col_name: ColumnName = ColumnName.DETAILS,
    feed_id_col_name: ColumnName = ColumnName.FEED_ID,
    status_col_name: ColumnName = ColumnName.STATUS,
    subscription_id_col_name: ColumnName = ColumnName.SUBSCRIPTION_ID,
    url_col_name: ColumnName = ColumnName.URL,
) -> list[Row]:
    data = sheet.get_all_records()

    return [
        Row(
            index=i,
            details=str(row.get(details_col_name, "")),
            feed_id=FeedId(row[feed_id_col_name]) if row.get(feed_id_col_name) else "",
            status=Status(row[status_col_name]) if row.get(status_col_name) else Status.NEW,
            subscription_id=SubscriptionId(row[subscription_id_col_name]) if row.get(subscription_id_col_name) else "",
            url=FeedUrl(row[url_col_name] if row.get(url_col_name) else ""),
        )
        for i, row in enumerate(data, start=2)  # skip header row
    ]


def subscribe_and_return_updated_row(row: Row) -> Row:
    """Subscribe to a URL and return the updated row."""
    if row.status in {Status.SUBSCRIBED, Status.BACKLOG_UNREAD, Status.SUFFIX_ADDED}:
        return row

    result, data = create_subscription(url=row.url)

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

    result, data = create_unread_entries(entry_ids)

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

    new_title = generate_new_title(row.subscription_id)
    if new_title is None:
        return row.model_copy(update={"status": Status.ERROR, "details": "Failed to generate new title"})

    result, data = update_subscription(subscription_id=row.subscription_id, new_title=new_title)

    match result:
        case UpdateSubscriptionResult.OK:
            return row.model_copy(
                update={"status": Status.SUFFIX_ADDED, "details": data.title if isinstance(data, Subscription) else ""}
            )
        case UpdateSubscriptionResult.FORBIDDEN | UpdateSubscriptionResult.NOT_FOUND:
            return row.model_copy(update={"status": Status.NOT_FOUND, "details": f"{result}: {data}"})
        case (
            UpdateSubscriptionResult.UNEXPECTED_STATUS_CODE
            | UpdateSubscriptionResult.HTTP_ERROR
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
    row_values = [[row.status.value, row.subscription_id, row.feed_id, str(row.details)]]

    sheet.update(row_values, row_range)


def process_rows(rows: list[Row], sheet: Worksheet) -> list[Row]:
    """
    TODO:
    - Make less imperative and more functional
    - Accumulate API calls and return them to be made in bulk later?
    - Recursively call until all rows are in a terminal state?
    - Make one bulk spreadsheet update at the end instead of defensively updating status throughout?
    """

    updated_rows: list[Row] = []

    for row in rows:
        if row.status == Status.SUFFIX_ADDED:
            log.debug(f"🔍 already processed: {row.url}")
            updated_rows.append(row)
            continue

        updated_row = row

        if row.status == Status.NEW:
            updated_row = subscribe_and_return_updated_row(row)
            update_row(row=updated_row, row_index=updated_row.index, sheet=sheet)
            log.debug(f"🔍 updated_row: {updated_row}")

        if updated_row.status == Status.SUBSCRIBED and isinstance(updated_row.feed_id, FeedId):
            result, entries = get_feed_entries(feed_id=updated_row.feed_id)
            if result != GetFeedEntriesResult.OK or not isinstance(entries, list):
                msg = f"{result}: {entries}"
                log.error(msg)
                updated_row = updated_row.model_copy(update={"details": msg})
                log.debug(f"🔍 updated_row: {updated_row}")
                update_row(row=updated_row, row_index=updated_row.index, sheet=sheet)
                updated_rows.append(updated_row)
                continue

            entry_ids = [EntryId(entry.id) for entry in entries]
            updated_row = mark_backlog_unread_and_return_updated_row(updated_row, entry_ids)
            log.debug(f"🔍 updated_row: {updated_row}")
            update_row(row=updated_row, row_index=updated_row.index, sheet=sheet)

        if updated_row.status == Status.BACKLOG_UNREAD and isinstance(updated_row.subscription_id, SubscriptionId):
            updated_row = append_suffix_to_title_and_return_updated_row(updated_row)
            log.debug(f"🔍 updated_row: {updated_row}")
            update_row(row=updated_row, row_index=updated_row.index, sheet=sheet)

        updated_rows.append(updated_row)

    return updated_rows


def generate_results_table(rows: list[Row]) -> Table:
    table = Table(title="Results:", show_header=True, title_justify="left", title_style="bold cyan")
    table.add_column(header="Row", style="magenta", no_wrap=True)
    table.add_column(header="Status", style="cyan", no_wrap=True)
    table.add_column(header="URL", style="yellow", no_wrap=True)
    table.add_column(header="Details", style="white", no_wrap=True)

    for idx, row in enumerate(rows, start=2):
        table.add_row(
            str(idx),
            row.status.value if isinstance(row.status, Status) else "Unknown",
            row.url,
            row.details,
        )

    return table


def main() -> None:
    """Subscribe to URLs saved in a Google Sheet and update the sheet with the result."""
    # I/O
    client = get_authenticated_sheets_client()
    sheet = get_worksheet(client)
    rows = get_rows(sheet)

    # TODO: make pure + make the API calls in bulk later?
    updated_rows = process_rows(rows, sheet)
    table = generate_results_table(updated_rows)

    # I/O
    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
