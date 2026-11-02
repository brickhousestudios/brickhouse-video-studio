#!/usr/bin/env python3
"""Probe block2-v4 and block3-v3 projects: comp/layer inventories.
Emits two driver configs (probe-b2.json, probe-b3.json) next to this file."""
import json
import os
from pathlib import Path

HERE = Path(__file__).parent
M2 = os.environ.get("BRICKHOUSE_WORKDIR", "/Volumes/STICK/BrickHouse/lyric-type-2026-10-31")

def cfg(ops):
    return {"ops": ops}

def op(ops, label, tool, args, hard=False):
    o = {"label": label, "tool": tool, "args": args}
    if hard:
        o["hard"] = True
    ops.append(o)

# ---- block 2 v4
ops = []
op(ops, "open", "open_project", {"path": f"{M2}/108-lyric-type-block2-v4.ecproj"}, hard=True)
for comp in ("block2_she_pulled_down_the_window", "block2_hey"):
    op(ops, f"open-{comp}", "execute_command", {"command": "comp.open", "params": {"comp": comp}}, hard=True)
    op(ops, f"comp-{comp}", "get_comp", {"comp": comp})
    for layer in ("SHE", "PULLED", "DOWN", "THE", "WINDOW", "I", "SAID", "HEY"):
        op(ops, f"layer-{comp}-{layer}", "get_layer", {"layer": layer})
json.dump(cfg(ops), open(HERE / "probe-b2.json", "w"), indent=1)

# ---- block 3 v3
ops = []
op(ops, "open", "open_project", {"path": f"{M2}/108-lyric-type-block3-take2-v3.ecproj"}, hard=True)
for comp in ("block3_line1_she_said_where_im_from", "block3_line2_i_told_her_im_not_around", "block3_cue4_no_way"):
    op(ops, f"open-{comp}", "execute_command", {"command": "comp.open", "params": {"comp": comp}}, hard=True)
    op(ops, f"comp-{comp}", "get_comp", {"comp": comp})
json.dump(cfg(ops), open(HERE / "probe-b3.json", "w"), indent=1)
print("probe configs written")
