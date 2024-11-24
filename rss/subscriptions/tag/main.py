"""Entry point for tagging a feed."""

import sys

from common.logs import log
from rss.entities import FeedId, FeedTag
from rss.subscriptions.tag.feedbin import create_tagging


def main(feed_id: FeedId, tag: FeedTag) -> None:
    log.debug(f"💪 Tagging feed {feed_id.id} with '{tag.tag}'")

    result, data = create_tagging(feed_id, tag)
    log.debug(f"{result.value}: {data}")

    log.debug("👍 Done tagging feed")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: PYTHONPATH=. uv run rss/subscriptions/tag/main.py <feed_id> <tag>")
        sys.exit(1)

    unvalidated_feed_id = int(sys.argv[1])
    unvalidated_tag = sys.argv[2]

    log.debug(f"👀 Validating feed ID {unvalidated_feed_id}")
    validated_id = FeedId(id=unvalidated_feed_id)

    log.debug(f"👀 Validating tag '{unvalidated_tag}'")
    validated_tag = FeedTag(tag=unvalidated_tag)

    main(validated_id, validated_tag)
