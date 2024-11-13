"""
The core application logic for marking entries as unread.
"""

from common.logs import log
from feedbin.adapters.api import UnexpectedError
from feedbin.adapters.api.unread_entries import create_unread_entries


def mark_entries_unread(entry_ids: list[int]) -> None:
    """Mark entries as unread."""
    if not entry_ids:
        log.info("No entries to mark as unread")
        return

    try:
        log.info(f"Marking {len(entry_ids)} entries as unread")
        create_unread_entries(entry_ids)
    except UnexpectedError as e:
        log.error(f"Error marking entries as unread: {e}")
        raise
