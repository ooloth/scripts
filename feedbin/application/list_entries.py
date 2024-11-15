"""
The core application logic for listing all entries of a Feedbin feed.
"""

from common.logs import log
from feedbin.adapters.api import ForbiddenError, NotFoundError, UnexpectedError
from feedbin.adapters.api.entries import get_feed_entries
from feedbin.domain.entities import Entry


# NOTE: not currently called
def list_feed_entries(feed_id: int) -> list[Entry]:
    log.debug(f"🔍 Getting feed entries for feed {feed_id}")

    try:
        entries = get_feed_entries(feed_id)
        log.info(f"{len(entries)} entries found")
        return entries
    except ForbiddenError as e:
        log.error(e)
        return []
    except NotFoundError as e:
        log.error(e)
        return []
    except UnexpectedError as e:
        log.error(e)
        return []
