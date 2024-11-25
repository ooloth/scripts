"""
Entry point for updating an existing RSS feed subscription.

TODO:
 - Update tag
"""

import sys

from common.logs import log
from rss.entities import Subscription, SubscriptionId, SubscriptionTitleWithSuffix
from rss.subscriptions.get.feedbin import GetSubscriptionOutput, get_subscription
from rss.subscriptions.update.feedbin import UpdateSubscriptionOutput, update_subscription


# def get_suffix(Subscription: str) -> str:
# def get_suffix(feed_url: str) -> str:
def choose_suffix(site_url: str) -> str:
    """Returns 📺 for YouTube URLs; otherwise, returns 📖."""
    if "youtube.com" in site_url or "youtu.be" in site_url:
        return "📺"
    return "📖"


def append_suffix(title: str, site_url: str) -> str:
    suffix = choose_suffix(site_url)
    return f"{title} {suffix}"


def main(subscription_id: SubscriptionId) -> GetSubscriptionOutput | UpdateSubscriptionOutput:
    log.debug("🔍 Getting subscription details")
    get_result = get_subscription(subscription_id)
    get_outcome, subscription = get_result
    log.debug(f"{get_outcome.value}: {subscription}")

    # assert isinstance(subscription, Subscription), f"Expected Subscription, got {type(subscription)}"
    if not isinstance(subscription, Subscription):
        log.error(f"Expected Subscription, got {type(subscription)}")
        return get_result

    log.debug("✍️ Getting updated title")
    new_title = SubscriptionTitleWithSuffix(title=append_suffix(subscription.title, subscription.site_url))

    log.debug(f"💪 Updating subscription {subscription.id} title to '{new_title.title}'")
    update_result = update_subscription(SubscriptionId(id=subscription.id), new_title)
    update_outcome, updated_subscription = update_result
    log.debug(f"{update_outcome.value}: {updated_subscription}")

    log.debug("👍 Done updating subscription")
    return update_result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss/subscriptions/update/main.py <subscription_id>")
        sys.exit(1)

    unvalidated_subscription_id = int(sys.argv[1])

    log.debug(f"👀 Validating subscription ID {unvalidated_subscription_id}")
    validated_id = SubscriptionId(id=unvalidated_subscription_id)

    main(validated_id)
