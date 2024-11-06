import logging

from rich.logging import RichHandler

# See: https://mathspp.com/blog/til/042
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)

log = logging.getLogger()


# def log(*objects: object) -> None:
#     """Send debugging print statements to stderr with pretty formatting."""
#     rich.print(*objects, file=sys.stderr)
