"""
The core application logic for adding a new feed subscription to Feedbin.

TODO: move all "typer" usage to feedbin.adapters.cli
"""

import typer

from common.logs import log
from feedbin.adapters.api import NotFoundError, UnexpectedError
from feedbin.adapters.api.subscriptions import MultipleChoicesError, Subscription, create_subscription

app = typer.Typer(no_args_is_help=True)


# def _find_matching_subscription(url: str, subscriptions: list[Subscription]):
#     url_without_trailing_slash = url.rstrip("/")
#     for sub in subscriptions:
#         if sub.site_url.strip("/") == url_without_trailing_slash:
#             return sub
#     return None


def add_subscription(url: str) -> Subscription:
    log.info(f"🔖 Subscribing to feed at '{url}'")

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
