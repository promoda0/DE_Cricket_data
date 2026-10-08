from __future__ import annotations

import json
from pathlib import Path

from src.readers.json_reader import read_json_file


class BronzeIngestionError(Exception):
    """Base exception for Bronze ingestion failures."""


class BronzeWriteError(BronzeIngestionError):
    """Raised when Bronze output cannot be written."""


def ingest_json_to_bronze(
    source_file: Path,
    bronze_dir: Path,
) -> Path:
    """
    Ingest a JSON source file into the Bronze layer.

    The source JSON structure is preserved without applying
    business transformations.

    Args:
        source_file: Source Cricsheet JSON file.
        bronze_dir: Bronze destination directory.

    Returns:
        Path to the generated Bronze file.

    Raises:
        BronzeIngestionError: If ingestion fails.
    """

    data = read_json_file(source_file)

    try:
        bronze_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination_file = bronze_dir / source_file.name

        with destination_file.open(
            mode="w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

    except OSError as exc:
        raise BronzeWriteError(
            f"Failed to write Bronze file "
            f"'{destination_file}': {exc}"
        ) from exc

    return destination_file