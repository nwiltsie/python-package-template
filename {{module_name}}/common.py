"""Common utilities."""

import logging
import sys


class ColorFormatter(logging.Formatter):
    """A log formatter to colorize the log."""

    GREY = "\x1b[38;21m"
    YELLOW = "\x1b[33;21m"
    RED = "\x1b[31;21m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    COLORS = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")

    STYLES = (
        "none",
        "bold",
        "faint",
        "italic",
        "underline",
        "blink",
        "blink2",
        "negative",
        "concealed",
        "crossed",
    )

    LEVEL_STYLES = {
        logging.DEBUG: ("", "faint"),
        logging.INFO: ("", ""),
        logging.WARNING: ("yellow", ""),
        logging.ERROR: ("red", ""),
        logging.CRITICAL: ("bold", "red"),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_cache = {}

    def _apply_style(self, string: str, color: str, styles: str) -> str:
        """
        Apply the ansi style to the string and return it.

        color can be blank or a named color. Styles are a ;-separated list or
        blank.
        """
        if not color and not styles:
            return string

        key = (color, styles)
        if key not in self._style_cache:
            prefix = "\x1b["

            if color:
                prefix += str(30 + self.COLORS.index(color))

            if styles:
                prefix += ";" + ";".join(
                    str(self.STYLES.index(style)) for style in styles.split(";")
                )

            self._style_cache[key] = prefix

        return f"{self._style_cache[key]}m{string}\x1b[0m"

    def formatMessage(self, record):
        return self._apply_style(
            super().formatMessage(record), *self.LEVEL_STYLES[record.levelno]
        )


def configure_logging():
    """Set up the logging system."""
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        ColorFormatter(fmt="%(asctime)s %(levelname)-8s %(name)-14s %(message)s")
    )

    logging.basicConfig(
        level=logging.NOTSET,
        handlers=(handler,),
    )


class LoggingMixin:
    """A mixin class for logging."""

    # pylint: disable=too-few-public-methods
    @property
    def logger(self):
        """Create and return a logger."""
        if not hasattr(self, "_logger") or not self._logger:
            self._logger = logging.getLogger(self.__class__.__name__)

        return self._logger


# https://gist.github.com/gurunars/4470c97c916e7b3c4731469c69671d06
def confirm(message):
    """
    Ask user to enter Y or N (case-insensitive).
    :return: True if the answer is Y.
    :rtype: bool
    """
    log = logging.getLogger(__name__)
    answer = ""
    while answer not in ["y", "n", "q"]:
        try:
            answer = input(f"{message} [y/n/q]? ").lower()
        except KeyboardInterrupt:
            log.warning("Treating Ctrl-C as a 'q'...")
            answer = "q"

    log.debug("User answered `%s` with `%s`", message, answer)

    if answer == "q":
        sys.exit(1)

    return answer == "y"
