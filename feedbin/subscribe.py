from dataclasses import asdict, dataclass
from typing import Annotated, Literal

import requests
import typer
from pydantic import BaseModel

from feedbin.client import NotFoundError, Subscription, UnexpectedError, _get_auth, get_subscriptions
from utils.logs import log

# Docs:
# - https://typer.tiangolo.com/tutorial/subcommands/add-typer

app = typer.Typer()


def _find_matching_subscription(url: str, subscriptions: list[Subscription]):
    url_without_trailing_slash = url.rstrip("/")
    for sub in subscriptions:
        if sub.site_url.strip("/") == url_without_trailing_slash:
            return sub
    return None


# def _validate_url(url: str) -> str:
#     """Validate the URL provided by the user."""
#     if len(url) == 0:
#         url = typer.prompt("🚨 Please provide a URL")
#         return _validate_url(url)

#     if not url.startswith("http"):
#         url = typer.prompt("🚨 Please provide full URL starting with 'https://' or 'http://")
#         return _validate_url(url)

#     return url


class FeedChoice(BaseModel):
    feed_url: str
    title: str


def choose_between_multiple_feeds(feeds: list[FeedChoice]):
    """Prompt the user to choose between multiple feeds."""
    print("Multiple feeds found. Please choose one:")
    for idx, feed in enumerate(feeds, start=1):
        print(f"{idx}. {feed['title']} ({feed['feed_url']})")

    choice = typer.prompt("Which feed number would you like to subscribe to?", type=int)
    if 1 <= choice <= len(feeds):
        selected_feed = feeds[choice - 1]
        log.info(f"🔖 Selected feed URL: {selected_feed['feed_url']}")
    else:
        log.error("🚨 Invalid choice")


@dataclass
class CreateSubscriptionRequestArgs:
    url: Literal["https://api.feedbin.com/v2/subscriptions.json"]
    json: dict[Literal["feed_url"], str]
    auth: tuple[str, str]
    headers: dict[Literal["Content-Type"], Literal["application/json; charset=utf-8"]]


def create_subscription(url: str, dry_run: bool = False) -> Subscription | None:
    """
    Create a subscription and handle the response.
    See: https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#create-subscription
    """
    request_args = CreateSubscriptionRequestArgs(
        url="https://api.feedbin.com/v2/subscriptions.json",
        json={"feed_url": url},
        auth=_get_auth(),
        headers={"Content-Type": "application/json; charset=utf-8"},
    )

    dry_run = typer.confirm("🌵 Is this a dry run?", default=False)
    if dry_run:
        log.info("🌵 Dry run enabled. Skipping subscribing with this request:", request_args)
        return None

    response = requests.post(**asdict(request_args))
    log.debug("🔍 response =", response.text)
    log.debug("🔍 status =", response.status_code)

    match response.status_code:
        case 201:
            log.info(f"✅ Now subscribed to '{url}'")
            return Subscription(**response.json())
        case 300:
            log.error(f"❌ Multiple feeds found at '{url}'")
            feeds = [FeedChoice(**choice) for choice in response.json()]
            chosen_feed = choose_between_multiple_feeds(feeds)
            return create_subscription(chosen_feed, dry_run)
        case 302:
            log.info(f"✅ Already subscribed to '{url}'")
            return Subscription(**response.json())
        case 404:
            log.error(f"❌ No feed found at '{url}'")
            return None
        case _:
            log.error("❌ Unexpected HTTP status code:", response.status_code)
            log.error(response.text)
            return None


# See: https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#create-subscription
@app.command()
def main(url: str, dry_run: Annotated[bool, typer.Option("--dry-run", "-d")] = False) -> None:
    try:
        subscriptions = get_subscriptions()
        log.info(f"{len(subscriptions)} Feedbin subscriptions found")
    except NotFoundError as e:
        log.error(e)
        subscriptions = []
    except UnexpectedError as e:
        log.error(e)
        subscriptions = []

    # log.debug("🔍 subscriptions =", subscriptions)
    return

    url = typer.prompt("💬 What URL would you like to subscribe to?", type=str)
    typer.confirm(f"🔖 Subscribe to '{url}'?", abort=True)

    # TODO: can I skip this step and just try to add and then handle the response?
    matching_subscription = _find_matching_subscription(url, subscriptions)

    if matching_subscription:
        log.info("👍 Subscription already exists:", matching_subscription)
        raise typer.Abort()
        # raise typer.Exit()

    log.info("👎 No matching subscription found.")
    create_subscription(url, dry_run)

    return None


if __name__ == "__main__":
    app()
