# TODO: https://github.com/feedbin/feedbin-api/blob/master/content/taggings.md#create-tagging

from enum import Enum
from typing import Literal

from requests import HTTPError

from rss.entities import FeedId, FeedTag
from rss.utils.feedbin import API, HTTPMethod, RequestArgs, make_request


class CreateTaggingResult(Enum):
    CREATED = "✅ Tagging created"
    EXISTS = "✅ Tagging already exists"
    NOT_FOUND = "⛔️ No RSS feed found with that ID"
    UNEXPECTED_STATUS_CODE = "🚨 Unexpected status code while tagging a feed"
    HTTP_ERROR = "🚨 HTTP error while tagging a feed"
    UNEXPECTED_ERROR = "🚨 Unexpected error while tagging a feed"


CreateTaggingOutput = (
    tuple[Literal[CreateTaggingResult.CREATED], FeedTag]
    | tuple[Literal[CreateTaggingResult.EXISTS], FeedTag]
    | tuple[Literal[CreateTaggingResult.NOT_FOUND], FeedId]
    | tuple[Literal[CreateTaggingResult.UNEXPECTED_STATUS_CODE], int]
    | tuple[Literal[CreateTaggingResult.HTTP_ERROR], str]
    | tuple[Literal[CreateTaggingResult.UNEXPECTED_ERROR], str]
)


def create_tagging(feed_id: FeedId, tag: FeedTag) -> CreateTaggingOutput:
    """
    Tag a feed.

    TODO:
    - Confirm it patches (updates) the tag if it already exists with a different value.
    - If not, see if there's undocumented PATCH functionality (what does the web app call?)

    Docs:
    - https://github.com/feedbin/feedbin-api/blob/master/content/taggings.md#create-tagging
    """
    try:
        request_args = RequestArgs(url=f"{API}/subscriptions.json", json={"feed_url": feed_id.id})
        response = make_request(HTTPMethod.POST, request_args)  # noqa: F821

        match response.status_code:
            case 200 | 302:
                return CreateTaggingResult.EXISTS, tag
            case 201:
                return CreateTaggingResult.CREATED, tag
            case _:
                return CreateTaggingResult.UNEXPECTED_STATUS_CODE, response.status_code
    except HTTPError as e:
        if e.response.status_code == 404:
            return CreateTaggingResult.NOT_FOUND, feed_id
        return CreateTaggingResult.HTTP_ERROR, str(e)
    except Exception as e:
        return CreateTaggingResult.UNEXPECTED_ERROR, str(e)
