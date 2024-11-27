"""
Common functionality used by the Feedbin API endpoint adapters.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

import requests

from common.secrets import get_secret

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


class HTTPMethod(str, Enum):
    GET = "GET"
    PATCH = "PATCH"
    POST = "POST"
    DELETE = "DELETE"


@dataclass
class RequestArgs:
    url: str
    params: dict[str, Any] | None = None
    json: dict[str, Any] | None = None


def make_request(method: HTTPMethod, args: RequestArgs) -> requests.Response:
    """
    Make an HTTP request to the Feedbin API.

    Since the possible status codes (and their explanations) vary by endpoint, we raise them at this base level
    and catch them one level up in the endpoint-specific API helper functions.

    TODO:
     - Expect different request args for GET vs POST methods?
    """
    headers = {}

    if method in (HTTPMethod.PATCH, HTTPMethod.POST):
        headers["Content-Type"] = "application/json; charset=utf-8"

    response = requests.request(
        method.value,
        args.url,
        json=args.json,
        params=args.params,
        headers=headers,
        auth=_get_auth(),
    )
    response.raise_for_status()

    return response


def parse_link_header(link_header: str) -> dict[str, str]:
    """
    Parse the "links" header to extract URLs for pagination.

    Example:
     - '<https://api.feedbin.com/v2/feeds/1079883/entries.json?page=2>'

    Docs:
     - https://github.com/feedbin/feedbin-api?tab=readme-ov-file#pagination
    """
    links = {}
    for link in link_header.split(","):
        parts = link.split(";")
        url = parts[0].strip()[1:-1]
        rel = parts[1].strip().split("=")[1].strip('"')
        links[rel] = url
    return links


def make_paginated_request(request_args: RequestArgs) -> list[dict[str, Any]]:
    """
    Fetch all pages of results for a paginated request.

    Docs:
     - https://github.com/feedbin/feedbin-api?tab=readme-ov-file#pagination
    """
    all_results = []
    while request_args.url:
        response = make_request(HTTPMethod.GET, request_args)
        all_results.extend(response.json())
        link_header = response.headers.get("links")
        if link_header:
            links = parse_link_header(link_header)
            request_args.url = links.get("next", "")
        else:
            request_args.url = ""

    return all_results
