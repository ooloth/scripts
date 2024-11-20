"""Entry point for deleting an RSS feed subscription."""

import sys

from common.logs import log
from rss.subscriptions.delete.feedbin import SubscriptionId, delete_subscription


def main(unvalidated_subscription_id: int) -> None:
    log.debug(f"👀 Validating subscription ID '{unvalidated_subscription_id}'")
    validated_id = SubscriptionId(id=unvalidated_subscription_id)

    log.debug(f"💪 Deleting subscription ID '{validated_id.id}'")
    result, data = delete_subscription(validated_id)

    log.debug(f"{result.value}: {data}")
    log.debug("👍 Done deleting subscription")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss12/domain/add_subscription.py <url>")
        sys.exit(1)

    subscription_id = int(sys.argv[1])
    main(subscription_id)
