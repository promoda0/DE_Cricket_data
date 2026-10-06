import json
from pathlib import Path

import pytest

from src.readers.json_reader import (
    InvalidJsonError,
    JsonFileNotFoundError,
    JsonFileReadError,
    JsonReaderError,
    read_json_file,
)


def test_read_valid_json_file(tmp_path: Path) -> None:
    file_path = tmp_path / "valid.json"

    expected_data = {
        "meta": {
            "data_version": "1.0.0",
        },
        "info": {
            "venue": "Test Stadium",
        },
    }

    file_path.write_text(
        json.dumps(expected_data),
        encoding="utf-8",
    )

    result = read_json_file(file_path)

    assert result == expected_data


def test_read_missing_json_file(tmp_path: Path) -> None:
    file_path = tmp_path / "missing.json"

    with pytest.raises(JsonFileNotFoundError):
        read_json_file(file_path)


def test_read_invalid_json_file(tmp_path: Path) -> None:
    file_path = tmp_path / "invalid.json"

    file_path.write_text(
        '{"meta": invalid}',
        encoding="utf-8",
    )

    with pytest.raises(InvalidJsonError):
        read_json_file(file_path)


def test_read_json_file_with_non_dictionary_root(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "list.json"

    file_path.write_text(
        json.dumps(["item1", "item2"]),
        encoding="utf-8",
    )

    with pytest.raises(JsonReaderError):
        read_json_file(file_path)


def test_read_directory_instead_of_file(tmp_path: Path) -> None:
    directory_path = tmp_path / "directory"
    directory_path.mkdir()

    with pytest.raises(JsonFileReadError):
        read_json_file(directory_path)