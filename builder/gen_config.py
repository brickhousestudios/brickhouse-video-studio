#!/usr/bin/env python3
"""SUB C: generate the EC driver config for block3-line1 FROM the director JSON.
Data (words, groups, motions, tiers, hero, landings, redlight) comes from the
file. Only locked-template defaults live here: baselines, left margin, punch-in
key pattern, effect stack, within-group hero sub-size ratio (320/400 = 0.8).
Pair x-positions are first-pass estimates; the template's ~0.33em ink-gap rule
is enforced by measuring the render and adjusting (the prior rounds' method).

Code-review fixes (Nov 1): the input path is a CLI arg defaulting to the
repo's director_out/block3.json (was a hardcoded /tmp path — not reproducible
from the repo), and landings are keyed by word INDEX (position in the line's
landings list), never by word text, so a repeated word keeps its own landing.
"""
import argparse
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "director_out" / "block3.json"

_parser = argparse.ArgumentParser(
    description="Generate the EC driver config for block3-line1 from a director JSON.")
_parser.add_argument("input", nargs="?", default=None,
                     help="director JSON path (default: director_out/block3.json in this repo)")
_args = _parser.parse_args()

D = json.load(open(_args.input or DEFAULT_INPUT))
LINE = [l for l in D["lines"] if l["line_id"] == "block3-line1"][0]
COMP = "block3_line1_she_said_where_im_from"
OUT = str(Path(os.environ.get("BRICKHOUSE_WORKDIR", "/Volumes/STICK/BrickHouse/lyric-type-2026-10-31")) / "108-lyric-type-block3-director.ecproj")
BASELINES = [280, 500, 890]          # template tier baselines (line 1, read back)
X0 = 120                             # template left margin (layer position x)
SUB_RATIO = 0.8                      # 320 beside 400 (line-1 A/LIGHT precedent)
SPAN_START_SONG_FRAME = 897          # song 29.90s * 30fps
# first-pass x for the 2nd word of a multi-word group (render-measured next),
# keyed by FLAT word index across the line (SHE=0, SAID=1, WHERE=2, I'M=3,
# FROM=4) — by position, not word text, so a repeated word can't collide
PAIR_X = {1: 360, 4: 525}

# landings as an index-keyed list in lyric order (list position == word index)
landings = [x["landing_frame"] - SPAN_START_SONG_FRAME
            for x in LINE["landings"]]
tiers = LINE["size_tiers_px"]
hero = LINE["hero_word"]

def t4(frame):
    return round(frame / 30.0, 4)

ops = []
def op(label, tool, args, hard=False):
    o = {"label": label, "tool": tool, "args": args}
    if hard: o["hard"] = True
    ops.append(o)

op("new_project", "open_project", {"new": True}, hard=True)
op("comp_new", "execute_command",
   {"command": "comp.new", "params": {"name": COMP, "width": 1920, "height": 1080,
                                      "frameRate": 30, "duration": 2.0}}, hard=True)
op("bed_placeholder", "execute_command",
   {"command": "layer.newSolid", "params": {"name": "PLACEHOLDER", "color": "#000000",
                                            "width": 1920, "height": 1080}}, hard=True)

flat = 0
for gi, group in enumerate(LINE["display_groups"]):
    tier = tiers[gi]
    y = BASELINES[gi]
    for wi, word in enumerate(group["words"]):
        size = tier
        if word != hero and hero in group["words"]:
            size = round(tier * SUB_RATIO)
        x = X0 if wi == 0 else PAIR_X[flat]
        lf = landings[flat]
        op(f"t-{word}", "execute_command",
           {"command": "layer.newText",
            "params": {"allCaps": True, "fill": "#FF3B1F", "font": "Anton",
                       "justify": "left", "name": word, "position": [x, y],
                       "size": size, "style": "Regular", "text": word}}, hard=True)
        op(f"{word}-ds", "add_effect", {"effect": "Drop Shadow", "layer": word})
        op(f"{word}-ds-color", "set_property", {"layer": word, "path": "effects/#1/color", "value": [0.02, 0, 0, 1]})
        op(f"{word}-ds-op", "set_property", {"layer": word, "path": "effects/#1/opacity", "value": 88})
        op(f"{word}-ds-dist", "set_property", {"layer": word, "path": "effects/#1/distance", "value": 0})
        op(f"{word}-ds-soft", "set_property", {"layer": word, "path": "effects/#1/softness", "value": 75})
        op(f"{word}-ds-dir", "set_property", {"layer": word, "path": "effects/#1/direction", "value": 135})
        op(f"{word}-grain", "add_effect", {"effect": "Add Grain", "layer": word})
        op(f"{word}-grain-vm", "set_property", {"layer": word, "path": "effects/#2/viewingMode", "value": 2})
        op(f"{word}-op", "add_keyframe",
           {"layer": word, "path": "transform/opacity",
            "keys": [{"time": 0, "value": 0},
                     {"time": t4(lf - 1), "value": 0},
                     {"time": t4(lf), "value": 100}]}, hard=True)
        op(f"{word}-scale", "add_keyframe",
           {"layer": word, "path": "transform/scale",
            "keys": [{"time": 0, "value": [115, 115, 0]},
                     {"time": t4(lf), "value": [115, 115, 0]},
                     {"time": t4(lf + 4), "value": [100, 100, 0]}]}, hard=True)
        flat += 1

op("comp_readback", "get_comp", {"comp": COMP})
op("save", "save_project", {"path": OUT}, hard=True)
json.dump({"ops": ops}, open("/tmp/subc_build.json", "w"), indent=1)
print(f"config written: {len(ops)} ops")
print("sizes:", [(w, (tiers[gi] if w == hero or hero not in g['words'] else round(tiers[gi]*SUB_RATIO)))
                 for gi, g in enumerate(LINE['display_groups']) for w in g['words']])
print("landings (comp frames, lyric order):", landings)
