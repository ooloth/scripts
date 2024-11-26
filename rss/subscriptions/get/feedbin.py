"""Feedbin API interactions for updating an existing RSS feed subscription."""

from enum import Enum
from typing import Literal

from requests import HTTPError

from rss.entities import Subscription, SubscriptionId
from rss.utils.feedbin import API, HTTPMethod, RequestArgs, make_request


class GetSubscriptionResult(Enum):
    OK = "✅ Subscription found"
    FORBIDDEN = "⛔️ You do not own this Feedbin subscription"
    NOT_FOUND = "⛔️ No Feedbin subscription found with that ID"
    UNEXPECTED_STATUS_CODE = "🚨 Unexpected status code while getting subscription"
    HTTP_ERROR = "🚨 HTTP error while getting subscription"
    UNEXPECTED_ERROR = "🚨 Unexpected error while getting subscription"


GetSubscriptionOutput = (
    tuple[Literal[GetSubscriptionResult.OK], Subscription]
    | tuple[Literal[GetSubscriptionResult.FORBIDDEN], SubscriptionId]
    | tuple[Literal[GetSubscriptionResult.NOT_FOUND], SubscriptionId]
    | tuple[Literal[GetSubscriptionResult.UNEXPECTED_STATUS_CODE], int]
    | tuple[Literal[GetSubscriptionResult.HTTP_ERROR], str]
    | tuple[Literal[GetSubscriptionResult.UNEXPECTED_ERROR], str]
)


def get_subscription(subscription_id: SubscriptionId) -> GetSubscriptionOutput:
    """
    Get an existing RSS feed subscription.

    Docs:
    - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#get-subscription
    """
    request_args = RequestArgs(url=f"{API}/subscriptions/{subscription_id}.json")

    try:
        response = make_request(HTTPMethod.GET, request_args)

        match response.status_code:
            case 200:
                return GetSubscriptionResult.OK, Subscription(**response.json())
            case _:
                return GetSubscriptionResult.UNEXPECTED_STATUS_CODE, response.status_code
    except HTTPError as e:
        match e.response.status_code:
            case 403:
                return GetSubscriptionResult.FORBIDDEN, subscription_id
            case 404:
                return GetSubscriptionResult.NOT_FOUND, subscription_id
        return GetSubscriptionResult.HTTP_ERROR, str(e)
