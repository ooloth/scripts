"""Entry point for marking RSS feed entries as unread."""

import sys

from common.logs import log
from rss.entries.mark_unread.feedbin import EntryId, UnreadEntriesResponse, create_unread_entries


def main(entry_ids: list[EntryId]) -> None:
    log.debug(f"💪 Marking {len(entry_ids)} as unread")

    result, data = create_unread_entries(entry_ids)
    log.debug(f"{result.value}: {data}")

    if isinstance(data, UnreadEntriesResponse):
        log.debug(f"✅ Marked {len(data.marked_as_unread)} entries as unread")
        if len(data.not_marked_as_unread) > 0:
            log.debug(f"🚫 Failed to mark {len(data.not_marked_as_unread)} entries as unread")

    log.debug("👍 Done marking entries as unread")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss12/subscriptions/add/main.py <url>")
        sys.exit(1)

    log.debug("🔪 Parsing entry IDs")
    parsed_entry_ids = sys.argv[1].split(",")  # or split on space?

    log.debug("🔢 Converting entry IDs to integers")
    unvalidated_entry_ids = [int(id) for id in parsed_entry_ids]

    log.debug("👀 Validating entry IDs")
    validated_entry_ids = [EntryId(id=int(id)) for id in sys.argv[1].split(",")]

    main(validated_entry_ids)