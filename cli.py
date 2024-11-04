import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from feedbin import subscribe

# from feedbin.subscribe import subscribe

# Docs:
# - https://typer.tiangolo.com/tutorial/subcommands/add-typer

# TODO: add modem typer app as well
app = typer.Typer(no_args_is_help=True)
# app.add_typer(subscribe.app, name="feed")

console = Console()


DRY_RUN_DEFAULT = "false"
SCRIPTS = ["feedbin/subscribe", "modem/restart"]


def _get_scripts_table(scripts: list[str] = SCRIPTS) -> Table:
    """Display the available script options as a table."""
    table = Table(title="Available scripts:", show_header=False, title_justify="left", title_style="bold cyan")
    table.add_column(justify="right", style="cyan", no_wrap=True)
    table.add_column(style="magenta")

    for idx, module in enumerate(scripts, start=1):
        table.add_row(str(idx), module)

    return table


def _get_env() -> dict[str, str]:
    """Return updated environment variables to be used by the subprocess."""
    env = os.environ.copy()

    env["DRY_RUN"] = env.get("DRY_RUN", DRY_RUN_DEFAULT)
    env["PYTHONPATH"] = Path(__file__).parent.absolute().as_posix()  # this project's root directory

    # log("env:", env)
    return env


@app.command()
def pick() -> None:
    """Run the selected script."""
    console.print(_get_scripts_table())
    script_number = typer.prompt("💬 Which script number would you like to run?", type=int)

    if 1 <= script_number <= len(SCRIPTS):
        script = SCRIPTS[script_number - 1]

        typer.echo(f"🚀 Running '{script}'.")

        match script:
            case "feedbin/subscribe":
                url = typer.prompt("💬 What URL would you like to subscribe to?", type=str)
                subscribe.add(url)
            case _:
                subprocess.run(["uv", "run", f"{script}.py"], env=_get_env())
    else:
        typer.echo("🚨 Invalid option '{script_number}'")


if __name__ == "__main__":
    app()
