"""Feedbin API interactions for adding an RSS feed subscription."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, field_validator
from requests import HTTPError

from rss.subscriptions.entities import Subscription
from rss.utils.feedbin import API, HTTPMethod, RequestArgs, make_request


class FeedUrl(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def is_domain_or_url(cls, url: str) -> str:
        # TODO: add validation?
        return url


class FeedOption(BaseModel):
    feed_url: str
    title: str


class CreateSubscriptionResult(Enum):
    CREATED = "✅ Subscription created"
    EXISTS = "✅ Subscription already exists"
    MULTIPLE_CHOICES = "🥞 Multiple RSS feeds found"
    NOT_FOUND = "⛔️ No RSS feed found at that URL"
    UNEXPECTED_STATUS_CODE = "🚨 Unexpected status code while creating subscription"
    HTTP_ERROR = "🚨 HTTP error while creating subscription"
    UNEXPECTED_ERROR = "🚨 Unexpected error while creating subscription"


CreateSubscriptionOutput = (
    tuple[Literal[CreateSubscriptionResult.CREATED], Subscription]
    | tuple[Literal[CreateSubscriptionResult.EXISTS], Subscription]
    | tuple[Literal[CreateSubscriptionResult.MULTIPLE_CHOICES], list[FeedOption]]
    | tuple[Literal[CreateSubscriptionResult.NOT_FOUND], int]
    | tuple[Literal[CreateSubscriptionResult.UNEXPECTED_STATUS_CODE], int]
    | tuple[Literal[CreateSubscriptionResult.HTTP_ERROR], str]
    | tuple[Literal[CreateSubscriptionResult.UNEXPECTED_ERROR], str]
)


def create_subscription(url: FeedUrl) -> CreateSubscriptionOutput:
    """
    Create a subscription from a website or feed URL (with or without the scheme).

    Docs:
     - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#create-subscription
    """
    try:
        request_args = RequestArgs(url=f"{API}/subscriptions.json", json={"feed_url": url.url})
        response = make_request(HTTPMethod.POST, request_args)

        match response.status_code:
            case 200 | 302:
                return CreateSubscriptionResult.EXISTS, Subscription(**response.json())
            case 201:
                return CreateSubscriptionResult.CREATED, Subscription(**response.json())
            case 300:
                options = [FeedOption(**feed) for feed in response.json()]
                return CreateSubscriptionResult.MULTIPLE_CHOICES, options
            case _:
                return CreateSubscriptionResult.UNEXPECTED_STATUS_CODE, response.status_code
    except HTTPError as e:
        if e.response.status_code == 404:
            return CreateSubscriptionResult.NOT_FOUND, e.response.status_code
        return CreateSubscriptionResult.HTTP_ERROR, str(e)
    except Exception as e:
        return CreateSubscriptionResult.UNEXPECTED_ERROR, str(e)
