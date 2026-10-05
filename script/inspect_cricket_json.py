import json
import logging
import sys
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

SOURCE_DIR = Path(r"G:\My Drive\Cricket\ipl")

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s"
)

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
)

logger = logging.getLogger("cricket_json_inspector")


# ============================================================
# JSON Structure Inspection
# ============================================================

def inspect_structure(data, level=0, max_level=3):
    """
    Recursively inspect the JSON structure without dumping
    the complete dataset.
    """

    indent = "  " * level

    if level > max_level:
        logger.info("%s...", indent)
        return

    if isinstance(data, dict):

        for key, value in data.items():

            logger.info(
                "%s%s -> %s",
                indent,
                key,
                type(value).__name__,
            )

            if isinstance(value, (dict, list)):
                inspect_structure(
                    value,
                    level + 1,
                    max_level,
                )

    elif isinstance(data, list):

        logger.info(
            "%sList size -> %d",
            indent,
            len(data),
        )

        if data:
            logger.info(
                "%sInspecting first element:",
                indent,
            )

            inspect_structure(
                data[0],
                level + 1,
                max_level,
            )


# ============================================================
# JSON Reader
# ============================================================

def read_json_file(file_path: Path) -> dict:

    logger.info(
        "Reading JSON file: %s",
        file_path,
    )

    try:

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        logger.info(
            "JSON file successfully loaded: %s",
            file_path.name,
        )

        return data

    except json.JSONDecodeError as exc:

        logger.error(
            "Invalid JSON format in file '%s': %s",
            file_path.name,
            exc,
        )

        raise

    except OSError as exc:

        logger.error(
            "Failed to read file '%s': %s",
            file_path,
            exc,
        )

        raise


# ============================================================
# Source File Discovery
# ============================================================

def get_source_file(source_dir: Path) -> Path:

    logger.info(
        "Scanning source directory: %s",
        source_dir,
    )

    if not source_dir.exists():

        raise FileNotFoundError(
            f"Source directory does not exist: {source_dir}"
        )

    json_files = sorted(
        source_dir.glob("*.json")
    )

    if not json_files:

        raise FileNotFoundError(
            f"No JSON files found in: {source_dir}"
        )

    logger.info(
        "JSON files discovered: %d",
        len(json_files),
    )

    # For inspection, select the first file.
    selected_file = json_files[0]

    logger.info(
        "Selected file for inspection: %s",
        selected_file.name,
    )

    return selected_file


# ============================================================
# Main
# ============================================================

def main() -> int:

    logger.info(
        "Starting cricket JSON inspection"
    )

    try:

        # 1. Discover source file
        json_file = get_source_file(
            SOURCE_DIR
        )

        # 2. Read JSON
        data = read_json_file(
            json_file
        )

        # 3. Root information
        logger.info(
            "Root data type: %s",
            type(data).__name__,
        )

        if isinstance(data, dict):

            logger.info(
                "Root-level keys: %d",
                len(data),
            )

            logger.info(
                "Root-level fields: %s",
                list(data.keys()),
            )

        elif isinstance(data, list):

            logger.info(
                "Root-level record count: %d",
                len(data),
            )

        # 4. Inspect nested structure
        logger.info(
            "Inspecting nested JSON structure"
        )

        inspect_structure(data)

        logger.info(
            "Cricket JSON inspection completed successfully"
        )

        return 0

    except Exception:

        logger.exception(
            "Cricket JSON inspection failed"
        )

        return 1


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":

    sys.exit(main())