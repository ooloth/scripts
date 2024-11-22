from pydantic import BaseModel, field_validator


class FeedId(BaseModel):
    id: int


class FeedUrl(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def is_domain_or_url(cls, url: str) -> str:
        # TODO: add validation?
        return url


class FeedOption(BaseModel):
    feed_url: str
    title: str


class SubscriptionId(BaseModel):
    id: int


class SubscriptionTitle(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def ends_with_emoji(cls, title: str) -> str:
        if not title.endswith(" 📖") and not title.endswith(" 📺"):
            raise ValueError("Title must end with either ' 📖' or ' 📺'")
        return title


class Subscription(BaseModel):
    title: str
    site_url: str
    feed_url: str
    feed_id: int
    id: int
