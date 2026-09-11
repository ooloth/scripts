from dataclasses import dataclass
from typing import NewType

from pydantic import BaseModel

# NewType rather than a plain alias: `EntryId = int` names the concept but lets any
# int through, so `get_feed_entries(entry_id)` type-checks. NewType makes the name
# carry the distinction the domain rules ask for.
EntryId = NewType("EntryId", int)
FeedId = NewType("FeedId", int)
FeedTitle = NewType("FeedTitle", str)
FeedUrl = NewType("FeedUrl", str)
SubscriptionId = NewType("SubscriptionId", int)
SubscriptionTitle = NewType("SubscriptionTitle", str)
Url = NewType("Url", str)


class Entry(BaseModel):
    id: EntryId


class FeedOption(BaseModel):
    feed_url: FeedUrl
    title: FeedTitle


@dataclass
class SubscriptionTitleWithSuffix:
    title: SubscriptionTitle

    def __post_init__(self) -> None:
        self.validate_title(self.title)

    @staticmethod
    def validate_title(value: str) -> None:
        if not value.endswith((" 📖", " 📺")):
            raise ValueError("Title must end with either ' 📖' or ' 📺'")


class Subscription(BaseModel):
    feed_id: FeedId
    feed_url: Url
    id: SubscriptionId
    site_url: Url
    title: SubscriptionTitle
