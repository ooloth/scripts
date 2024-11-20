"""Entry point for deleting an RSS feed subscription."""

import sys

from common.logs import log
from rss.subscriptions.delete.feedbin import SubscriptionId, delete_subscription


def main(subscription_id: SubscriptionId) -> None:
    log.debug(f"💪 Deleting subscription ID {subscription_id.id}")
    result, data = delete_subscription(subscription_id)

    log.debug(f"{result.value}: {data}")
    log.debug("👍 Done deleting subscription")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss12/domain/add_subscription.py <url>")
        sys.exit(1)

    unvalidated_subscription_id = int(sys.argv[1])

    log.debug(f"👀 Validating subscription ID {unvalidated_subscription_id}")
    validated_subscription_id = SubscriptionId(id=unvalidated_subscription_id)

    main(validated_subscription_id)
