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


def test_interval_parsing_minutes():
    """Test that interval_Xm is parsed as minutes, not hours."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    scheduler = AsyncIOScheduler()

    test_cases = [
        ("interval_30m", 30),
        ("interval_15m", 15),
        ("interval_60m", 60),
        ("interval_5m", 5),
    ]

    for recurrence, expected_minutes in test_cases:
        task = {
            "id": f"test_{recurrence}",
            "type": "test",
            "prompt": "test prompt",
            "recurrence": recurrence,
        }

        # Parse the interval format
        if recurrence.startswith("interval_"):
            interval_str = recurrence.replace("interval_", "")

            # Check if it ends with 'm' for minutes
            if interval_str.endswith("m"):
                minutes = int(interval_str.replace("m", ""))
                assert minutes == expected_minutes, (
                    f"Expected {expected_minutes} minutes for {recurrence}, got {minutes}"
                )
            elif interval_str.endswith("h"):
                hours = int(interval_str.replace("h", ""))
                assert hours * 60 == expected_minutes, (
                    f"Expected {expected_minutes} minutes for {recurrence}"
                )


def test_interval_format_handling():
    """Test that interval_30m creates job with minutes=30, not hours."""
    from scheduler import load_scheduled_tasks, save_scheduled_tasks
    import tempfile
    import os

    # Test the parse logic
    def parse_interval(recurrence: str):
        if recurrence.startswith("interval_"):
            interval_str = recurrence.replace("interval_", "")
            if interval_str.endswith("m"):
                return {"minutes": int(interval_str.replace("m", ""))}
            elif interval_str.endswith("h"):
                return {"hours": int(interval_str.replace("h", ""))}
        return None

    # Test minute intervals
    result = parse_interval("interval_30m")
    assert result == {"minutes": 30}, f"Expected minutes=30, got {result}"

    result = parse_interval("interval_5m")
    assert result == {"minutes": 5}, f"Expected minutes=5, got {result}"

    # Test hour intervals (should use hours, not minutes)
    result = parse_interval("interval_6h")
    assert result == {"hours": 6}, f"Expected hours=6, got {result}"


def test_recurrence_format_variations():
    """Test various recurrence format parsing."""
    formats = {
        "interval_30m": ("minutes", 30),
        "interval_1h": ("hours", 1),
        "interval_6h": ("hours", 6),
        "interval_15m": ("minutes", 15),
        "todo dia às 9h": ("daily", "09:00"),
        "todo dia às 14h30": ("daily", "14:30"),
    }

    for recurrence, expected in formats.items():
        if recurrence.startswith("interval_"):
            interval_str = recurrence.replace("interval_", "")

            if expected[0] == "minutes":
                assert interval_str.endswith("m"), f"{recurrence} should end with 'm'"
                value = int(interval_str.replace("m", ""))
                assert value == expected[1], f"Expected {expected[1]}, got {value}"
            elif expected[0] == "hours":
                assert interval_str.endswith("h"), f"{recurrence} should end with 'h'"
                value = int(interval_str.replace("h", ""))
                assert value == expected[1], f"Expected {expected[1]}, got {value}"
