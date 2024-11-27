"""Entry point for adding an RSS feed subscription."""

import sys

from common.logs import log
from rss.domain import FeedUrl
from rss.subscriptions.add.feedbin import create_subscription


def main(url: FeedUrl) -> None:
    log.debug(f"💪 Creating subscription for '{url}'")

    result, data = create_subscription(url)
    log.debug(f"{result.value}: {data}")

    log.debug("👍 Done adding subscription")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss/subscriptions/add/main.py <url>")
        sys.exit(1)

    main(FeedUrl(sys.argv[1]))  # use pydantic core's Url here for validation?
