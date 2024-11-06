import logging

from rich.logging import RichHandler

# TODO: https://calmcode.io/course/logging/rich
# TODO: https://www.willmcgugan.com/blog/tech/post/prettier-logging-with-rich/
# TODO: https://rich.readthedocs.io/en/stable/logging.html
# TODO: https://rich.readthedocs.io/en/stable/reference/logging.html
# See: https://mathspp.com/blog/til/042

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)

# Create a module-level logger
log = logging.getLogger(__name__)

# Export the logger
__all__ = ["log"]

# def log(*objects: object) -> None:
#     """Send debugging print statements to stderr with pretty formatting."""
#     rich.print(*objects, file=sys.stderr)
