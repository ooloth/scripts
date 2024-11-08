from feedbin.api import NotFoundError, UnexpectedError
from feedbin.api.subscriptions import Subscription, get_subscriptions
from utils.logs import log


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


def main() -> list[Subscription]:
    return list_subscriptions()
