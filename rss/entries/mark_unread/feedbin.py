"""Feedbin API interactions for marking RSS feed entries as unread."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal

from requests import HTTPError

from rss.entries.entities import EntryId
from rss.utils.feedbin import API, HTTPMethod, RequestArgs, make_request

MAX_ENTRIES_PER_BATCH = 1000


class CreateUnreadEntriesResult(Enum):
    OK = "✅ Entries marked as unread"
    UNEXPECTED_STATUS_CODE = "🚨 Unexpected status code while marking entries as unread"
    HTTP_ERROR = "🚨 HTTP error while marking entries as unread"
    UNEXPECTED_ERROR = "🚨 Unexpected error while marking entries as unread"


@dataclass(frozen=True)
class UnreadEntriesResponse:
    marked_as_unread: set[EntryId]
    not_marked_as_unread: set[EntryId]


CreateUnreadEntriesOutput = (
    tuple[Literal[CreateUnreadEntriesResult.OK], UnreadEntriesResponse]
    | tuple[Literal[CreateUnreadEntriesResult.UNEXPECTED_STATUS_CODE], int]
    | tuple[Literal[CreateUnreadEntriesResult.HTTP_ERROR], str]
    | tuple[Literal[CreateUnreadEntriesResult.UNEXPECTED_ERROR], str]
)


def create_unread_entries(entry_ids: list[EntryId]) -> CreateUnreadEntriesOutput:
    """
    Mark up to 1,000 entry IDs as unread.

    The response will contain all of the entry IDs that were successfully marked as unread.
    If any IDs that were sent are not returned in the response, it usually means the user
    no longer has access to the feed the entry belongs to.

    Docs:
    - https://github.com/feedbin/feedbin-api/blob/master/content/unread-entries.md
    """
    ids_as_ints = [id.__root__ for id in entry_ids]
    marked_as_unread: set[int] = set()
    not_marked_as_unread: set[int] = set()

    for i in range(0, len(ids_as_ints), MAX_ENTRIES_PER_BATCH):
        batch = ids_as_ints[i : i + MAX_ENTRIES_PER_BATCH]

        request_args = RequestArgs(
            url=f"{API}/unread_entries.json",
            json={"unread_entries": batch},
        )

        try:
            response = make_request(HTTPMethod.POST, request_args)

            match response.status_code:
                case 200:
                    ids_marked_unread: set[int] = {int(id) for id in response.json()}  # TODO: validate?
                    ids_not_marked_unread: set[int] = set(batch) - set(ids_marked_unread)
                    marked_as_unread.add(*ids_marked_unread)
                    not_marked_as_unread.add(*ids_not_marked_unread)
                case _:
                    return CreateUnreadEntriesResult.UNEXPECTED_STATUS_CODE, response.status_code
        except HTTPError as e:
            return CreateUnreadEntriesResult.HTTP_ERROR, str(e)
        except Exception as e:
            return CreateUnreadEntriesResult.UNEXPECTED_ERROR, str(e)

    return CreateUnreadEntriesResult.OK, UnreadEntriesResponse(
        marked_as_unread={EntryId(id) for id in marked_as_unread},
        not_marked_as_unread={EntryId(id) for id in not_marked_as_unread},
    )
