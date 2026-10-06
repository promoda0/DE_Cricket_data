import logging
from pathlib import Path


DEFAULT_LOG_LEVEL = logging.INFO

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s"
)


def configure_logging(
    log_file: Path | None = None,
    log_level: int = DEFAULT_LOG_LEVEL,
) -> None:
    """
    Configure application-wide logging.

    Args:
        log_file: Optional path where logs should be written.
        log_level: Logging level for the application.
    """

    handlers: list[logging.Handler] = [
        logging.StreamHandler()
    ]

    if log_file is not None:
        log_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        handlers.append(
            logging.FileHandler(
                log_file,
                encoding="utf-8",
            )
        )

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=handlers,
        force=True,
    )