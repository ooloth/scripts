"""Entry point for marking RSS feed entries as unread."""

import sys

from common.logs import log
from rss.domain import EntryId
from rss.entries.mark_unread.feedbin import UnreadEntriesResponse, create_unread_entries


def main(entry_ids: list[EntryId]) -> None:
    log.debug(f"💪 Marking {len(entry_ids)} entries as unread")

    result, data = create_unread_entries(entry_ids)
    log.debug(f"{result.value}: {data}")

    if isinstance(data, UnreadEntriesResponse):
        log.debug(f"✅ Marked {len(data.marked_as_unread)} entries as unread")
        if len(data.not_marked_as_unread) > 0:
            log.debug(f"🚫 Failed to mark {len(data.not_marked_as_unread)} entries as unread")

    log.debug("👍 Done marking entries as unread")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: PYTHONPATH=. uv run rss/entries/mark_unread/main.py <entry-id,entry-id>")
        sys.exit(1)

    log.debug("🔪 Parsing entry IDs")
    entry_ids = [EntryId(id) for id in sys.argv[1].split(",")]

    main(entry_ids)
