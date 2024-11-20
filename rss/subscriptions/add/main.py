"""Entry point for adding an RSS feed subscription."""

import sys

from common.logs import log
from rss.subscriptions.add.feedbin import FeedUrl, create_subscription


def main(unvalidated_url: str) -> None:
    log.debug(f"👀 Validating URL '{unvalidated_url}'")
    validated_url = FeedUrl(url=unvalidated_url)

    log.debug(f"💪 Creating subscription for '{validated_url.url}'")
    result, data = create_subscription(validated_url)

    log.debug(f"{result.value}: {data}")
    log.debug("👍 Done adding subscription")


if __name__ == "__main__":
    # search_term = sys.argv[1] - use feeds/search?
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss12/subscriptions/add/main.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    main(url)
