"""
The entities returned by the Feedbin API.
"""

from pydantic import BaseModel


class Entry(BaseModel):
    title: str
    author: str
    url: str
    feed_id: int
    id: int
