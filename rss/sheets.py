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

import json
from enum import Enum
from functools import partial
from itertools import groupby
from typing import Callable, Literal

from google.oauth2.service_account import Credentials
from gspread.auth import authorize
from gspread.client import Client
from gspread.worksheet import Worksheet
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

# from common.fp import pipe
from common.logs import log
from common.secrets import get_secret
from common.sendgrid import send_email
from rss.domain import EntryId, FeedId, FeedUrl, Subscription, SubscriptionId
from rss.entries.list.feedbin import GetFeedEntriesResult, get_feed_entries
from rss.entries.mark_unread.feedbin import CreateUnreadEntriesResult, create_unread_entries
from rss.subscriptions.add.feedbin import CreateSubscriptionResult, create_subscription
from rss.subscriptions.update.feedbin import UpdateSubscriptionResult, update_subscription
from rss.subscriptions.update.main import generate_new_title

GOOGLE_CLOUD_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
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


class Row(BaseModel):
    index: int
    details: str
    feed_id: FeedId | Literal[""]
    status: Status
    subscription_id: SubscriptionId | Literal[""]
    url: FeedUrl


JsonParsed = dict[str, str]


def get_authenticated_sheets_client(
    service_account_info: JsonParsed,
    scopes: list[str],
) -> Client:
    credentials = Credentials.from_service_account_info(service_account_info)  # type: ignore
    scoped_credentials = credentials.with_scopes(scopes)
    client = authorize(scoped_credentials)
    return client


def get_worksheet(client: Client, sheet_name: str = SHEET_NAME) -> Worksheet:
    """Get the form responses worksheet from the Google Sheet."""
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
    """Get the parsed rows from the Google Sheet."""
    data = sheet.get_all_records()

    return [
        Row(
            index=i,
            details=str(row.get(details_col_name, "")),
            feed_id=FeedId(row[feed_id_col_name]) if row.get(feed_id_col_name) else "",
            status=Status(row[status_col_name]) if row.get(status_col_name) else Status.NEW,
            subscription_id=SubscriptionId(row[subscription_id_col_name])
            if row.get(subscription_id_col_name)
            else "",
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
            return row.model_copy(
                update={"status": Status.NOT_FOUND, "details": f"{result}: {data}"}
            )
        case (
            CreateSubscriptionResult.HTTP_ERROR
            | CreateSubscriptionResult.UNEXPECTED_ERROR
            | CreateSubscriptionResult.UNEXPECTED_STATUS_CODE
        ):
            return row.model_copy(update={"status": Status.ERROR, "details": f"{result}: {data}"})


def mark_backlog_unread_and_return_updated_row(row: Row, entry_ids: list[EntryId]) -> Row:
    """Mark subscription's entire backlog as unread and return the updated row."""
    if row.status in {Status.BACKLOG_UNREAD, Status.SUFFIX_ADDED} or not isinstance(
        entry_ids, list
    ):
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
        return row.model_copy(
            update={"status": Status.ERROR, "details": "Failed to generate new title"}
        )

    result, data = update_subscription(subscription_id=row.subscription_id, new_title=new_title)

    match result:
        case UpdateSubscriptionResult.OK:
            return row.model_copy(
                update={
                    "status": Status.SUFFIX_ADDED,
                    "details": data.title if isinstance(data, Subscription) else data,
                }
            )
        case UpdateSubscriptionResult.FORBIDDEN | UpdateSubscriptionResult.NOT_FOUND:
            return row.model_copy(
                update={"status": Status.NOT_FOUND, "details": f"{result}: {data}"}
            )
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
    """Update the row in the Google Sheet."""
    row_range = f"C{row_index}:F{row_index}"  # columns C to F of the row
    row_values = [[row.status.value, row.subscription_id, row.feed_id, str(row.details)]]

    sheet.update(row_values, row_range)


def process_new_row(row: Row, sheet: Worksheet) -> Row:
    if row.status != Status.NEW:
        return row

    processed_row = subscribe_and_return_updated_row(row)
    update_row(row=processed_row, row_index=processed_row.index, sheet=sheet)
    return processed_row


def partially_apply_sheet(
    sheet: Worksheet,
    funcs: list[Callable[..., Row]],
) -> list[Callable[..., Row]]:
    return [partial(func, sheet=sheet) for func in funcs]


def process_rows(rows: list[Row], sheet: Worksheet) -> list[Row]:
    """
    TODO:
    - Accumulate API calls and return them to be made in bulk later?
    - Recursively call until all rows are in a terminal state?
    - Make one bulk spreadsheet update at the end instead of defensively updating status throughout?
    """

    # functions = partially_apply_sheet(
    #     sheet, [process_new_row, process_subscribed_row, process_backlog_unread_row]
    # )

    # new_to_subscribed = partial(process_new_row, sheet=sheet)
    # new_to_subscribed = partial(process_new_row, sheet=sheet)
    # subscribed_to_unread = partial(process_subscribed_row, sheet=sheet)
    # unread_to_renamed = partial(process_unread_backlog_row, sheet=sheet)

    # def process_row(row: Row) -> Row:
    #     processed_row = pipe(row, *functions)
    #     processed_row = pipe(row, process_new_row, process_subscribed_row, process_backlog_unread_row)

    #     processed_row = reduce(
    #         lambda acc, f: f(acc),
    #         (new_to_subscribed, new_to_subscribed, new_to_subscribed),
    #         row,
    #     )

    #     if not isinstance(processed_row, Row):
    #         log.error(f"🚨 failed to process row: {row}")
    #         return row

    #     return processed_row

    # return list(map(process_row, rows))

    processed_rows: list[Row] = []

    for row in rows:
        if row.status == Status.SUFFIX_ADDED:
            log.debug(f"🔍 already processed: {row.url}")
            processed_rows.append(row)
            continue

        processed_row = row

        if row.status == Status.NEW:
            processed_row = subscribe_and_return_updated_row(row)
            update_row(row=processed_row, row_index=processed_row.index, sheet=sheet)
            log.debug(f"🔍 updated_row: {processed_row}")

        if processed_row.status == Status.SUBSCRIBED and isinstance(processed_row.feed_id, FeedId):
            result, entries = get_feed_entries(feed_id=processed_row.feed_id)
            if result != GetFeedEntriesResult.OK or not isinstance(entries, list):
                processed_row = processed_row.model_copy(update={"details": f"{result}: {entries}"})
                log.debug(f"🔍 updated_row: {processed_row}")
                update_row(row=processed_row, row_index=processed_row.index, sheet=sheet)
                processed_rows.append(processed_row)
                continue

            entry_ids = [EntryId(entry.id) for entry in entries]
            processed_row = mark_backlog_unread_and_return_updated_row(processed_row, entry_ids)
            log.debug(f"🔍 updated_row: {processed_row}")
            update_row(row=processed_row, row_index=processed_row.index, sheet=sheet)

        if processed_row.status == Status.BACKLOG_UNREAD and isinstance(
            processed_row.subscription_id, SubscriptionId
        ):
            processed_row = append_suffix_to_title_and_return_updated_row(processed_row)
            log.debug(f"🔍 updated_row: {processed_row}")
            update_row(row=processed_row, row_index=processed_row.index, sheet=sheet)

        processed_rows.append(processed_row)

    return processed_rows


def generate_results_email(original_rows: list[Row], updated_rows: list[Row]) -> tuple[str, str]:
    """Generate the email subject and HTML body for the results."""
    subject = "✅ RSS Feed Wish List Updated"

    def group_rows_by_status(rows: list[Row]) -> dict[str, list[Row]]:
        """Sort rows by status, then group by status."""
        rows.sort(key=lambda row: row.status.value)
        grouped_rows = {
            status: list(items) for status, items in groupby(rows, key=lambda row: row.status.value)
        }
        return grouped_rows

    def generate_html(grouped_rows: dict[str, list[Row]]) -> str:
        """Output the URLs in the sheet, grouped by their status, sorted by the Status enum field order."""
        status_order = {status.value: index for index, status in enumerate(Status)}
        sorted_grouped_rows = sorted(grouped_rows.items(), key=lambda item: status_order[item[0]])
        html_fragments = [
            f"<h3>{status}</h3><ul>{''.join(f'<li>{row.url}</li>' for row in rows)}</ul>"
            for status, rows in sorted_grouped_rows
        ]
        return "".join(html_fragments)

    rows_by_status = group_rows_by_status(updated_rows)
    html = generate_html(rows_by_status)

    return subject, html


def generate_results_table(rows: list[Row]) -> Table:
    table = Table(title="Results:", show_header=True, title_justify="left", title_style="bold cyan")
    table.add_column(header="Row", style="magenta", no_wrap=True)
    table.add_column(header="Status", style="cyan", no_wrap=True)
    table.add_column(header="URL", style="yellow", no_wrap=True)
    table.add_column(header="Details", style="white", no_wrap=True)

    for i, row in enumerate(rows, start=2):
        table.add_row(
            str(i),
            row.status.value if isinstance(row.status, Status) else "Unknown",
            row.url,
            str(row.details),
        )

    return table


def main() -> None:
    """Subscribe to URLs saved in a Google Sheet and update the sheet with the result."""
    service_account_key_json = json.loads(
        get_secret("Google Cloud Service Account Key", "michael-uloth-f8d0e53fdb41.json")
    )

    # I/O
    client = get_authenticated_sheets_client(service_account_key_json, GOOGLE_CLOUD_SCOPES)
    sheet = get_worksheet(client)
    rows = get_rows(sheet)

    # TODO: make pure + make the API calls in bulk later?
    updated_rows = process_rows(rows, sheet)
    subject, html = generate_results_email(rows, updated_rows)
    table = generate_results_table(updated_rows)

    # I/O
    send_email(subject, html)
    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
