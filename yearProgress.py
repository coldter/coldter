#!/usr/bin/env python3
"""Render the yearly-progress banner.

A Python port of the original yearProgress.js, kept byte-for-byte compatible
with its output (used by build_readme.py via yearProgress.txt).
"""

import sys
from datetime import datetime, timezone

# JavaScript's Date.prototype.toUTCString() always emits English abbreviations
# regardless of the host locale, so they are hardcoded here to match exactly.
DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

PROGRESS_BAR_CAPACITY = 30


def to_utc_string(dt: datetime) -> str:
    """Mirror JavaScript's Date.prototype.toUTCString()."""
    dt = dt.astimezone(timezone.utc)
    # Python's weekday() is Mon=0..Sun=6; JS getUTCDay() is Sun=0..Sat=6.
    day_name = DAY_NAMES[(dt.weekday() + 1) % 7]
    month_name = MONTH_NAMES[dt.month - 1]
    return (
        f"{day_name}, {dt.day:02d} {month_name} {dt.year} "
        f"{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d} GMT"
    )


def main() -> None:
    now = datetime.now(timezone.utc)
    this_year = now.year

    # NB: the end of year is 23:59:59 on Dec 31, matching the original script
    # (one second short of a full year), so the denominator is intentional.
    start_of_year = datetime(this_year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    end_of_year = datetime(this_year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

    progress = (now.timestamp() - start_of_year.timestamp()) / (
        end_of_year.timestamp() - start_of_year.timestamp()
    )

    # parseInt() truncates toward zero; int() does the same for progress >= 0.
    passed = int(progress * PROGRESS_BAR_CAPACITY)
    bar = "█" * passed + "▁" * (PROGRESS_BAR_CAPACITY - passed)
    progress_bar = f"( {bar} )"

    output = (
        f"⏳ Year progress {progress_bar} {progress * 100:.2f} %\n\n"
        f"⏰ Updated on {to_utc_string(now)}"
    )

    # Write UTF-8 bytes directly (+ trailing newline) so the emoji and
    # box-drawing characters survive any locale, mirroring Node's console.log.
    sys.stdout.buffer.write((output + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
