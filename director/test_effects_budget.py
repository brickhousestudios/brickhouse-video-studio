#!/usr/bin/env python3
"""Offline tests for the director effects budget (BO, locked 2026-11-01).

No API calls, no spend: exercises validate()'s rejection rules
(repeated hero in a block, more than one motif/scatter claim, scatter
claimed without motif, motif claimed without
redlight) and the deterministic add_effects() annotation
against synthetic candidates and the committed block-3 JSONs.
Run with the repo venv python:

    python director/test_effects_budget.py

Exits 0 when every check passes, 1 otherwise.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import director  # noqa: E402
from director import add_effects, add_hero_color, validate  # noqa: E402
import cue4_director  # noqa: E402

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f" -- {detail}"))
    if not cond:
        FAILURES.append(name)


def line(line_id, groups, tiers, hero, placement):
    return {
        "line_id": line_id,
        "display_groups": [{"words": w, "motion": m} for w, m in groups],
        "placement": placement,
        "hero_word": hero,
        "size_tiers_px": tiers,
        "redlight": False,
        "reason": "test line",
    }


# Synthetic target: RED appears twice so a hero CAN repeat across lines.
SYNTH = {
    "block_id": "synth",
    "words": [
        {"word": "RED", "onset_s": 1.0},
        {"word": "BLUE", "onset_s": 2.0},
        {"word": "RED", "onset_s": 3.0},
        {"word": "GREEN", "onset_s": 4.0},
    ],
}


def base_lines():
    return [
        line("s-line1", [(["RED"], "punch_in"), (["BLUE"], "punch_in")],
             [400, 150], "RED", "left"),
        line("s-line2", [(["RED"], "punch_in"), (["GREEN"], "punch_in")],
             [150, 400], "GREEN", "right"),
    ]


# ---------------------------------------------------------- validate rules
errs = validate({"lines": base_lines()}, SYNTH)
check("baseline candidate validates clean", errs == [], str(errs))

cand = base_lines()
cand[1]["hero_word"] = "RED"
cand[1]["size_tiers_px"] = [400, 150]
errs = validate({"lines": cand}, SYNTH)
check("repeated hero in block rejected",
      any("repeats an earlier hero" in e for e in errs) and len(errs) == 1,
      str(errs))

cand = base_lines()
cand[0]["motif"] = True
cand[0]["redlight"] = True
cand[1]["motif"] = True
cand[1]["redlight"] = True
errs = validate({"lines": cand}, SYNTH)
check("two motif claims in a block rejected",
      any("at most ONE line per block" in e for e in errs) and len(errs) == 1,
      str(errs))

cand = base_lines()
cand[0]["scatter"] = True
errs = validate({"lines": cand}, SYNTH)
check("scatter claimed without motif rejected",
      any("scatter claimed without motif" in e for e in errs) and len(errs) == 1,
      str(errs))

cand = base_lines()
cand[0]["motif"] = True
errs_off = validate({"lines": cand}, SYNTH)
cand[0]["redlight"] = True
errs_on = validate({"lines": cand}, SYNTH)
check("motif scatter only on a redlight line",
      "line 0 (s-line1): motif scatter only on a redlight line" in errs_off
      and "line 0 (s-line1): motif scatter only on a redlight line" not in errs_on,
      str((errs_off, errs_on)))

cand = base_lines()
cand[0]["motif"] = True
cand[0]["redlight"] = True
errs = validate({"lines": cand}, SYNTH, prior_scatter_used=True)
check("motif claim after prior scatter rejected",
      any("at most ONE line per block" in e for e in errs) and len(errs) == 1,
      str(errs))

single = [line("s-only",
               [(["RED"], "punch_in"), (["BLUE"], "punch_in"),
                (["RED"], "punch_in"), (["GREEN"], "punch_in")],
               [400, 150, 230, 320], "RED", "left")]
errs = validate({"lines": single}, SYNTH, prior_heroes=["RED"])
check("hero repeating a PRIOR line of the block rejected",
      any("repeats an earlier hero" in e for e in errs) and len(errs) == 1,
      str(errs))
errs = validate({"lines": single}, SYNTH, prior_heroes=["BLUE"])
check("same candidate clean with unrelated prior heroes", errs == [], str(errs))

# --------------------------------------------- placement rotation rule
def rot_lines(placements):
    """One display line per placement over synthetic word pairs; a
    'full' line takes a single word in a full_frame_punch group."""
    words = ["AA", "BB", "CC", "DD", "EE", "FF", "GG", "HH", "II"]
    lines, pos = [], 0
    for i, placement in enumerate(placements):
        if placement == "full":
            lines.append(line(f"r-line{i + 1}",
                              [([words[pos]], "full_frame_punch")],
                              [1250], words[pos], "full"))
            pos += 1
        else:
            pair = words[pos:pos + 2]
            lines.append(line(f"r-line{i + 1}",
                              [(pair[:1], "punch_in"), (pair[1:], "punch_in")],
                              [400, 150], pair[0], placement))
            pos += 2
    return lines


def rot_target(lines):
    words = [w for l in lines for g in l["display_groups"] for w in g["words"]]
    return {"block_id": "rot",
            "words": [{"word": w, "onset_s": float(i + 1)}
                      for i, w in enumerate(words)]}


ROT_MSG = "more than 2 consecutive lines without a full-frame placement"
ls = rot_lines(["left", "right", "left"])
errs = validate({"lines": ls}, rot_target(ls))
check("rotation: 3 stacks in a row rejected",
      any(ROT_MSG in e for e in errs) and len(errs) == 1, str(errs))
check("rotation: error tagged at the 3rd stack line",
      any(e.startswith("line 2 (r-line3):") for e in errs), str(errs))
ls = rot_lines(["left", "right", "full"])
errs = validate({"lines": ls}, rot_target(ls))
check("rotation: full-frame at line 3 is clean", errs == [], str(errs))
ls = rot_lines(["left", "right", "full", "left", "right"])
errs = validate({"lines": ls}, rot_target(ls))
check("rotation: stack stack full stack stack is clean",
      errs == [], str(errs))
one_stack = [line("r-only", [(["AA"], "punch_in"), (["BB"], "punch_in")],
                  [400, 150], "AA", "left")]
errs = validate({"lines": one_stack}, rot_target(one_stack),
                prior_stack_streak=2)
check("rotation: prior stack streak chains into the candidate",
      any(ROT_MSG in e for e in errs) and len(errs) == 1, str(errs))
one_full = [line("r-only", [(["AA"], "full_frame_punch")], [1250], "AA", "full")]
errs = validate({"lines": one_full}, rot_target(one_full),
                prior_stack_streak=2)
check("rotation: full-frame line clears a prior streak",
      errs == [], str(errs))

# ------------------------------------------------- cue4 prior-block wiring
cue4_cand = {"lines": [
    line("block3-line3",
         [(["THEN", "I", "ASKED"], "punch_in"), (["WHERE", "SHE"], "punch_in"),
          (["FROM"], "stack_build")],
         [150, 230, 400], "FROM", "left"),
    line("block3-line4",
         [(["SHE", "SAID"], "punch_in"), (["NO"], "punch_in")],
         [150, 400], "NO", "right"),
    line("block3-line5", [(["WAY"], "full_frame_punch")], [1250], "WAY", "full"),
]}
errs = cue4_director.validate_cue4(cue4_cand, cue4_director.TARGET)
check("cue4: FROM hero rejected (repeats block3-line1 via prior block)",
      any("repeats an earlier hero" in e for e in errs) and len(errs) == 1,
      str(errs))
ok_cand = copy.deepcopy(cue4_cand)
ok_cand["lines"][0]["hero_word"] = "ASKED"
ok_cand["lines"][0]["size_tiers_px"] = [400, 230, 150]
errs = cue4_director.validate_cue4(ok_cand, cue4_director.TARGET)
check("cue4: fresh-hero candidate validates clean", errs == [], str(errs))

# ------------------------------------------------------ annotation derive
raw = base_lines()
raw[0]["motif"] = True
raw[0]["redlight"] = True
raw[1]["motif"] = True
raw[1]["redlight"] = True
out = add_effects(raw)
check("first motif line gets the scatter",
      out[0]["effects"] == {"scatter": True, "hero_demoted": False},
      str(out[0]["effects"]))
check("second motif claim gets no scatter",
      out[1]["effects"] == {"scatter": False, "hero_demoted": False},
      str(out[1]["effects"]))
check("no motif anywhere -> no scatter",
      all(l["effects"]["scatter"] is False for l in add_effects(base_lines())))

raw = base_lines()
raw[0]["motif"] = True
out_off = add_effects(raw)
raw = base_lines()
raw[0]["motif"] = True
raw[0]["redlight"] = True
out_on = add_effects(raw)
check("backstop: scatter requires motif AND redlight (slot free)",
      out_off[0]["effects"]["scatter"] is False
      and out_on[0]["effects"]["scatter"] is True,
      str((out_off[0]["effects"], out_on[0]["effects"])))

raw = base_lines()
raw[1]["hero_word"] = "RED"
out = add_effects(raw)
check("repeated hero demoted by annotation",
      out[1]["effects"] == {"scatter": False, "hero_demoted": True},
      str(out[1]["effects"]))
check("demoted hero_color record shape",
      out[1]["hero_color"] == {
          "hero_word": None,
          "hero_fill": director.HERO_FILL,
          "others_fill": director.OTHERS_FILL,
          "demoted_from": "RED",
          "reason": "repeat_hero_in_block",
      }, str(out[1]["hero_color"]))
check("first hero untouched by demotion",
      out[0]["hero_color"]["hero_word"] == "RED"
      and out[0]["effects"]["hero_demoted"] is False)

# ------------------------------------------- committed block-3 documents
d1 = json.loads((ROOT / "director" / "block3-director.json").read_text())
d2 = json.loads((ROOT / "director" / "block3-cue4-director.json").read_text())


def strip_records(lines):
    return [{k: v for k, v in l.items() if k not in ("hero_color", "effects")}
            for l in lines]


rebuilt_12 = add_effects(add_hero_color(strip_records(d1["lines"])))
check("lines 1-2: strip + re-annotate reproduces the committed lines",
      rebuilt_12 == d1["lines"]
      and json.dumps(rebuilt_12) == json.dumps(d1["lines"]))
prior_heroes = [l["hero_word"] for l in d1["lines"]]
rebuilt_345 = add_effects(add_hero_color(strip_records(d2["lines"])),
                          prior_heroes=prior_heroes)
check("lines 3-5: strip + re-annotate (prior block) reproduces committed",
      rebuilt_345 == d2["lines"]
      and json.dumps(rebuilt_345) == json.dumps(d2["lines"]))

expected = [
    ("block3-line1", "FROM", False),
    ("block3-line2", "AROUND", False),
    ("block3-line3", None, True),   # FROM repeats line 1 -> demoted
    ("block3-line4", "NO", False),
    ("block3-line5", "WAY", False),
]
for l, (lid, hero, demoted) in zip(d1["lines"] + d2["lines"], expected):
    check(f"{lid}: hero kept/demoted as expected, no scatter",
          l["line_id"] == lid
          and l["hero_color"]["hero_word"] == hero
          and l["effects"] == {"scatter": False, "hero_demoted": demoted},
          str((l["hero_color"], l["effects"])))
check("line3 demotion carries demoted_from + reason",
      d2["lines"][0]["hero_color"].get("demoted_from") == "FROM"
      and d2["lines"][0]["hero_color"].get("reason") == "repeat_hero_in_block")

errs = validate({"lines": copy.deepcopy(d1["lines"])}, director.TARGETS["block3"])
check("committed block3 lines validate clean", errs == [], str(errs))
errs = validate({"lines": copy.deepcopy(d2["lines"])}, cue4_director.TARGET,
                prior_heroes=prior_heroes)
# The committed cue4 lines predate the budget: as a fresh candidate they
# draw exactly ONE error -- the repeat-hero rejection (the repair loop
# would make the model re-pick). Their renderer records still match
# the deterministic derivation exactly (no record-mismatch errors):
# the demotion backstop is what carries them.
check("committed cue4 lines: only the repeat-hero rejection fires",
      len(errs) == 1 and "repeats an earlier hero" in errs[0], str(errs))

bad = copy.deepcopy(d2["lines"])
bad[2]["effects"] = {"scatter": True, "hero_demoted": False}
errs = validate({"lines": bad}, cue4_director.TARGET, prior_heroes=prior_heroes)
check("tampered effects record rejected",
      any("effects" in e and "does not match" in e for e in errs), str(errs))
bad = copy.deepcopy(d1["lines"])
bad[0]["hero_color"] = dict(bad[0]["hero_color"], hero_fill="#00FF00")
errs = validate({"lines": bad}, director.TARGETS["block3"])
check("tampered hero_color rejected (step-a regression)",
      any("hero_color" in e and "does not match" in e for e in errs), str(errs))

if FAILURES:
    print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("\nALL EFFECTS-BUDGET TESTS PASS")
