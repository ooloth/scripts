"""
Helper functions for Feedbin's subscriptions endpoint.

Docs:
 - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md
"""

from pydantic import BaseModel

from feedbin.api import (
    API,
    FeedbinError,
    ForbiddenError,
    HTTPMethod,
    NotFoundError,
    RequestArgs,
    UnexpectedError,
    make_request,
)
from utils.logs import log


class Subscription(BaseModel):
    title: str
    site_url: str
    feed_url: str
    feed_id: int
    id: int


def get_subscriptions() -> list[Subscription]:
    """Get all of my subscriptions."""
    request_args = RequestArgs(url=f"{API}/subscriptions.json")

    log.info("Feedbin: getting all subscriptions")
    response = make_request(HTTPMethod.GET, request_args)

    match response.status_code:
        case 200:
            return [Subscription(**sub) for sub in response.json()]
        case 403:
            raise ForbiddenError("Feedbin: you are not authenticated")
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

    TODO:
     - automatically call update_subscription to add emoji suffix to title?
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
