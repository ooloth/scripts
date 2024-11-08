"""
Helper functions for Feedbin's entries endpoint.

Docs:
 - https://github.com/feedbin/feedbin-api/blob/master/content/entries.md
"""

from pydantic import BaseModel

from feedbin.api import API, ForbiddenError, HTTPMethod, NotFoundError, RequestArgs, UnexpectedError, make_request
from utils.logs import log


class Entry(BaseModel):
    title: str
    author: str
    url: str
    feed_id: int
    id: int


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

    TODO: handle pagination in this helper so the caller doesn't have to think about it?
    TODO: accept a site_url and look up the feed_id internally?
    """
    request_args = RequestArgs(
        url=f"{API}/feeds/{feed_id}/entries.json",
        params={"read": read, "starred": starred},
    )

    log.info(f"Feedbin: getting entries for feed {feed_id}")
    response = make_request(HTTPMethod.GET, request_args)

    match response.status_code:
        case 200:
            return [Entry(**entry) for entry in response.json()]
        case 403:
            raise ForbiddenError("Feedbin: you are not subscribed to feed {feed_id}")
        case 404:
            raise NotFoundError("Feedbin: no subscriptions found")
        case _:
            raise UnexpectedError("Feedbin: unexpected error while getting subscriptions")
