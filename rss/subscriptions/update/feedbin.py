"""Feedbin API interactions for updating an existing RSS feed subscription."""

from enum import Enum
from typing import Literal

from requests import HTTPError

from rss.subscriptions.entities import Subscription, SubscriptionId, SubscriptionTitleWithSuffix
from rss.utils.feedbin import API, HTTPMethod, RequestArgs, make_request


class UpdateSubscriptionResult(Enum):
    OK = "✅ Subscription title updated"
    FORBIDDEN = "⛔️ You do not own this Feedbin subscription"
    NOT_FOUND = "⛔️ No Feedbin subscription found with that ID"
    UNEXPECTED_STATUS_CODE = "🚨 Unexpected status code while updating subscription"
    HTTP_ERROR = "🚨 HTTP error while updating subscription"
    UNEXPECTED_ERROR = "🚨 Unexpected error while updating subscription"


GetFeedEntriesOutput = (
    tuple[Literal[UpdateSubscriptionResult.OK], Subscription]
    | tuple[Literal[UpdateSubscriptionResult.FORBIDDEN], SubscriptionId]
    | tuple[Literal[UpdateSubscriptionResult.NOT_FOUND], SubscriptionId]
    | tuple[Literal[UpdateSubscriptionResult.UNEXPECTED_STATUS_CODE], int]
    | tuple[Literal[UpdateSubscriptionResult.HTTP_ERROR], str]
    | tuple[Literal[UpdateSubscriptionResult.UNEXPECTED_ERROR], str]
)


def update_subscription(
    subscription_id: SubscriptionId,
    new_title: SubscriptionTitleWithSuffix,
) -> GetFeedEntriesOutput:
    """
    Update an existing RSS feed subscription with the provided title (which must end with an emoji).

    Docs:
    - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#update-subscription
    """
    request_args = RequestArgs(
        url=f"{API}/subscriptions/{subscription_id}.json",
        json={"title": new_title},
    )

    try:
        response = make_request(HTTPMethod.PATCH, request_args)

        match response.status_code:
            case 200:
                return UpdateSubscriptionResult.OK, Subscription(**response.json())
            case _:
                return UpdateSubscriptionResult.UNEXPECTED_STATUS_CODE, response.status_code
    except HTTPError as e:
        match e.response.status_code:
            case 403:
                return UpdateSubscriptionResult.FORBIDDEN, subscription_id
            case 404:
                return UpdateSubscriptionResult.NOT_FOUND, subscription_id
        return UpdateSubscriptionResult.HTTP_ERROR, str(e)
