from utils.logs import log


def mark_unread(entry_ids: list[int]) -> None:
    """Mark entries as unread."""
    if not entry_ids:
        log.info("No entries to mark as unread")
        return

    log.info(f"Marking {len(entry_ids)} entries as unread")


def main(entry_ids: list[int]) -> None:
    mark_unread(entry_ids)
