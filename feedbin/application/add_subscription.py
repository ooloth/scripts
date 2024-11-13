# TODO: move all "typer" usage to feedbin.adapters.cli

import os
from typing import Annotated

import rich
import typer

from common.cli import DryRun
from common.logs import log
from feedbin.adapters.api import NotFoundError, UnexpectedError
from feedbin.adapters.api.entries import get_feed_entries
from feedbin.adapters.api.subscriptions import FeedOption, MultipleChoicesError, Subscription, create_subscription
from feedbin.application.mark_entries_unread import mark_entries_unread

app = typer.Typer(no_args_is_help=True)


# def _find_matching_subscription(url: str, subscriptions: list[Subscription]):
#     url_without_trailing_slash = url.rstrip("/")
#     for sub in subscriptions:
#         if sub.site_url.strip("/") == url_without_trailing_slash:
#             return sub
#     return None


def _ask_for_feed_choice(feeds: list[FeedOption]) -> FeedOption:
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


def subscribe_to_feed(url: str) -> Subscription:
    log.info(f"🔖 Subscribing to feed at '{url}'")

    try:
        return create_subscription(url)
    except MultipleChoicesError as e:
        chosen_feed = _ask_for_feed_choice(e.choices)
        return subscribe_to_feed(chosen_feed.feed_url)
    except NotFoundError as e:
        log.warning(e)
        raise typer.Abort()
    except UnexpectedError as e:
        log.error(e)
        raise typer.Abort()


Unread = Annotated[bool, typer.Option("--unread", "-u", help="Mark backlog unread")]


def add_subscription(url: str, mark_backlog_unread: Unread = False, dry_run: DryRun = False) -> None:
    dry_run = os.getenv("DRY_RUN") == "true" or dry_run

    typer.confirm(f"🔖 Subscribe to '{url}'?", abort=True)

    if dry_run:
        log.warning("🌵 Skipping subscription (dry run)")
        typer.Exit()

    new_subscription = subscribe_to_feed(url)
    log.debug(f"🔍 new_subscription: {new_subscription}")

    mark_backlog_unread = typer.confirm("🔖 Mark backlog unread?", default=mark_backlog_unread)

    if not mark_backlog_unread:
        rich.print("👋 You're all set!")
        typer.Exit()

    log.info("🔖 Getting all entries")
    entries = get_feed_entries(new_subscription.feed_id)
    log.debug(f"🔍 entries: {entries}")

    entry_ids = [entry.id for entry in entries]
    log.debug(f"🔍 entry_ids: {entry_ids}")

    log.info("🔖 Marking all entries as unread")
    mark_entries_unread(entry_ids)
    # TODO: get all entry ids for this subscription via get_feed_entries
    # TODO: mark all entries as unread via https://github.com/feedbin/feedbin-api/blob/master/content/unread-entries.md#create-unread-entries-mark-as-unread

    # log.debug(f"subscriptions = {subscriptions}")

    return
