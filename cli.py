"""
CLI for running scripts.

Usage:
 - uv run cli.py feedbin
 - uv run cli.py feedbin add
 - uv run cli.py modem restart

Docs:
 - https://typer.tiangolo.com/tutorial/subcommands/add-typer
 - https://typer.tiangolo.com/tutorial/subcommands/single-file
 - https://typer.tiangolo.com/tutorial/subcommands/nested-subcommands/#review-the-files
"""

import typer

import feedbin.cli as feedbin_cli
import modem.restart as modem_cli

app = typer.Typer(no_args_is_help=True)
app.add_typer(feedbin_cli.app, name="feedbin")
app.add_typer(modem_cli.app, name="modem")


if __name__ == "__main__":
    app()
