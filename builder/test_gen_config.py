#!/usr/bin/env python3
"""Assert-based tests for builder/gen_config.py (plain python3, no framework).

Covers the Nov 1 code-review fixes:
  1. REPEATED WORDS: landings are keyed by word index, so a line that repeats
     a word keeps BOTH landings at their own distinct frames (the old
     word-text-keyed dict silently dropped the earlier one).
  2. REAL LINE UNCHANGED: block3-line1 from director_out/block3.json still
     lands SHE/SAID/WHERE/I'M/FROM at song frames 906/912/923/930/938.

Run from anywhere:  python3 builder/test_gen_config.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "gen_config.py"
REAL_INPUT = HERE.parent / "director_out" / "block3.json"
BUILD_OUT = Path("/tmp/subc_build.json")
SPAN = 897  # gen_config's SPAN_START_SONG_FRAME


def t4(frame):
    return round(frame / 30.0, 4)


def run_gen(input_path):
    r = subprocess.run([sys.executable, str(SCRIPT), str(input_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"gen_config failed: {r.stderr}"
    return json.loads(BUILD_OUT.read_text())["ops"]


def landing_times(ops, layer):
    """Times at which a layer's opacity keyframes hit 100 (its landings)."""
    out = []
    for o in ops:
        if (o["tool"] == "add_keyframe" and o["args"].get("layer") == layer
                and o["args"].get("path") == "transform/opacity"):
            out += [k["time"] for k in o["args"]["keys"] if k["value"] == 100]
    return out


# --- test 1: a repeated word keeps both landings, each at its own frame ---
synth = {"lines": [{
    "line_id": "block3-line1",
    "display_groups": [
        {"words": ["HEY", "HEY"], "motion": "punch_in"},
        {"words": ["GO"], "motion": "punch_in"},
        {"words": ["STOP"], "motion": "stack_build"}],
    "size_tiers_px": [150, 230, 400],
    "hero_word": "STOP",
    "redlight": False,
    "landings": [
        {"word": "HEY", "landing_frame": 1000},
        {"word": "HEY", "landing_frame": 1040},
        {"word": "GO", "landing_frame": 1100},
        {"word": "STOP", "landing_frame": 1160}]}]}
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump(synth, f)
    synth_path = f.name
ops = run_gen(synth_path)
hey = landing_times(ops, "HEY")
assert hey == [t4(1000 - SPAN), t4(1040 - SPAN)], \
    f"repeated word lost a landing: {hey}"
assert landing_times(ops, "GO") == [t4(1100 - SPAN)]
assert landing_times(ops, "STOP") == [t4(1160 - SPAN)]
print("PASS repeated-word: both HEY landings survive "
      "(comp frames 103 and 143, distinct)")

# --- test 2: the real block-3 line 1 is unchanged ---
ops = run_gen(REAL_INPUT)
expect = {"SHE": 906, "SAID": 912, "WHERE": 923, "I'M": 930, "FROM": 938}
for word, song_frame in expect.items():
    got = landing_times(ops, word)
    assert got == [t4(song_frame - SPAN)], \
        f"{word}: got {got}, want song frame {song_frame}"
print("PASS real-line: block3-line1 landings at song frames "
      "906/912/923/930/938")
print("ALL TESTS PASS")
