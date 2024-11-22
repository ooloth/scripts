"""Entry point for listing all entries in an RSS feed subscription."""

import sys

from common.logs import log
from rss.entries.list.feedbin import FeedId, get_feed_entries


def main(feed_id: FeedId) -> None:
    log.debug(f"💪 Getting all entries for feed {feed_id.id}")

    result, data = get_feed_entries(feed_id)
    log.debug(f"{result.value}: {data}")

    log.debug("👍 Done getting feed entries")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss/entries/list/main.py <feed_id>")
        sys.exit(1)

    unvalidated_feed_id = int(sys.argv[1])

    log.debug(f"👀 Validating feed ID {unvalidated_feed_id}")
    validated_id = FeedId(id=unvalidated_feed_id)

    main(validated_id)
