"""Entry point for deleting an RSS feed subscription."""

# TODO: support deleting based on a URL as well as an ID
# > If an int, validate as an ID, then delete that subscription
# > If a string, validate as a URL, then get list of all subscriptions, then find a match by site_url or feed_url and delete that subscription

import sys

from common.logs import log
from rss.entities import SubscriptionId
from rss.subscriptions.delete.feedbin import delete_subscription


def main(subscription_id: SubscriptionId) -> None:
    log.debug(f"💪 Deleting subscription ID {subscription_id.id}")

    result, data = delete_subscription(subscription_id)
    log.debug(f"{result.value}: {data}")

    log.debug("👍 Done deleting subscription")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss/subscriptions/delete/main.py <subscription_id>")
        sys.exit(1)

    unvalidated_subscription_id = int(sys.argv[1])

    log.debug(f"👀 Validating subscription ID {unvalidated_subscription_id}")
    validated_subscription_id = SubscriptionId(id=unvalidated_subscription_id)

    main(validated_subscription_id)
