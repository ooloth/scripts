"""
CLI adapter for Feedbin. All usage of typer should occur in this module.
"""

import os
from typing import Annotated

import rich
import typer

from common.cli import DryRun
from common.logs import log
from rss.entities import FeedOption

subscriptions_app = typer.Typer(no_args_is_help=True)
entries_app = typer.Typer(no_args_is_help=True)

app = typer.Typer(no_args_is_help=True)
app.add_typer(subscriptions_app, name="subscriptions")
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

    try:
        new_subscription = add_subscription(url)
    except MultipleChoicesError as e:
        chosen_feed = _ask_for_feed_choice(e.choices)
        new_subscription = add_subscription(chosen_feed.feed_url)

    log.info("🔍 Counting backlog entries")
    entries = get_feed_entries(new_subscription.feed_id)
    entry_ids = [entry.id for entry in entries]

    mark_backlog_unread = typer.confirm(
        f"🔖 There are {len(entry_ids)} backlog entries. Mark all as unread?", abort=True
    )

    if not mark_backlog_unread:
        rich.print("👋 You're all set!")
        return

    mark_entries_unread(entry_ids)

    # TODO: get all entry ids for this subscription via get_feed_entries
    # TODO: mark all entries as unread via https://github.com/feedbin/feedbin-api/blob/master/content/unread-entries.md#create-unread-entries-mark-as-unread

    # log.debug(f"subscriptions = {subscriptions}")


subscriptions_app.command(name="list")(list_subscriptions)
entries_app.command(name="mark-unread", no_args_is_help=True)(mark_entries_unread)
entries_app.command(name="list", no_args_is_help=True)(get_feed_entries)

# michaeluloth.com = feed_id: 2338770
