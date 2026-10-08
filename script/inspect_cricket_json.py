from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from src.ingestion.bronze_ingestion import (
    BronzeIngestionError,
    ingest_json_to_bronze,
)
from src.logging.logger_config import configure_logging


logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Ingest a Cricsheet JSON file into Bronze."
    )

    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Path to the source Cricsheet JSON file.",
    )

    parser.add_argument(
        "--bronze-dir",
        required=True,
        type=Path,
        help="Destination directory for Bronze data.",
    )

    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("logs/bronze_ingestion.log"),
        help="Path to the ingestion log file.",
    )

    return parser.parse_args()


def main() -> int:
    """Run the Bronze ingestion process."""

    args = parse_arguments()

    configure_logging(
        log_file=args.log_file,
    )

    logger.info("Bronze ingestion started")
    logger.info("Source file: %s", args.source)
    logger.info("Bronze directory: %s", args.bronze_dir)

    try:
        destination_file = ingest_json_to_bronze(
            source_file=args.source,
            bronze_dir=args.bronze_dir,
        )

        logger.info(
            "Bronze ingestion completed successfully"
        )

        logger.info(
            "Bronze file created: %s",
            destination_file,
        )

        return 0

    except BronzeIngestionError:
        logger.exception(
            "Bronze ingestion failed"
        )
        return 1

    except Exception:
        logger.exception(
            "Unexpected error during Bronze ingestion"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())