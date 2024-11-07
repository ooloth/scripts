import os
from pathlib import Path

from rich.table import Table


def get_env(dry_run: bool = False) -> dict[str, str]:
    """Return updated environment variables to be used by the subprocess."""
    env = os.environ.copy()

    env["DRY_RUN"] = env.get("DRY_RUN", str(dry_run))
    env["PYTHONPATH"] = Path(__file__).parent.absolute().as_posix()  # this project's root directory

    return env


def format_as_table(items: list[str], title: str) -> Table:
    """Display the available script options as a table."""
    table = Table(title=f"{title}:", show_header=False, title_justify="left", title_style="bold cyan")
    table.add_column(justify="right", style="cyan", no_wrap=True)
    table.add_column(style="magenta")

    for idx, module in enumerate(items, start=1):
        table.add_row(str(idx), module)

    return table
