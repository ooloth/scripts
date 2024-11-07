from typing import Annotated

import rich
import typer

from feedbin.api import (
    FeedOption,
    MultipleChoicesError,
    NotFoundError,
    Subscription,
    UnexpectedError,
    create_subscription,
    get_subscriptions,
)
from utils.logs import log

# Docs:
# - https://typer.tiangolo.com/tutorial/subcommands/add-typer

app = typer.Typer()


# def _find_matching_subscription(url: str, subscriptions: list[Subscription]):
#     url_without_trailing_slash = url.rstrip("/")
#     for sub in subscriptions:
#         if sub.site_url.strip("/") == url_without_trailing_slash:
#             return sub
#     return None


@app.command(name="list")
def list_subscriptions() -> list[Subscription]:
    try:
        subscriptions = get_subscriptions()
        log.info(f"{len(subscriptions)} Feedbin subscriptions found")
        return subscriptions
    except NotFoundError as e:
        log.error(e)
        return []
    except UnexpectedError as e:
        log.error(e)
        return []


def ask_for_feed_choice(feeds: list[FeedOption]) -> FeedOption:
    """Prompt the user to choose between multiple feeds."""
    print("Multiple feeds found. Please choose one:")
    for idx, feed in enumerate(feeds, start=1):
        print(f"{idx}. {feed.title} ({feed.feed_url})")

    choice = typer.prompt("Which feed number would you like to subscribe to?", type=int)
    if 1 <= choice <= len(feeds):
        selected_feed = feeds[choice - 1]
        log.info(f"🔖 Selected feed URL: {selected_feed.feed_url}")
        return selected_feed
    else:
        log.error("🚨 Invalid choice")
        raise typer.Abort()


def subscribe(url: str) -> Subscription:
    log.info(f"Subscribing to '{url}'")
    try:
        return create_subscription(url)
    except MultipleChoicesError as e:
        chosen_feed = ask_for_feed_choice(e.choices)
        return subscribe(chosen_feed.feed_url)
    except NotFoundError as e:
        log.warning(e)
        raise typer.Abort()
    except UnexpectedError as e:
        log.error(e)
        raise typer.Abort()


# See: https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#create-subscription
@app.command()
def add(url: str, dry_run: Annotated[bool, typer.Option("--dry-run", "-d")] = False) -> None:
    # Get the URL
    if not url:
        url = typer.prompt("💬 What URL would you like to subscribe to?", type=str)

    typer.confirm(f"🔖 Subscribe to '{url}'?", abort=True)

    # Subscribe
    new_subscription = subscribe(url)
    log.debug(f"🔬 new_subscription = {new_subscription}")

    # Mark backlog  unread
    mark_unread = typer.confirm("🔖 Mark backlog unread?", default=False)
    if not mark_unread:
        rich.print("👋 You're all set!")
        typer.Exit()

    log.info("🔖 Marking backlog as unread")
    # TODO: get all entry ids for this subscription via get_feed_entries
    # TODO: mark all entries as unread via https://github.com/feedbin/feedbin-api/blob/master/content/unread-entries.md#create-unread-entries-mark-as-unread

    # log.debug(f"subscriptions = {subscriptions}")

    return


if __name__ == "__main__":
    app()
