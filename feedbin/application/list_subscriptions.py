"""
The core application logic for listing all Feedbin subscriptions.
"""

from common.logs import log
from feedbin.adapters.api import NotFoundError, UnexpectedError
from feedbin.adapters.api.subscriptions import Subscription, get_subscriptions


def list_subscriptions() -> list[Subscription]:
    try:
        subscriptions = get_subscriptions()
        log.info(f"{len(subscriptions)} Feedbin subscriptions found")
        return subscriptions
    except NotFoundError as e:
        log.error(e)
        return []
    except UnexpectedError as e:
        log.error(e)
        return []
