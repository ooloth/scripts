"""
The core application logic for subscribing to a new feed in Feedbin.
"""

from common.logs import log
from feedbin.adapters.api import NotFoundError, UnexpectedError
from feedbin.adapters.api.subscriptions import MultipleChoicesError, Subscription, create_subscription


def add_subscription(url: str) -> Subscription:
    log.debug(f"🔖 Subscribing to feed at '{url}'")

    try:
        return create_subscription(url)
    except MultipleChoicesError as e:
        raise e
    except NotFoundError as e:
        log.warning(e)
        raise e
    except UnexpectedError as e:
        log.error(e)
        raise e
