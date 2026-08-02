"""Utility functions for parsing cron schedules for APScheduler."""

from typing import Any


def parse_cron_schedule(cron_string: str) -> dict[str, Any]:
    """Parse a cron schedule string into a dictionary of arguments for APScheduler's cron trigger.

    Supports standard 5-field cron expressions (minute hour day month day_of_week)
    and 6-field expressions (second minute hour day month day_of_week).

    Args:
        cron_string: The cron schedule string to parse.

    Returns:
        A dictionary containing the cron trigger arguments.
    """
    parts = cron_string.split()
    num_parts = len(parts)

    if num_parts == 5:
        # Standard cron: minute hour day month day_of_week
        return {
            "minute": parts[0],
            "hour": parts[1],
            "day": parts[2],
            "month": parts[3],
            "day_of_week": parts[4],
            "second": "0",
        }
    elif num_parts == 6:
        # Cron with seconds: second minute hour day month day_of_week
        return {
            "second": parts[0],
            "minute": parts[1],
            "hour": parts[2],
            "day": parts[3],
            "month": parts[4],
            "day_of_week": parts[5],
        }
    else:
        raise ValueError(f"Invalid cron schedule string: '{cron_string}'. Expected 5 or 6 fields.")
