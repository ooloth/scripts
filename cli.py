"""
CLI for running scripts.

Usage:
 - uv run cli.py select
 - uv run cli.py feedbin
 - uv run cli.py feedbin add

Docs:
 - https://typer.tiangolo.com/tutorial/subcommands/add-typer
"""

import subprocess
from typing import Annotated

import typer
from rich.console import Console

from feedbin import add
from utils.cli import format_as_table, get_env
from utils.logs import log

# TODO: add modem typer app as well
app = typer.Typer(no_args_is_help=True)
app.add_typer(add.app, name="feedbin")

console = Console()


SCRIPTS = ["feedbin/subscribe", "modem/restart"]


@app.command()
def select(dry_run: bool = False) -> None:
    """Run the selected script."""
    console.print(format_as_table(SCRIPTS, "Available scripts"))
    script_number = typer.prompt("💬 Which script number would you like to run?", type=int)

    if 1 <= script_number <= len(SCRIPTS):
        script = SCRIPTS[script_number - 1]

        log.info(f"Running '{script}'.")

        match script:
            case "feedbin/subscribe":
                add.app()
            case _:
                subprocess.run(["uv", "run", f"{script}.py"], env=get_env(dry_run))
    else:
        log.info("Invalid option '{script_number}'")


# @app.command(hidden=True)
# def main(
#     subcommand: Annotated[str, typer.Argument()] = "select",
#     dry_run: Annotated[bool, typer.Option("--dry-run", "-d")] = False,
# ) -> None:
#     match subcommand:
#         case "select":
#             select()
#         case "feedbin":
#             log.info("Running 'feed' subcommand.")
#             add.app()
#         case _:
#             log.error("Invalid subcommand")


if __name__ == "__main__":
    app()
