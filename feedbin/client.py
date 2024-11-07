from dataclasses import dataclass
from enum import Enum
from typing import Any

import requests
from pydantic import BaseModel

from op.secrets import get_secret
from utils.logs import log

API = "https://api.feedbin.com/v2"


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


@dataclass
class RequestArgs:
    url: str
    params: dict[str, Any] | None = None
    json: dict[str, Any] | None = None
    headers: dict[str, str] | None = None


class FeedbinError(Exception):
    """Base class for Feedbin API errors."""

    pass


class NotFoundError(FeedbinError):
    """Raised when a resource is not found."""

    pass


class ForbiddenError(FeedbinError):
    """Raised when the caller does not own a resource."""

    pass


class UnexpectedError(FeedbinError):
    "Raised for unexpected errors."

    pass


_auth = None


def _get_auth() -> tuple[str, str]:
    "Retrieve the username and password for the Feedbin API from 1Password."
    global _auth

    if _auth is None:
        username = get_secret("Feedbin", "username")
        password = get_secret("Feedbin", "password")
        _auth = (username, password)

    return _auth


def make_request(method: HTTPMethod, args: RequestArgs) -> requests.Response:
    """
    Make an HTTP request and handle common tasks.

    TODO: expect different request args based on the method?
    """
    return requests.request(
        method.value,
        args.url,
        json=args.json,
        params=args.params,
        headers=args.headers,
        auth=_get_auth(),
    )


class Subscription(BaseModel):
    title: str
    site_url: str
    feed_url: str
    feed_id: int
    id: int


def get_subscriptions() -> list[Subscription]:
    """
    Get all subscriptions.

    Docs:
     - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#get-subscriptions
    """
    request_args = RequestArgs(url=f"{API}/subscriptions.json")

    log.info("Feedbin: getting all subscriptions")
    response = make_request(HTTPMethod.GET, request_args)

    match response.status_code:
        case 200:
            return [Subscription(**sub) for sub in response.json()]
        case 404:
            raise NotFoundError("Feedbin: no subscriptions found")
        case _:
            raise UnexpectedError("Feedbin: unexpected error while getting subscriptions")


class FeedOption(BaseModel):
    feed_url: str
    title: str


class MultipleChoicesError(FeedbinError):
    """Raised when multiple choices are returned."""

    def __init__(self, choices: list[FeedOption]) -> None:
        self.choices = choices
        super().__init__("Feedbin: multiple options returned")


def create_subscription(url: str) -> Subscription:
    """
    Create a subscription from a website or feed URL (with or without the scheme).

    Docs:
     - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md

    TODO: automatically call update_subscription to add emoji suffix to title?
    """
    request_args = RequestArgs(
        url=f"{API}/subscriptions.json",
        json={"feed_url": url},
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    log.info(f"Feedbin: creating subscription for '{url}'")
    response = make_request(HTTPMethod.POST, request_args)

    match response.status_code:
        case 200 | 302:
            log.debug("Feedbin: existing subscription found")
            return Subscription(**response.json())
        case 201:
            log.debug("Feedbin: subscription created")
            return Subscription(**response.json())
        case 300:
            log.debug("Feedbin: multiple feed options found")
            options = [FeedOption(**feed) for feed in response.json()]
            raise MultipleChoicesError(options)
        case 404:
            raise NotFoundError(f"Feedbin: no feed found at {url}")
        case _:
            raise UnexpectedError("Feedbin: unexpected error while creating subscription")


def delete_subscription(subscription_id: int) -> None:
    """
    Delete a subscription.

    Docs:
     - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#delete-subscription

    TODO: add possible responses
    """
    request_args = RequestArgs(url=f"{API}/subscriptions/{subscription_id}.json")

    log.info(f"Feedbin: deleting subscription {subscription_id}")
    response = make_request(HTTPMethod.DELETE, request_args)

    match response.status_code:
        case 204:
            log.debug(f"Feedbin: subscription {subscription_id} deleted")
        case 403:
            raise ForbiddenError(f"Feedbin: you do not own subscription {subscription_id} so you cannot delete it")
        case _:
            raise UnexpectedError("Feedbin: unexpected error while deleting subscription")


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

    Docs:
     - https://github.com/feedbin/feedbin-api/blob/master/content/entries.md#get-v2feeds203entriesjson

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
