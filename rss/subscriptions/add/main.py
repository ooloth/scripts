"""Entry point for adding an RSS feed subscription."""

import sys

from common.logs import log
from rss.subscriptions.add.feedbin import FeedUrl, create_subscription


def main(url: FeedUrl) -> None:
    log.debug(f"💪 Creating subscription for '{url.url}'")
    result, data = create_subscription(url)

    log.debug(f"{result.value}: {data}")
    log.debug("👍 Done adding subscription")


if __name__ == "__main__":
    # TODO: pivat to using feeds/search? can I send both URLs and search terms there?
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss12/subscriptions/add/main.py <url>")
        sys.exit(1)

    unvalidated_url = sys.argv[1]

    log.debug(f"👀 Validating URL '{unvalidated_url}'")
    validated_url = FeedUrl(url=unvalidated_url)

    main(validated_url)
