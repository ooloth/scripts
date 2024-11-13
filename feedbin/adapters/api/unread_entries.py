"""
Adapter for the Feedbin API unread entries endpoint.

Docs:
 - https://github.com/feedbin/feedbin-api/blob/master/content/unread-entries.md
"""

from common.logs import log
from feedbin.adapters.api import API, HTTPMethod, RequestArgs, UnexpectedError, make_request


def create_unread_entries(entry_ids: list[int]) -> list[int]:
    """
    Mark up to 1,000 entry IDs as unread.

    The response will contain all of the entry_ids that were successfully marked as unread.
    If any IDs that were sent are not returned in the response, it usually means the user
    no longer has access to the feed the entry belongs to.
    """
    request_args = RequestArgs(
        url=f"{API}/unread-entries.json",
        json={"unread_entries": entry_ids},
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    log.info(f"Marking {len(entry_ids)} entries as unread")
    response = make_request(HTTPMethod.POST, request_args)

    match response.status_code:
        case 200:
            entry_ids_marked_as_unread = response.json()
            log.info(f"Marked {len(entry_ids_marked_as_unread)} entries as unread")

            entry_ids_not_marked_as_unread = set(entry_ids) - set(entry_ids_marked_as_unread)
            if entry_ids_not_marked_as_unread:
                log.warning(f"Failed to mark the following entries as unread: {entry_ids_not_marked_as_unread}")

            return entry_ids_marked_as_unread
        case _:
            raise UnexpectedError("Unexpected error while marking entries as unread")
