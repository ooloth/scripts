from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

import requests
from pydantic import BaseModel

from op.secrets import get_secret
from utils.logs import log

API = "https://api.feedbin.com/v2"

_auth = None


def _get_auth() -> tuple[str, str]:
    "Retrieve the username and password for the Feedbin API from 1Password."
    global _auth

    if _auth is None:
        username = get_secret("Feedbin", "username")
        password = get_secret("Feedbin", "password")
        _auth = (username, password)

    return _auth


@dataclass
class RequestArgs:
    url: str
    params: dict[str, Any] | None = None
    json: dict[str, Any] | None = None
    headers: dict[str, str] | None = None
    # auth: tuple[str, str] | None = None


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


class FeedbinError(Exception):
    """Base class for Feedbin API errors."""

    pass


class NotFoundError(FeedbinError):
    """Raised when a resource is not found."""

    pass


class UnexpectedError(FeedbinError):
    "Raised for unexpected errors."

    pass


def make_request(method: HTTPMethod, args: RequestArgs) -> requests.Response:
    """Make an HTTP request and handle common tasks."""
    response = requests.request(
        method.value,
        args.url,
        json=args.json,
        params=args.params,
        headers=args.headers,
        auth=_get_auth(),
    )
    response.raise_for_status()
    return response


class Subscription(BaseModel):
    title: str
    site_url: str
    feed_url: str
    feed_id: int
    id: int


def get_subscriptions(*, extended: bool = False, since: datetime | None = None) -> list[Subscription]:
    """
    Get all subscriptions.

    Params:
    - extended: Include additional information about the subscription.
    - since: Only return subscriptions that have been updated since this date.

    DOCS: https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#get-subscriptions
    """
    params = {"extended": extended, "since": ""}
    if since:
        params["since"] = since.isoformat()  # convert to ISO 8601 format

    request_args = RequestArgs(
        url=f"{API}/subscriptions.json",
        params={"extended": extended, "since": since},
    )

    log.info(f"Feedbin: getting subscriptions with params: {params}")
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


def create_subscription(url: str) -> Subscription | None:
    """
    Create a subscription.

    DOCS: https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md

    TODO: add params
    TODO: add possible responses
    """
    request_args = RequestArgs(
        url=f"{API}/subscriptions.json",
        json={"feed_url": url},
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    response = make_request(HTTPMethod.POST, request_args)
    # match response.status_code:
    #     case 200:
    #         log(f"✅ Now subscribed to '{url}'")
    return Subscription(**response.json())


def delete_subscription(subscription_id: int) -> None:
    """
    Delete a subscription.

    DOCS: ...

    TODO: add params
    TODO: add possible responses
    """
    request_args = RequestArgs(url=f"{API}/subscriptions/{subscription_id}.json")
    make_request(HTTPMethod.DELETE, request_args)


# TODO: move out of client file
# def choose_between_multiple_feeds(feeds: list[FeedChoice]):
#     """Prompt the user to choose between multiple feeds."""
#     print("Multiple feeds found. Please choose one:")
#     for idx, feed in enumerate(feeds, start=1):
#         print(f"{idx}. {feed.title} ({feed.feed_url})")

#     choice = int(input("Enter the number of the feed you want to subscribe to: "))
#     if 1 <= choice <= len(feeds):
#         selected_feed = feeds[choice - 1]
#         print(f"Selected feed URL: {selected_feed.feed_url}")
#     else:
#         print("Invalid choice")


#####################
# Client as a class #
#####################

_client = None


def get_client() -> "FeedbinClient":
    global _client

    if _client is None:
        _client = FeedbinClient(*_get_auth())

    return _client


class FeedbinClient:
    def __init__(self, username: str, password: str):
        self.auth = (username, password)

    def create_subscription(self, url: str) -> Subscription | None:
        """Create a subscription and handle the response."""
        response = requests.post(
            f"{API}/subscriptions.json",
            auth=self.auth,
            headers={"Content-Type": "application/json; charset=utf-8"},
            json={"feed_url": url},
        )

        if response.status_code == 201:
            return Subscription(**response.json())
        elif response.status_code == 302:
            return Subscription(**response.json())
        elif response.status_code == 404:
            print(f"❌ No feed found at '{url}'")
        elif response.status_code == 300:
            self.choose_between_multiple_feeds(response.json())
        else:
            print(f"❌ Unexpected HTTP status code: {response.status_code}")
            print(response.text)
        return None

    def choose_between_multiple_feeds(self, feeds: list[FeedOption]) -> None:
        """Prompt the user to choose between multiple feeds."""
        print("Multiple feeds found. Please choose one:")
        for idx, feed in enumerate(feeds, start=1):
            print(f"{idx}. {feed.title} ({feed.feed_url})")

        choice = int(input("Enter the number of the feed you want to subscribe to: "))
        if 1 <= choice <= len(feeds):
            selected_feed = feeds[choice - 1]
            print(f"Selected feed URL: {selected_feed.feed_url}")
        else:
            print("Invalid choice")
