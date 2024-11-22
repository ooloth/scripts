"""Entry point for adding an RSS feed subscription."""

import sys

from common.logs import log
from rss.subscriptions.add.feedbin import create_subscription
from rss.subscriptions.entities import FeedUrl


def main(url: FeedUrl) -> None:
    log.debug(f"💪 Creating subscription for '{url}'")

    result, data = create_subscription(url)
    log.debug(f"{result.value}: {data}")

    log.debug("👍 Done adding subscription")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss/subscriptions/add/main.py <url>")
        sys.exit(1)

    unvalidated_url = sys.argv[1]

    log.debug(f"👀 Validating URL '{unvalidated_url}'")
    validated_url = FeedUrl(unvalidated_url)

    main(validated_url)
