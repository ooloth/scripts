"""
The entities returned by the Feedbin API.
"""

from pydantic import BaseModel


class EntryId(BaseModel):
    __root__: int

    def __init__(self, x: int) -> None:
        super().__init__(__root__=x)


class Entry(BaseModel):
    title: str
    author: str
    url: str
    feed_id: int
    id: int
