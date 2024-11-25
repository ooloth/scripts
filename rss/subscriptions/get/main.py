"""
Entry point for updating an existing RSS feed subscription.

TODO:
 - Update tag
"""

import sys

from common.logs import log
from rss.entities import SubscriptionId
from rss.subscriptions.get.feedbin import get_subscription


# def get_suffix(Subscription: str) -> str:
# def get_suffix(feed_url: str) -> str:
def get_suffix(site_url: str) -> str:
    """Returns 📺 for YouTube URLs; otherwise, returns 📖."""
    if "youtube.com" in site_url or "youtu.be" in site_url:
        return "📺"
    return "📖"


def get_title_with_suffix(title: str, site_url: str) -> str:
    suffix = get_suffix(site_url)
    return f"{title} {suffix}"


def main(subscription_id: SubscriptionId) -> None:
    log.debug(f"💪 Getting subscription {subscription_id.id}")

    result, data = get_subscription(subscription_id)
    log.debug(f"{result.value}: {data}")

    log.debug("👍 Done getting subscription")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss/subscriptions/get/main.py <subscription_id>")
        sys.exit(1)

    unvalidated_subscription_id = int(sys.argv[1])

    log.debug(f"👀 Validating subscription ID {unvalidated_subscription_id}")
    validated_id = SubscriptionId(id=unvalidated_subscription_id)

    main(validated_id)
