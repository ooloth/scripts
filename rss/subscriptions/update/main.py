"""
Entry point for updating an existing RSS feed subscription.

TODO:
 - Update tag
"""

import sys

from common.logs import log
from rss.entities import SubscriptionId, SubscriptionTitleWithSuffix
from rss.subscriptions.update.feedbin import update_subscription


def main(subscription_id: SubscriptionId, new_title: SubscriptionTitleWithSuffix) -> None:
    log.debug(f"💪 Updating subscription {subscription_id.id} title to '{new_title.title}'")

    result, data = update_subscription(subscription_id, new_title)
    log.debug(f"{result.value}: {data}")

    log.debug("👍 Done updating subscription")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: PYTHONPATH=. uv run rss/subscriptions/update/main.py <subscription_id> <new_title>")
        sys.exit(1)

    unvalidated_subscription_id = int(sys.argv[1])
    unvalidated_new_title = sys.argv[2]

    log.debug(f"👀 Validating subscription ID {unvalidated_subscription_id}")
    validated_id = SubscriptionId(id=unvalidated_subscription_id)

    log.debug(f"👀 Validating title '{unvalidated_new_title}'")
    validated_title = SubscriptionTitleWithSuffix(title=unvalidated_new_title)

    main(validated_id, validated_title)
