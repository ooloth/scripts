"""
Entry point for updating an existing RSS feed subscription.

TODO:
 - Update tag
"""

import sys

from common.logs import log
from rss.entities import SubscriptionId
from rss.subscriptions.get.feedbin import get_subscription


def main(subscription_id: SubscriptionId) -> None:
    log.debug(f"💪 Getting subscription {subscription_id}")

    result, data = get_subscription(subscription_id)
    log.debug(f"{result.value}: {data}")

    log.debug("👍 Done getting subscription")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss/subscriptions/get/main.py <subscription_id>")
        sys.exit(1)

    main(SubscriptionId(sys.argv[1]))
