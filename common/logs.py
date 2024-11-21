import logging
from functools import partial
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

from rich.logging import RichHandler

# TODO: https://calmcode.io/course/logging/rich
# TODO: https://www.willmcgugan.com/blog/tech/post/prettier-logging-with-rich/
# TODO: https://rich.readthedocs.io/en/stable/logging.html
# TODO: https://rich.readthedocs.io/en/stable/reference/logging.html
# See: https://mathspp.com/blog/til/042

LOG_DIR = ".logs"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes
BACKUP_COUNT = 5


def file_handler(level: Literal["debug", "error"]) -> logging.FileHandler:
    """Create a file handler for logging."""

    log_dir = Path(LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    log_file_path = log_dir / f"{level}.log"

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=MAX_FILE_SIZE,
        backupCount=BACKUP_COUNT,
    )
    file_handler.setLevel(level.upper())
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)-8s %(message)s (%(filename)s:%(lineno)d:%(funcName)s)",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    return file_handler


_log = None


def get_logger() -> logging.Logger:
    """Create and cache the logger."""
    global _log

    if _log is None:
        # Configure both console and file handlers
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(), file_handler(level="debug"), file_handler(level="error")],
        )

        # Always output exceptions and stack traces when logging an error
        logging.error = partial(logging.error, exc_info=True, stack_info=True)
        logging.critical = partial(logging.critical, exc_info=True, stack_info=True)

        _log = logging.getLogger()

    return _log


log = get_logger()

# Export the logger
__all__ = ["log"]
