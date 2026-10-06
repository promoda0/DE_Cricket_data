import json
from pathlib import Path
from typing import Any


class JsonReaderError(Exception):
    """Base exception for JSON reader failures."""


class JsonFileNotFoundError(JsonReaderError):
    """Raised when the requested JSON file does not exist."""


class JsonFileReadError(JsonReaderError):
    """Raised when the JSON file cannot be read."""


class InvalidJsonError(JsonReaderError):
    """Raised when the file contains invalid JSON."""


def read_json_file(file_path: Path) -> dict[str, Any]:
    """
    Read and parse a JSON file.

    Args:
        file_path: Path to the JSON file.

    Returns:
        Parsed JSON document as a dictionary.

    Raises:
        JsonFileNotFoundError: If the file does not exist.
        JsonFileReadError: If the file cannot be read.
        InvalidJsonError: If the file contains invalid JSON.
        JsonReaderError: If the root JSON object is not a dictionary.
    """

    if not file_path.exists():
        raise JsonFileNotFoundError(
            f"JSON file does not exist: {file_path}"
        )

    if not file_path.is_file():
        raise JsonFileReadError(
            f"Path is not a file: {file_path}"
        )

    try:
        with file_path.open(
            mode="r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as exc:
        raise InvalidJsonError(
            f"Invalid JSON in file '{file_path}': {exc}"
        ) from exc

    except OSError as exc:
        raise JsonFileReadError(
            f"Failed to read JSON file '{file_path}': {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise JsonReaderError(
            f"Expected JSON root object to be a dictionary, "
            f"but received {type(data).__name__}"
        )

    return data