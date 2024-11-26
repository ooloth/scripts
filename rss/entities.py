from pydantic import BaseModel, field_validator

EntryId = int
FeedId = int
FeedUrl = str
SubscriptionId = int


class Entry(BaseModel):
    id: EntryId


class FeedOption(BaseModel):
    feed_url: str
    title: str


class SubscriptionTitleWithSuffix(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def ends_with_emoji(cls, value: str) -> str:
        if not value.endswith(" 📖") and not value.endswith(" 📺"):
            raise ValueError("Title must end with either ' 📖' or ' 📺'")
        return value


class Subscription(BaseModel):
    title: str
    site_url: str
    feed_url: str
    feed_id: int
    id: int
