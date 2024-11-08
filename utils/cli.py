import os
from pathlib import Path
from typing import Annotated

import typer
from rich.table import Table

DryRun = Annotated[bool, typer.Option("--dry-run", "-d", help="Dry run mode")]


# TODO: delete? not currently used... maybe useful for feed choices?
def get_env(dry_run: str = "false") -> dict[str, str]:
    """Return updated environment variables to be used by the subprocess."""
    env = os.environ.copy()
    dry_run_option: bool = dry_run.lower() == "true"

    env["DRY_RUN"] = env.get("DRY_RUN", str(dry_run_option).lower())
    env["PYTHONPATH"] = Path.cwd().resolve().as_posix()  # this project's root directory

    return env


# TODO: delete? not currently used... maybe useful for feed choices?
def format_as_table(items: list[str], title: str) -> Table:
    """Display the available script options as a table."""
    table = Table(title=f"{title}:", show_header=False, title_justify="left", title_style="bold cyan")
    table.add_column(justify="right", style="cyan", no_wrap=True)
    table.add_column(style="magenta")

    for idx, module in enumerate(items, start=1):
        table.add_row(str(idx), module)

    return table
