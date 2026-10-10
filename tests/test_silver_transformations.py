
from pathlib import Path

import pytest

from src.transforms.silver_transformations import (
    SilverTransformationError,
    transform_match,
)


@pytest.fixture
def sample_match() -> dict:
    return {
        "info": {
            "season": "2024",
            "match_type": "T20",
            "gender": "male",
            "teams": ["Team A", "Team B"],
            "city": "Mumbai",
            "venue": "Example Stadium",
            "dates": ["2024-04-01"],
        },
        "innings": [
            {
                "team": "Team A",
                "overs": [
                    {
                        "over": 0,
                        "deliveries": [
                            {
                                "batter": "Player A",
                                "bowler": "Player B",
                                "non_striker": "Player C",
                                "runs": {
                                    "batter": 4,
                                    "extras": 0,
                                    "total": 4,
                                },
                            },
                            {
                                "batter": "Player A",
                                "bowler": "Player B",
                                "non_striker": "Player C",
                                "runs": {
                                    "batter": 0,
                                    "extras": 1,
                                    "total": 1,
                                },
                            },
                        ],
                    }
                ],
            },
            {
                "team": "Team B",
                "overs": [],
            },
        ],
    }


def test_match_mapping_and_grain(sample_match: dict) -> None:
    match, innings, deliveries = transform_match(
        Path("1234567.json"), sample_match
    )

    assert match["match_id"] == "1234567"
    assert match["venue"] == "Example Stadium"
    assert match["team_1"] == "Team A"
    assert match["team_2"] == "Team B"
    assert match["match_date"].isoformat() == "2024-04-01"

    assert len([match]) == 1
    assert len(innings) == 2
    assert len(deliveries) == 2


def test_innings_numbering(sample_match: dict) -> None:
    _, innings, _ = transform_match(
        Path("1234567.json"), sample_match
    )

    assert [row["innings_number"] for row in innings] == [1, 2]
    assert [row["batting_team"] for row in innings] == [
        "Team A",
        "Team B",
    ]


def test_delivery_position_and_runs(sample_match: dict) -> None:
    _, _, deliveries = transform_match(
        Path("1234567.json"), sample_match
    )

    assert deliveries[0]["over_number"] == 0
    assert deliveries[0]["ball_number"] == 1
    assert deliveries[0]["runs_total"] == 4

    assert deliveries[1]["ball_number"] == 2
    assert deliveries[1]["runs_extras"] == 1
    assert deliveries[1]["runs_total"] == 1


def test_invalid_innings_structure_is_rejected() -> None:
    invalid_match = {
        "info": {"teams": ["Team A", "Team B"]},
        "innings": "not-a-list",
    }

    with pytest.raises(
        SilverTransformationError,
        match="innings.*list",
    ):
        transform_match(Path("1234567.json"), invalid_match)


def test_missing_batting_team_is_rejected() -> None:
    invalid_match = {
        "info": {"teams": ["Team A", "Team B"]},
        "innings": [{"overs": []}],
    }

    with pytest.raises(
        SilverTransformationError,
        match="batting team",
    ):
        transform_match(Path("1234567.json"), invalid_match)
