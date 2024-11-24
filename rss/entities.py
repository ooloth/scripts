from enum import Enum

from pydantic import BaseModel, field_validator


class EntryId(BaseModel):
    id: int


class Entry(BaseModel):
    title: str
    author: str
    url: str
    feed_id: int
    id: int


class FeedId(BaseModel):
    id: int


# TODO: what if I change these in the UI? Should I just always make a request for the current ones?
# TODO: is there an undocumented GET for /tags.json?
# https://github.com/feedbin/feedbin-api/blob/master/content/tags.md#tags
class Tag(Enum):
    FAVES = "1. Faves"
    CREATING = "2. Creating"
    FITNESS = "3. Fitness"
    FINANCES = "4. Finances"
    FOOD = "5. Food"
    CODING = "6. Coding"
    TOOLS = "7. Tools"
    CAREER = "8. Career"
    INTERVIEWS = "9. Interviews"
    EDUCATIONAL = "10. Educational"
    OPINION = "11. Opinion"


class FeedTag(BaseModel):
    tag: str

    @field_validator("tag")
    @classmethod
    def is_valid_tag(cls, tag: str) -> str:
        if tag not in [t.value for t in Tag]:
            raise ValueError(f"Invalid tag: {tag}")
        return tag


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
