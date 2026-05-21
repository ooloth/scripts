"""
CLI adapter for Feedbin. All usage of typer should occur in this module.
"""

import os
from typing import Annotated

import rich
import typer

from common.logs import log
from common.typer import DryRun
from rss.domain import EntryId, FeedId, FeedOption, FeedUrl
from rss.entries.list.feedbin import get_feed_entries
from rss.entries.mark_unread.feedbin import create_unread_entries
from rss.subscriptions.add.feedbin import CreateSubscriptionResult, create_subscription

entries_app = typer.Typer(no_args_is_help=True)

app = typer.Typer(no_args_is_help=True)
app.add_typer(entries_app, name="entries")


MarkUnread = Annotated[bool, typer.Option("--unread", "-u", help="Mark backlog unread")]


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


@app.command("add", no_args_is_help=True)
def add(url: str, mark_backlog_unread: MarkUnread = False, dry_run: DryRun = False) -> None:
    dry_run = os.getenv("DRY_RUN") == "true" or dry_run

    typer.confirm(f"🔖 Subscribe to '{url}'?", default=True, abort=True)

    if dry_run:
        log.warning("🌵 Skipping subscription (dry run)")
        typer.Exit()

    result, data = create_subscription(FeedUrl(url))

    if result == CreateSubscriptionResult.MULTIPLE_CHOICES:
        assert isinstance(data, list)
        chosen_feed = _ask_for_feed_choice(data)
        result, data = create_subscription(chosen_feed.feed_url)

    if result not in (CreateSubscriptionResult.CREATED, CreateSubscriptionResult.EXISTS):
        log.error(f"{result.value}: {data}")
        raise typer.Exit(code=1)

    rich.print(f"✅ {result.value}")


@entries_app.command("list", no_args_is_help=True)
def list_entries(feed_id: int) -> None:
    result, data = get_feed_entries(FeedId(feed_id))
    log.info(f"{result.value}: {data}")


@entries_app.command("mark-unread", no_args_is_help=True)
def mark_entries_unread(entry_ids: list[int]) -> None:
    ids = [EntryId(i) for i in entry_ids]
    result, data = create_unread_entries(ids)
    log.info(f"{result.value}: {data}")

# michaeluloth.com = feed_id: 2338770
