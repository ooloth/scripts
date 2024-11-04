import json

import requests
import typer
from pydantic import BaseModel

from feedbin.client import get_auth
from utils.logs import log

# Docs:
# - https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md
# - https://typer.tiangolo.com/tutorial/subcommands/add-typer

app = typer.Typer()

API = "https://api.feedbin.com/v2"


class Subscription(BaseModel):
    title: str
    site_url: str
    feed_url: str
    feed_id: int
    id: int


# @app.command(name="list")
def ls() -> list[Subscription]:
    """Fetch subscriptions and parse the relevant response properties using Pydantic."""
    response = requests.get(f"{API}/subscriptions.json", auth=get_auth())
    response.raise_for_status()

    return [Subscription(**subscription) for subscription in response.json()]


def _find_matching_subscription(url: str, subscriptions: list[Subscription]):
    url_without_trailing_slash = url.rstrip("/")
    log("🔍 url_without_trailing_slash =", url_without_trailing_slash)
    for sub in subscriptions:
        if sub.site_url.strip("/") == url_without_trailing_slash:
            return sub
    return None


def _validate_url(url: str | None) -> str | None:
    if not url:
        log("🚨 No URL provided.")
        return None

    if not url.startswith("http"):
        return f"https://{url}"

    return url


def choose_between_multiple_feeds(feeds: list[dict]):
    """Prompt the user to choose between multiple feeds."""
    print("Multiple feeds found. Please choose one:")
    for idx, feed in enumerate(feeds, start=1):
        print(f"{idx}. {feed['title']} ({feed['feed_url']})")

    choice = typer.prompt("Which feed number would you like to subscribe to?", type=int)
    if 1 <= choice <= len(feeds):
        selected_feed = feeds[choice - 1]
        typer.echo(f"🔖 Selected feed URL: {selected_feed['feed_url']}")
    else:
        typer.echo("🚨 Invalid choice")


@app.command()
def add(url: str) -> Subscription | None:
    """
    See: # See: https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#create-subscription
    """
    # url = _validate_url(url)
    # if not url:
    # return

    subscriptions = ls()
    log("subscriptions:", subscriptions)

    matching_subscription = _find_matching_subscription(url, subscriptions)
    log("matching_subscription:", matching_subscription)

    # if matching_subscription:
    #     print("Matching subscription found:", matching_subscription)
    # else:
    #     print("No matching subscription found.")

    """Create a subscription and handle the response."""
    response = requests.post(
        f"{API}/subscriptions.json",
        auth=get_auth(),
        headers={"Content-Type": "application/json; charset=utf-8"},
        data=json.dumps({"feed_url": url}),
    )

    if response.status_code == 201:
        print(f"✅ Successfully subscribed to '{url}'")
        return Subscription(**response.json())
    elif response.status_code == 302:
        print(f"✅ Already subscribed to '{url}'")
        return Subscription(**response.json())
    elif response.status_code == 404:
        print(f"❌ No feed found at '{url}'")
    elif response.status_code == 300:
        print(f"❌ Multiple feeds found at '{url}'")
        choose_between_multiple_feeds(response.json())
    else:
        print(f"❌ Unexpected HTTP status code: {response.status_code}")
        print(response.text)
    return None


if __name__ == "__main__":
    app()
