from pydantic import BaseModel, field_validator


class FeedId(BaseModel):
    __root__: int

    def __init__(self, x: int) -> None:
        super().__init__(__root__=x)


class FeedUrl(BaseModel):
    __root__: str

    def __init__(self, x: str) -> None:
        super().__init__(__root__=x)

    @field_validator("url")
    @classmethod
    def is_domain_or_url(cls, url: str) -> str:
        # TODO: add validation?
        return url


class FeedOption(BaseModel):
    feed_url: str
    title: str


class SubscriptionId(BaseModel):
    __root__: int

    def __init__(self, x: int) -> None:
        super().__init__(__root__=x)


class SubscriptionTitleWithSuffix(BaseModel):
    __root__: str

    def __init__(self, x: str) -> None:
        super().__init__(__root__=x)

    @field_validator("__root__")
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
