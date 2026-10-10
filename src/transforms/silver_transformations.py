
from __future__ import annotations

from pathlib import Path
from typing import Any

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import (
    DateType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from src.readers.json_reader import read_json_file


class SilverTransformationError(Exception):
    """Base exception for Silver transformation failures."""


MATCH_SCHEMA = StructType(
    [
        StructField("match_id", StringType(), False),
        StructField("season", StringType(), True),
        StructField("match_type", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("team_1", StringType(), True),
        StructField("team_2", StringType(), True),
        StructField("city", StringType(), True),
        StructField("venue", StringType(), True),
        StructField("match_date", DateType(), True),
    ]
)

INNINGS_SCHEMA = StructType(
    [
        StructField("match_id", StringType(), False),
        StructField("innings_number", IntegerType(), False),
        StructField("batting_team", StringType(), False),
    ]
)

DELIVERY_SCHEMA = StructType(
    [
        StructField("match_id", StringType(), False),
        StructField("innings_number", IntegerType(), False),
        StructField("over_number", IntegerType(), False),
        StructField("ball_number", IntegerType(), False),
        StructField("batter", StringType(), False),
        StructField("bowler", StringType(), False),
        StructField("non_striker", StringType(), True),
        StructField("runs_batter", IntegerType(), True),
        StructField("runs_extras", IntegerType(), True),
        StructField("runs_total", IntegerType(), True),
    ]
)


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SilverTransformationError(
            f"Expected '{field_name}' to be a JSON object."
        )
    return value


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_integer(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise SilverTransformationError(
            f"Expected '{field_name}' to be an integer."
        )
    return value


def _parse_match_date(info: dict[str, Any]):
    from datetime import date

    dates = info.get("dates", [])
    if not dates:
        return None

    if not isinstance(dates, list) or not isinstance(dates[0], str):
        raise SilverTransformationError(
            "Expected 'info.dates' to be a list of date strings."
        )

    try:
        return date.fromisoformat(dates[0])
    except ValueError as exc:
        raise SilverTransformationError(
            f"Invalid match date: {dates[0]}"
        ) from exc


def transform_match(
    source_file: Path,
    data: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Convert one Cricsheet match object into Silver row records."""
    info = _require_mapping(data.get("info"), "info")
    innings_list = data.get("innings")

    if not isinstance(innings_list, list):
        raise SilverTransformationError(
            "Expected root field 'innings' to be a list."
        )

    teams = info.get("teams", [])
    if not isinstance(teams, list):
        raise SilverTransformationError("Expected 'info.teams' to be a list.")

    match_id = source_file.stem

    match_row = {
        "match_id": match_id,
        "season": _optional_string(info.get("season")),
        "match_type": _optional_string(info.get("match_type")),
        "gender": _optional_string(info.get("gender")),
        "team_1": _optional_string(teams[0]) if len(teams) > 0 else None,
        "team_2": _optional_string(teams[1]) if len(teams) > 1 else None,
        "city": _optional_string(info.get("city")),
        "venue": _optional_string(info.get("venue")),
        "match_date": _parse_match_date(info),
    }

    innings_rows: list[dict[str, Any]] = []
    delivery_rows: list[dict[str, Any]] = []

    for innings_number, innings_value in enumerate(innings_list, start=1):
        innings = _require_mapping(
            innings_value, f"innings[{innings_number - 1}]"
        )
        batting_team = innings.get("team")

        if not isinstance(batting_team, str) or not batting_team:
            raise SilverTransformationError(
                f"Innings {innings_number} has no valid batting team."
            )

        innings_rows.append(
            {
                "match_id": match_id,
                "innings_number": innings_number,
                "batting_team": batting_team,
            }
        )

        overs = innings.get("overs", [])
        if not isinstance(overs, list):
            raise SilverTransformationError(
                f"Innings {innings_number}: expected 'overs' to be a list."
            )

        for over_value in overs:
            over = _require_mapping(over_value, "over")
            over_number = over.get("over")
            deliveries = over.get("deliveries")

            if (
                isinstance(over_number, bool)
                or not isinstance(over_number, int)
            ):
                raise SilverTransformationError(
                    f"Innings {innings_number}: invalid over number."
                )

            if not isinstance(deliveries, list):
                raise SilverTransformationError(
                    f"Over {over_number}: expected deliveries to be a list."
                )

            # Position within the over, not the legal-ball count.
            for ball_number, delivery_value in enumerate(deliveries, start=1):
                delivery = _require_mapping(delivery_value, "delivery")
                runs = _require_mapping(
                    delivery.get("runs"), "delivery.runs"
                )

                batter = delivery.get("batter")
                bowler = delivery.get("bowler")

                if not isinstance(batter, str) or not batter:
                    raise SilverTransformationError(
                        "Delivery has no valid batter."
                    )
                if not isinstance(bowler, str) or not bowler:
                    raise SilverTransformationError(
                        "Delivery has no valid bowler."
                    )

                delivery_rows.append(
                    {
                        "match_id": match_id,
                        "innings_number": innings_number,
                        "over_number": over_number,
                        "ball_number": ball_number,
                        "batter": batter,
                        "bowler": bowler,
                        "non_striker": _optional_string(
                            delivery.get("non_striker")
                        ),
                        "runs_batter": _optional_integer(
                            runs.get("batter"), "runs.batter"
                        ),
                        "runs_extras": _optional_integer(
                            runs.get("extras"), "runs.extras"
                        ),
                        "runs_total": _optional_integer(
                            runs.get("total"), "runs.total"
                        ),
                    }
                )

    return match_row, innings_rows, delivery_rows


def transform_bronze_file(
    spark: SparkSession,
    source_file: Path,
) -> tuple[DataFrame, DataFrame, DataFrame]:
    """Build explicitly typed Silver DataFrames from one Bronze JSON file."""
    try:
        data = read_json_file(source_file)
        match_row, innings_rows, delivery_rows = transform_match(
            source_file, data
        )

        matches_df = spark.createDataFrame([match_row], schema=MATCH_SCHEMA)
        innings_df = spark.createDataFrame(
            innings_rows, schema=INNINGS_SCHEMA
        )
        deliveries_df = spark.createDataFrame(
            delivery_rows, schema=DELIVERY_SCHEMA
        )

        return matches_df, innings_df, deliveries_df

    except SilverTransformationError:
        raise
    except Exception as exc:
        raise SilverTransformationError(
            f"Failed to transform Bronze file '{source_file}': {exc}"
        ) from exc


def write_silver_datasets(
    matches_df: DataFrame,
    innings_df: DataFrame,
    deliveries_df: DataFrame,
    silver_dir: Path,
) -> None:
    """Write Silver datasets as Parquet files."""
    try:
        matches_df.write.mode("append").parquet(
            str(silver_dir / "matches")
        )
        innings_df.write.mode("append").parquet(
            str(silver_dir / "innings")
        )
        deliveries_df.write.mode("append").parquet(
            str(silver_dir / "deliveries")
        )
    except Exception as exc:
        raise SilverTransformationError(
            f"Failed to write Silver datasets to '{silver_dir}': {exc}"
        ) from exc
