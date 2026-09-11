"""Feedbin API interactions for listing all entries in an RSS feed subscription."""

from enum import Enum
from typing import Literal

from requests import HTTPError

from rss.domain import Entry, FeedId
from rss.utils.feedbin import API, RequestArgs, make_paginated_request


class GetFeedEntriesResult(str, Enum):
    OK = "✅ Feed entries found"
    FORBIDDEN = "⛔️ You are not subscribed to this feed"
    NOT_FOUND = "⛔️ No feed found with that ID"
    UNEXPECTED_STATUS_CODE = "🚨 Unexpected status code while listing feed entries"
    HTTP_ERROR = "🚨 HTTP error while listing feed entries"
    UNEXPECTED_ERROR = "🚨 Unexpected error while listing feed entries"


GetFeedEntriesOutput = (
    tuple[Literal[GetFeedEntriesResult.OK], list[Entry]]
    | tuple[Literal[GetFeedEntriesResult.FORBIDDEN], FeedId]
    | tuple[Literal[GetFeedEntriesResult.NOT_FOUND], FeedId]
    | tuple[Literal[GetFeedEntriesResult.UNEXPECTED_STATUS_CODE], int]
    | tuple[Literal[GetFeedEntriesResult.HTTP_ERROR], str]
    | tuple[Literal[GetFeedEntriesResult.UNEXPECTED_ERROR], str]
)


def get_feed_entries(
    feed_id: FeedId,
    *,
    read: bool | None = None,
    starred: bool | None = None,
) -> GetFeedEntriesOutput:
    """
    Get all entries for a feed.

    Params:
    - read: Filter by read status. Options: True, False, None.
    - starred: Filter by starred status. Options: True, False, None.

    Docs:
    - https://github.com/feedbin/feedbin-api/blob/master/content/entries.md#get-v2feeds203entriesjson

    TODO:
    - accept a site_url and look up the feed_id internally?
    """
    request_args = RequestArgs(
        url=f"{API}/feeds/{feed_id}/entries.json",
        params={"read": read, "starred": starred},
    )

    try:
        all_entries = make_paginated_request(request_args)
        entries = [Entry(id=entry["id"]) for entry in all_entries]
        return GetFeedEntriesResult.OK, entries
    except HTTPError as e:
        match e.response.status_code:
            case 403:
                return GetFeedEntriesResult.FORBIDDEN, feed_id
            case 404:
                return GetFeedEntriesResult.NOT_FOUND, feed_id
        return GetFeedEntriesResult.HTTP_ERROR, str(e)
    except Exception as e:
        return GetFeedEntriesResult.UNEXPECTED_ERROR, str(e)
