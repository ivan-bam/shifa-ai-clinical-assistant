import logging
import sys

_configured = False


def configure_logging(level: int = logging.INFO) -> None:
    """
    Set up application-wide logging once.

    Produces lines like:
        2026-05-30 12:00:00 | INFO    | shifa.request | abc12345 | --> POST /clinical/generate
    """
    global _configured
    if _configured:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Use a dotted name like 'shifa.workflow'."""
    return logging.getLogger(name)
