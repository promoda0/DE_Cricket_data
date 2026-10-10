
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from pyspark.sql import SparkSession

from src.logging.logger_config import configure_logging
from src.transforms.silver_transformations import (
    SilverTransformationError,
    transform_bronze_file,
    write_silver_datasets,
)

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transform one Bronze Cricket JSON file into Silver."
    )
    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Path to one Bronze JSON file.",
    )
    parser.add_argument(
        "--silver-dir",
        required=True,
        type=Path,
        help="Root directory for Silver Parquet datasets.",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("logs/silver_transformations.log"),
        help="Log file path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(log_file=args.log_file)

    if not args.source.exists() or not args.source.is_file():
        logger.error("Source file does not exist or is not a file: %s",
                     args.source)
        return 1

    spark = None

    try:
        logger.info("Starting Silver transformation.")
        logger.info("Source: %s", args.source)
        logger.info("Silver destination: %s", args.silver_dir)

        spark = (
            SparkSession.builder
            .appName("CricketSilverTransformations")
            .getOrCreate()
        )

        matches_df, innings_df, deliveries_df = transform_bronze_file(
            spark, args.source
        )

        logger.info(
            "Transformed records: matches=%s, innings=%s, deliveries=%s",
            matches_df.count(),
            innings_df.count(),
            deliveries_df.count(),
        )

        write_silver_datasets(
            matches_df,
            innings_df,
            deliveries_df,
            args.silver_dir,
        )

        logger.info("Silver datasets written successfully.")
        return 0

    except SilverTransformationError:
        logger.exception("Silver transformation failed.")
        return 1
    except Exception:
        logger.exception("Unexpected Silver pipeline failure.")
        return 1
    finally:
        if spark is not None:
            spark.stop()


if __name__ == "__main__":
    sys.exit(main())
