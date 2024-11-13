"""
CLI adapter for Feedbin. All typer commands should be defined in this module.
"""

from typing import Annotated

import typer

from common.cli import DryRun
from feedbin.adapters.api.entries import get_feed_entries
from feedbin.application.add_subscription import add_subscription
from feedbin.application.list_subscriptions import list_subscriptions
from feedbin.application.mark_entries_unread import mark_entries_unread

subscriptions_app = typer.Typer(no_args_is_help=True)
entries_app = typer.Typer(no_args_is_help=True)

app = typer.Typer(no_args_is_help=True)
app.add_typer(subscriptions_app, name="subscriptions")
app.add_typer(entries_app, name="entries")


MarkUnread = Annotated[bool, typer.Option("--unread", "-u", help="Mark backlog unread")]


@app.command("add", no_args_is_help=True)
def add(url: str, mark_backlog_unread: MarkUnread = False, dry_run: DryRun = False) -> None:
    add_subscription(url, mark_backlog_unread=mark_backlog_unread, dry_run=dry_run)


subscriptions_app.command(name="list")(list_subscriptions)
entries_app.command(name="mark-unread", no_args_is_help=True)(mark_entries_unread)
entries_app.command(name="list", no_args_is_help=True)(get_feed_entries)

# michaeluloth.com = feed_id: 2338770
