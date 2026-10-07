from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.ingestion.bronze_ingestion import (
    BronzeWriteError,
    ingest_json_to_bronze,
)


def test_ingest_json_to_bronze(
    tmp_path: Path,
) -> None:
    """Valid JSON should be written to Bronze."""

    source_file = tmp_path / "1082591.json"
    bronze_dir = tmp_path / "bronze"

    source_data = {
        "meta": {
            "data_version": "1.0.0",
        },
        "info": {
            "venue": "Test Stadium",
            "teams": [
                "Team A",
                "Team B",
            ],
        },
    }

    source_file.write_text(
        json.dumps(source_data),
        encoding="utf-8",
    )

    destination_file = ingest_json_to_bronze(
        source_file=source_file,
        bronze_dir=bronze_dir,
    )

    assert destination_file.exists()
    assert destination_file.name == "1082591.json"

    bronze_data = json.loads(
        destination_file.read_text(
            encoding="utf-8"
        )
    )

    assert bronze_data == source_data


def test_bronze_directory_is_created(
    tmp_path: Path,
) -> None:
    """Bronze directory should be created automatically."""

    source_file = tmp_path / "match.json"
    bronze_dir = (
        tmp_path
        / "output"
        / "bronze"
        / "cricket"
        / "matches"
    )

    source_file.write_text(
        '{"meta": {}}',
        encoding="utf-8",
    )

    ingest_json_to_bronze(
        source_file=source_file,
        bronze_dir=bronze_dir,
    )

    assert bronze_dir.exists()
    assert bronze_dir.is_dir()


def test_invalid_json_is_rejected(
    tmp_path: Path,
) -> None:
    """Invalid JSON should cause ingestion to fail."""

    source_file = tmp_path / "invalid.json"
    bronze_dir = tmp_path / "bronze"

    source_file.write_text(
        '{"invalid": }',
        encoding="utf-8",
    )

    with pytest.raises(Exception):
        ingest_json_to_bronze(
            source_file=source_file,
            bronze_dir=bronze_dir,
        )


def test_missing_source_file_is_rejected(
    tmp_path: Path,
) -> None:
    """Missing source file should cause ingestion to fail."""

    source_file = tmp_path / "missing.json"
    bronze_dir = tmp_path / "bronze"

    with pytest.raises(Exception):
        ingest_json_to_bronze(
            source_file=source_file,
            bronze_dir=bronze_dir,
        )


def test_bronze_output_preserves_source_content(
    tmp_path: Path,
) -> None:
    """Bronze content should match the source content."""

    source_file = tmp_path / "match.json"
    bronze_dir = tmp_path / "bronze"

    source_data = {
        "info": {
            "venue": "Mumbai",
            "season": "2024",
        },
        "innings": [
            {
                "team": "Team A",
                "overs": [],
            }
        ],
    }

    source_file.write_text(
        json.dumps(source_data),
        encoding="utf-8",
    )

    destination_file = ingest_json_to_bronze(
        source_file=source_file,
        bronze_dir=bronze_dir,
    )

    assert json.loads(
        destination_file.read_text(
            encoding="utf-8"
        )
    ) == source_data