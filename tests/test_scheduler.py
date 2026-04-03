import pytest
from scheduler import add_task_to_scheduler
import re


def test_recurrence_parsing():
    test_cases = [
        ("todo dia às 9h", 9, 0),
        ("todo dia às 14h30", 14, 30),
        ("todo dia às 6h15", 6, 15),
    ]

    for recurrence, expected_hour, expected_minute in test_cases:
        match = re.search(r"(\d{1,2})[h:](\d{1,2})?", recurrence)
        assert match is not None, f"Failed to parse: {recurrence}"
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        assert hour == expected_hour
        assert minute == expected_minute


def test_invalid_recurrence():
    match = re.search(r"(\d{1,2})[h:](\d{1,2})?", "invalid time")
    assert match is None
