"""
Adapter for the Feedbin API subscriptions endpoint.

Docs:
 - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md
"""

from pydantic import BaseModel

from common.logs import log
from feedbin.adapters.api import (
    API,
    FeedbinError,
    ForbiddenError,
    HTTPMethod,
    NotFoundError,
    RequestArgs,
    UnexpectedError,
    make_request,
)
from feedbin.domain.entities import Subscription


def get_subscriptions() -> list[Subscription]:
    """Get all of my subscriptions."""
    request_args = RequestArgs(url=f"{API}/subscriptions.json")

    log.debug("Getting all Feedbin subscriptions")
    response = make_request(HTTPMethod.GET, request_args)

    match response.status_code:
        case 200:
            subscriptions = [Subscription(**sub) for sub in response.json()]
            log.debug(f"Found {len(subscriptions)} subscriptions")
            return subscriptions
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
    )

    log.debug(f"Creating subscription for '{url}'")
    response = make_request(HTTPMethod.POST, request_args)

    match response.status_code:
        case 200 | 302:
            subscription = Subscription(**response.json())
            log.debug(f"Existing subscription found: {subscription}")
            return subscription
        case 201:
            subscription = Subscription(**response.json())
            log.debug(f"Subscription created: {subscription}")
            return subscription
        case 300:
            options = [FeedOption(**feed) for feed in response.json()]
            log.debug(f"{len(options)} feed options found:", options)
            raise MultipleChoicesError(options)
        case 404:
            raise NotFoundError(f"No feed found at '{url}'")
        case _:
            raise UnexpectedError("Unexpected error while creating subscription")


def delete_subscription(subscription_id: int) -> None:
    """
    Delete a subscription.

    Docs:
     - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#delete-subscription

    TODO: add possible responses
    """
    request_args = RequestArgs(url=f"{API}/subscriptions/{subscription_id}.json")

    log.debug(f"Deleting subscription {subscription_id}")
    response = make_request(HTTPMethod.DELETE, request_args)

    match response.status_code:
        case 204:
            log.debug(f"Subscription {subscription_id} deleted")
        case 403:
            raise ForbiddenError(f"You are not subscribed to subscription {subscription_id} so you cannot delete it")
        case _:
            raise UnexpectedError("Unexpected error while deleting subscription")
