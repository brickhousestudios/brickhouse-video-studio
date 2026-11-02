#!/usr/bin/env python3
"""Offline tests for punch_hold_keys() (FULL-FRAME PUNCH HOLD as code).

No API calls, no spend, no EC driving: the function must reproduce
the shipped rough-cut-v4 punch keys exactly from the measured word
times, and move the out-point when the measured word-end moves.
Run with the repo venv python:

    python builder/rollout/test_punch_hold.py

Exits 0 when every check passes, 1 otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from build_phase4 import punch_hold_keys  # noqa: E402

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f" -- {detail}"))
    if not cond:
        FAILURES.append(name)


def t4(f):
    return round(f / 30.0, 4)


def keys(spec):
    return [{"time": t4(f), "value": [v, v, 0]} for f, v in spec]


# HEY (comp block2_hey, frame 0 = song 28.00): "hey" measured on the
# bounce -- onset 28.74, end consensus 29.25. Shipped v4: visible
# f20..39 (20 frames), push 108@f20 / 104.8@f24 / 101.9@f29 /
# 100.4@f34 / 100@f39, hard cut @f40.
hey_out, hey_keys = punch_hold_keys(28.74, 29.25, 30, 28.00)
check("HEY: out_frame is the f40 cut", hey_out == 40, str(hey_out))
check("HEY: 20 frames on screen", hey_out - 20 == 20, str(hey_out))
check("HEY: scale keys reproduce v4 exactly",
      hey_keys == keys([(20, 108), (24, 104.8), (29, 101.9),
                        (34, 100.4), (39, 100)]),
      str(hey_keys))

# WAY (comp block3_cue4_no_way, frame 0 = song 33.10): "way"
# measured on the bounce -- onset 36.12, end consensus 36.66.
# Shipped v4: visible f89..108 (20 frames), push 108@f89 /
# 104.1@f94 / 101.5@f99 / 100.3@f104 / 100@f108, hard cut @f109.
way_out, way_keys = punch_hold_keys(36.12, 36.66, 30, 33.10)
check("WAY: out_frame is the f109 cut", way_out == 109, str(way_out))
check("WAY: 20 frames on screen", way_out - 89 == 20, str(way_out))
check("WAY: scale keys reproduce v4 exactly",
      way_keys == keys([(89, 108), (94, 104.1), (99, 101.5),
                        (104, 100.3), (108, 100)]),
      str(way_keys))

# A different measured word-end must move the out-point: +0.3s of
# sung word on the HEY inputs lands the cut 9 frames later (@f49).
late_out, _late_keys = punch_hold_keys(28.74, 29.25 + 0.3, 30, 28.00)
check("different word-end gives a different out-point",
      late_out != hey_out and late_out == 49,
      str((hey_out, late_out)))

if FAILURES:
    print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("\nALL PUNCH-HOLD TESTS PASS")
