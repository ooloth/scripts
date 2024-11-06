from typing import Annotated

import typer

from feedbin.client import FeedOption, MultipleChoicesError, NotFoundError, UnexpectedError, create_subscription
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


def subscribe(url: str) -> None:
    log.info(f"Subscribing to '{url}'")
    try:
        # TODO: do something with the subscription in the response?
        subscription = create_subscription(url)
    except MultipleChoicesError as e:
        chosen_feed = ask_for_feed_choice(e.choices)
        subscribe(chosen_feed.feed_url)
    except NotFoundError as e:
        log.warning(e)
        raise typer.Abort()
    except UnexpectedError as e:
        log.error(e)
        raise typer.Abort()


def ask_for_url() -> str:
    """Prompt the user for a URL to subscribe to."""
    return typer.prompt("💬 What URL would you like to subscribe to?", type=str)


# See: https://github.com/feedbin/feedbin-api/blob/master/content/subscriptions.md#create-subscription
@app.command()
def add(url: str, dry_run: Annotated[bool, typer.Option("--dry-run", "-d")] = False) -> None:
    if not url:
        url = ask_for_url()

    typer.confirm(f"🔖 Subscribe to '{url}'?", abort=True)

    subscribe(url)

    mark_unread = typer.confirm("🔖 Mark backlog as unread?", default=False)

    # try:
    #     subscriptions = get_subscriptions()
    #     log.info(f"{len(subscriptions)} Feedbin subscriptions found")
    # except NotFoundError as e:
    #     log.error(e)
    #     subscriptions = []
    # except UnexpectedError as e:
    #     log.error(e)
    #     subscriptions = []

    # log.debug(f"subscriptions = {subscriptions}")

    return

    # TODO: can I skip this step and just try to add and then handle the response?
    # matching_subscription = _find_matching_subscription(url, subscriptions)

    # if matching_subscription:
    #     log.info("👍 Subscription already exists:", matching_subscription)
    #     raise typer.Abort()
    #     # raise typer.Exit()

    # log.info("👎 No matching subscription found.")
    # create_subscription(url, dry_run)

    return None


if __name__ == "__main__":
    app()
