"""
Core functionality for interacting with all Feedbin API endpoints.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

import requests

from op.secrets import get_secret

API = "https://api.feedbin.com/v2"


_auth = None


def _get_auth() -> tuple[str, str]:
    "Retrieve the username and password for the Feedbin API from 1Password."
    global _auth

    if _auth is None:
        username = get_secret("Feedbin", "username")
        password = get_secret("Feedbin", "password")
        _auth = (username, password)

    return _auth


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


@dataclass
class RequestArgs:
    url: str
    params: dict[str, Any] | None = None
    json: dict[str, Any] | None = None
    headers: dict[str, str] | None = None


def make_request(method: HTTPMethod, args: RequestArgs) -> requests.Response:
    """
    Make an HTTP request to the Feedbin API.

    TODO:
     - expect different request args based on the method?
    """
    return requests.request(
        method.value,
        args.url,
        json=args.json,
        params=args.params,
        headers=args.headers,
        auth=_get_auth(),
    )


class FeedbinError(Exception):
    """Base class for Feedbin API errors."""

    pass


class NotFoundError(FeedbinError):
    """Raised when a resource is not found."""

    pass


class ForbiddenError(FeedbinError):
    """Raised when the caller does not own a resource."""

    pass


class UnexpectedError(FeedbinError):
    "Raised for unexpected errors."

    pass
