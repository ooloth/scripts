"""
The domain entities for the Feedbin application.
"""

from pydantic import BaseModel


class Entry(BaseModel):
    title: str
    author: str
    url: str
    feed_id: int
    id: int


class Subscription(BaseModel):
    title: str
    site_url: str
    feed_url: str
    feed_id: int
    id: int
