from dataclasses import dataclass

from pydantic import BaseModel

EntryId = int
FeedId = int
FeedUrl = str
SubscriptionId = int
SubscriptionTitle = str
Url = str


class Entry(BaseModel):
    id: EntryId


class FeedOption(BaseModel):
    feed_url: FeedUrl
    title: str


@dataclass
class SubscriptionTitleWithSuffix:
    title: str

    def __post_init__(self) -> None:
        self.validate_title(self.title)

    @staticmethod
    def validate_title(value: str) -> None:
        if not value.endswith(" 📖") and not value.endswith(" 📺"):
            raise ValueError("Title must end with either ' 📖' or ' 📺'")


class Subscription(BaseModel):
    feed_id: FeedId
    feed_url: Url
    id: SubscriptionId
    site_url: Url
    title: SubscriptionTitle
