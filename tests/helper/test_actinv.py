"""Duration compatibility controls for the external ACTINV scalar CLI."""

from __future__ import annotations

import pytest

from jade.helper.actinv import schedule_endpoints


# These controls follow actinv-spec-1 and ACTINV's parse_duration/Spec::validate
# in crates/actinv-core/src/spec.rs. Keep them aligned when the CLI format changes.
# JADE's tests do not require ACTINV or nuclear data to be installed.
@pytest.mark.parametrize(
    "duration,seconds",
    [
        ("300 s", 300),
        ("300s", 300),
        ("5 min", 300),
        ("5min", 300),
        ("0.08333333333333333 h", 300),
        ("  +5 MINUTES  ", 300),
        ("3e2", 300),
        ("1e-8 s", 1e-8),
        ("2.5E+3sec", 2500),
        (".5 hr", 1800),
        ("1. days", 86400),
        ("1 y", 31557600),
        ("1 years", 31557600),
        ("0" * 63 + "1", 1),
        ("  " + "0" * 63 + "1  ", 1),
    ],
)
def test_cli_duration_compatibility(duration, seconds):
    [(elapsed, flux)] = schedule_endpoints([{"dt": duration, "flux": 1}])
    assert elapsed == pytest.approx(seconds, rel=1e-14, abs=0)
    assert flux == 1


@pytest.mark.parametrize(
    "duration",
    [
        "0 s",
        "-1 s",
        "nan s",
        "inf s",
        "1e309 s",
        "1e308 years",
        "2.5E+3ms",
        "1 fortnight",
        "3e",
        "٣٠٠ s",
        "0" * 64 + "1",
    ],
)
def test_cli_invalid_duration_rejected(duration):
    with pytest.raises(ValueError):
        schedule_endpoints([{"dt": duration, "flux": 1}])


@pytest.mark.parametrize("duration", [None, 300])
def test_duration_requires_string(duration):
    with pytest.raises(TypeError):
        schedule_endpoints([{"dt": duration, "flux": 1}])


def test_mixed_units_accumulate_elapsed_time():
    assert schedule_endpoints(
        [{"dt": "5min", "flux": 1}, {"dt": "1.1 min", "flux": 0}]
    ) == [(300, 1), (366, 0)]
