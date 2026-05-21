"""
CLI for running scripts.

Usage:
 - uv run cli.py rss --help
 - uv run cli.py rss add <url>
 - uv run cli.py rss entries list <feed_id>
 - uv run cli.py rss entries mark-unread <entry_id> [<entry_id> ...]
 - uv run cli.py modem restart

Docs:
 - https://typer.tiangolo.com/tutorial/subcommands/add-typer
 - https://typer.tiangolo.com/tutorial/subcommands/single-file
 - https://typer.tiangolo.com/tutorial/subcommands/nested-subcommands/#review-the-files
"""

import typer

import modem.restart as modem_cli
import rss.cli as rss_cli

app = typer.Typer(no_args_is_help=True)
app.add_typer(rss_cli.app, name="rss")
app.add_typer(modem_cli.app, name="modem")


if __name__ == "__main__":
    app()
