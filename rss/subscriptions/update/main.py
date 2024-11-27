"""Entry point for updating an existing RSS feed subscription."""

import sys

from common.logs import log
from rss.domain import Subscription, SubscriptionId, SubscriptionTitle, SubscriptionTitleWithSuffix, Url
from rss.subscriptions.get.feedbin import get_subscription
from rss.subscriptions.update.feedbin import update_subscription


def choose_suffix(url: Url) -> str:
    """Returns 📺 for YouTube URLs; otherwise, 📖."""
    if "youtube.com" in url or "youtu.be" in url:
        return "📺"
    return "📖"


def append_suffix(title: SubscriptionTitle, url: Url) -> SubscriptionTitleWithSuffix:
    """Appends the appropriate suffix to the title based on the URL if the suffix isn't already there."""
    if title.endswith(" 📖") or title.endswith(" 📺"):
        return SubscriptionTitleWithSuffix(title=title)

    return SubscriptionTitleWithSuffix(title=f"{title} {choose_suffix(url)}")


def generate_new_title(subscription_id: SubscriptionId) -> SubscriptionTitleWithSuffix | None:
    """Look up the subscription and generate a new title with the appropriate suffix."""
    log.debug("🔍 Getting subscription details")
    get_result, subscription = get_subscription(subscription_id)
    log.debug(f"{get_result.value}: {subscription}")

    if not isinstance(subscription, Subscription):
        log.error(f"Expected Subscription, got {type(subscription)}")
        return None

    log.debug("✍️ Getting updated title")
    return append_suffix(subscription.title, subscription.site_url)


def main(subscription_id: SubscriptionId, new_title: SubscriptionTitleWithSuffix | None = None) -> None:
    if new_title is None:
        log.debug("✍️ Generating new title")
        new_title = generate_new_title(subscription_id)

    if new_title is None:
        log.error("Failed to generate new title")
        return

    log.debug(f"💪 Updating subscription {subscription_id} title to '{new_title.title}'")
    update_result, updated_subscription = update_subscription(subscription_id, new_title)
    log.debug(f"{update_result.value}: {updated_subscription}")

    log.debug("👍 Done updating subscription")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss/subscriptions/update/main.py <subscription_id> <optional-new-title>")
        sys.exit(1)

    subscription_id = SubscriptionId(sys.argv[1])
    optional_new_title = SubscriptionTitleWithSuffix(title=sys.argv[2]) if len(sys.argv) > 2 else None

    main(subscription_id, optional_new_title)
