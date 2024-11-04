import sys

import rich


def log(*objects: object) -> None:
    """Send debugging print statements to stderr with pretty formatting."""
    rich.print(*objects, file=sys.stderr)
