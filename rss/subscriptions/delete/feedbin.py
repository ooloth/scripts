"""Feedbin API interactions for deleting an RSS feed subscription."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel
from requests import HTTPError

from rss.utils.feedbin import (
    API,
    HTTPMethod,
    RequestArgs,
    UnexpectedError,
    make_request,
)


class SubscriptionId(BaseModel):
    id: int


class DeleteSubscriptionResult(Enum):
    NO_CONTENT = "✅ Subscription deleted"
    FORBIDDEN = "⛔️ You do not own this subscription"
    NOT_FOUND = "⛔️ No subscription found with that ID"
    UNEXPECTED_STATUS_CODE = "🚨 Unexpected status code while deleting subscription"
    HTTP_ERROR = "🚨 HTTP error while deleting subscription"
    UNEXPECTED_ERROR = "🚨 Unexpected error while deleting subscription"


DeleteSubscriptionOutput = (
    tuple[Literal[DeleteSubscriptionResult.NO_CONTENT], None]
    | tuple[Literal[DeleteSubscriptionResult.FORBIDDEN], int]
    | tuple[Literal[DeleteSubscriptionResult.NOT_FOUND], None]
    | tuple[Literal[DeleteSubscriptionResult.UNEXPECTED_STATUS_CODE], int]
    | tuple[Literal[DeleteSubscriptionResult.HTTP_ERROR], str]
    | tuple[Literal[DeleteSubscriptionResult.UNEXPECTED_ERROR], str]
)


def delete_subscription(subscription_id: SubscriptionId) -> DeleteSubscriptionOutput:
    """
    Delete a subscription.

    Docs:
     - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#delete-subscription
    """
    try:
        request_args = RequestArgs(url=f"{API}/subscriptions/{subscription_id.id}.json")
        response = make_request(HTTPMethod.DELETE, request_args)

        match response.status_code:
            case 204:
                return DeleteSubscriptionResult.NO_CONTENT, None
            case 403:
                return DeleteSubscriptionResult.FORBIDDEN, subscription_id.id
            case 404:
                return DeleteSubscriptionResult.NOT_FOUND, None
            case _:
                raise UnexpectedError("Unexpected error while deleting subscription")
    except HTTPError as e:
        return DeleteSubscriptionResult.HTTP_ERROR, str(e)
    except Exception as e:
        return DeleteSubscriptionResult.UNEXPECTED_ERROR, str(e)
