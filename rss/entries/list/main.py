"""Entry point for listing all entries in an RSS feed subscription."""

import sys

from common.logs import log
from rss.entities import FeedId
from rss.entries.list.feedbin import GetFeedEntriesOutput, get_feed_entries


def main(feed_id: FeedId) -> GetFeedEntriesOutput:
    log.debug(f"💪 Getting all entries for feed {feed_id}")

    result = get_feed_entries(feed_id)

    outcome, data = result
    log.debug(f"{outcome.value}: {data}")

    log.debug("👍 Done getting feed entries")
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss/entries/list/main.py <feed_id>")
        sys.exit(1)

    main(FeedId(sys.argv[1]))
