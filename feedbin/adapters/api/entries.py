"""
Adapter for the Feedbin API entries endpoint.

Docs:
 - https://github.com/feedbin/feedbin-api/blob/master/content/entries.md#get-v2feeds203entriesjson
"""

from requests import HTTPError

from common.logs import log
from feedbin.adapters.api import (
    API,
    ForbiddenError,
    NotFoundError,
    RequestArgs,
    UnexpectedError,
    make_paginated_request,
)
from feedbin.domain.entities import Entry


def get_feed_entries(
    feed_id: int,
    *,
    read: bool | None = None,
    starred: bool | None = None,
) -> list[Entry]:
    """
    Get all entries for a feed.

    Params:
     - read: Filter by read status. Options: True, False, None.
     - starred: Filter by starred status. Options: True, False, None.

    TODO: accept a site_url and look up the feed_id internally?
    """
    log.debug(f"Getting entries for feed {feed_id}")

    request_args = RequestArgs(
        url=f"{API}/feeds/{feed_id}/entries.json",
        params={"read": read, "starred": starred},
    )

    try:
        all_entries = make_paginated_request(request_args)
        entries = [Entry(**entry) for entry in all_entries]
        log.debug(f"Found {len(entries)} entries for feed {feed_id}")
        return entries
    except HTTPError as e:
        match e.response.status_code:
            case 403:
                raise ForbiddenError("You are not subscribed to feed {feed_id}")
            case 404:
                raise NotFoundError("No feed with an ID of {feed} found")
            case _:
                raise UnexpectedError("Unexpected error while getting entries for feed {feed_id}")
