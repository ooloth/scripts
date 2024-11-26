"""Entry point for adding an RSS feed subscription."""

import sys

from common.logs import log
from rss.entities import FeedUrl
from rss.subscriptions.add.feedbin import CreateSubscriptionOutput, create_subscription


def main(url: FeedUrl) -> CreateSubscriptionOutput:
    log.debug(f"💪 Creating subscription for '{url}'")

    result = create_subscription(url)

    outcome, data = result
    log.debug(f"{outcome.value}: {data}")

    log.debug("👍 Done adding subscription")

    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss/subscriptions/add/main.py <url>")
        sys.exit(1)

    main(FeedUrl(sys.argv[1]))
