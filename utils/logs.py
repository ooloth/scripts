import sys

import rich


def log(label: str, value: object | None = None) -> None:
    """Send debugging print statements to stderr to avoid concatenating them with the puzzle answer sent to stdout."""
    if value is None:
        rich.print(label, file=sys.stderr)
    else:
        rich.print(label, value, file=sys.stderr)
    # rich.print(f"{obj=}", file=sys.stderr)
