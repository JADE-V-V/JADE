"""Small format helpers for the external ACTINV scalar CLI."""

from __future__ import annotations

import math
import re


def schedule_endpoints(schedule: list[dict]) -> list[tuple[float, float]]:
    """Return elapsed seconds and flux multipliers from ACTINV duration strings.

    Mirrors actinv-spec-1 duration syntax: ASCII numbers, optional scientific
    notation, and seconds/minutes/hours/days/Julian years (365.25 days).
    The compatibility controls live in tests/helper/test_actinv.py.
    """
    units = {
        "": 1,
        "s": 1,
        "sec": 1,
        "secs": 1,
        "second": 1,
        "seconds": 1,
        "m": 60,
        "min": 60,
        "mins": 60,
        "minute": 60,
        "minutes": 60,
        "h": 3600,
        "hr": 3600,
        "hrs": 3600,
        "hour": 3600,
        "hours": 3600,
        "d": 86400,
        "day": 86400,
        "days": 86400,
        "y": 31557600,
        "yr": 31557600,
        "yrs": 31557600,
        "year": 31557600,
        "years": 31557600,
    }
    if not isinstance(schedule, list) or not schedule:
        raise ValueError("ACTINV schedule must contain at least one step")
    time = 0.0
    endpoints = []
    for step in schedule:
        duration_text = step["dt"]
        if not isinstance(duration_text, str):
            raise TypeError("ACTINV schedule duration must be a string")
        duration_text = duration_text.strip()
        if len(duration_text.encode("utf-8")) > 64:
            raise ValueError("ACTINV duration exceeds the CLI's 64-byte limit")
        match = re.fullmatch(
            r"([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
            r"(?:[eE][+-]?[0-9]+)?)\s*([a-zA-Z]*)",
            duration_text,
        )
        if match is None or match[2].lower() not in units:
            raise ValueError(f"Unsupported ACTINV duration: {step['dt']}")
        duration = float(match[1]) * units[match[2].lower()]
        flux = step["flux"]
        if (
            not math.isfinite(duration)
            or duration <= 0
            or isinstance(flux, bool)
            or not isinstance(flux, (int, float))
            or not math.isfinite(flux)
            or flux < 0
        ):
            raise ValueError("Invalid ACTINV schedule duration or flux")
        previous = time
        time += duration
        if not math.isfinite(time) or time <= previous:
            raise ValueError("ACTINV schedule has unresolvable or nonfinite endpoints")
        endpoints.append((time, flux))
    return endpoints
