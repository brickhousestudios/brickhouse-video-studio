#!/usr/bin/env python3
"""Phase 3 (effects budget, BO verdict on v2): build block2-v6 and
block3-take2-v5. Same concept template as Phase 2 (non-hero off-white
#F2EDE4 + G3 stacked shadow, headers, heroes red) with the scatter
budget cut: NO per-char assembles anywhere in these units (LIGHT in
line 1 keeps the only scatter; line-1 + comp-B segments are reused
from v2 at assembly). Changes vs build_phase2.py:
- WINDOW: wipe pinned to 0 (as v2) but NO assemble — instead the
  standard punch-in scale keys mirrored from SHE's template keys:
  [115]@0, [115]@landing f49, [100]@f53 (its opacity step at f49
  already exists in the v4 base). Red, hard cut out (comp cut).
- FROM (L1) / AROUND (L2): no assemble — the take2-v3 base punch-in
  stands untouched.
- FROM_L0_1 (cue 4): DEMOTED to off-white + G3 (white_treatment);
  its base punch-in stands; no assemble.
Emits EC driver configs: build-b2-v3.json, build-b3-v3.json,
render-b2-v3.json (comp A only — comp B reused), render-b3-v3.json.
"""
import json
import os
from pathlib import Path

HERE = Path(__file__).parent
M2 = os.environ.get("BRICKHOUSE_WORKDIR", "/Volumes/STICK/BrickHouse/lyric-type-2026-10-31")
OW = "#F2EDE4"
HDR = "DRIZZZ  \u2022  108  \u2022  BRICKHOUSE STUDIOS"

def t4(f):
    return round(f / 30.0, 4)

class Cfg:
    def __init__(self):
        self.ops = []
    def op(self, label, tool, args, hard=False):
        o = {"label": label, "tool": tool, "args": args}
        if hard:
            o["hard"] = True
        self.ops.append(o)
    def cmd(self, label, command, params, hard=False):
        self.op(label, "execute_command", {"command": command, "params": params}, hard)
    def open_comp(self, comp):
        self.cmd(f"open-{comp[:12]}", "comp.open", {"comp": comp}, hard=True)

def white_treatment(cfg, layer, stack_idx, tag):
    """Recolor off-white + G3 shadow: #1 opacity -> 100, stacked 2nd shadow."""
    cfg.cmd(f"{tag}-fill", "layer.setText", {"layer": layer, "fill": OW}, hard=True)
    cfg.op(f"{tag}-ds1op", "set_property", {"layer": layer, "path": "effects/#1/opacity", "value": 100})
    cfg.op(f"{tag}-addds", "add_effect", {"effect": "Drop Shadow", "layer": layer})
    p = f"effects/#{stack_idx}"
    cfg.op(f"{tag}-ds2-color", "set_property", {"layer": layer, "path": f"{p}/color", "value": [0.02, 0, 0, 1]})
    cfg.op(f"{tag}-ds2-op", "set_property", {"layer": layer, "path": f"{p}/opacity", "value": 85})
    cfg.op(f"{tag}-ds2-dist", "set_property", {"layer": layer, "path": f"{p}/distance", "value": 0})
    cfg.op(f"{tag}-ds2-soft", "set_property", {"layer": layer, "path": f"{p}/softness", "value": 180})
    cfg.op(f"{tag}-ds2-dir", "set_property", {"layer": layer, "path": f"{p}/direction", "value": 135})

def header(cfg, tag):
    cfg.cmd(f"{tag}-header", "layer.newText",
            {"text": HDR, "name": "HEADER", "position": [122, 54], "font": "Anton",
             "style": "Regular", "size": 30, "fill": OW, "allCaps": True,
             "justify": "left", "tracking": 200}, hard=True)
    cfg.op(f"{tag}-header-op", "set_property", {"layer": "HEADER", "path": "transform/opacity", "value": 55}, hard=True)
    cfg.cmd(f"{tag}-rule", "layer.newSolid", {"name": "HEADER-RULE", "color": OW, "width": 1676, "height": 2}, hard=True)
    cfg.op(f"{tag}-rule-pos", "set_property", {"layer": "HEADER-RULE", "path": "transform/position", "value": [960, 67, 0]}, hard=True)
    cfg.op(f"{tag}-rule-op", "set_property", {"layer": "HEADER-RULE", "path": "transform/opacity", "value": 55}, hard=True)

# ---------------------------------------------------------------- block 2
def build_b2():
    cfg = Cfg()
    cfg.op("open", "open_project", {"path": "/tmp/b2-base.ecproj"}, hard=True)
    cfg.open_comp("block2_she_pulled_down_the_window")
    for w, idx in (("SHE", 3), ("PULLED", 3), ("DOWN", 4), ("THE", 4)):
        white_treatment(cfg, w, idx, f"A-{w}")
    # WINDOW: wipe neutralized (completion pinned to 0, as v2), then the
    # standard punch-in: scale keys mirrored from SHE's template keys
    # ([115]@0 hold, [115]@landing, [100]@landing+4). Opacity step at
    # f49 already exists in the v4 base. No animators. Red stays red.
    cfg.cmd("A-WINDOW-wipe49", "keys.set", {"layer": "WINDOW", "path": "effects/#3/completion",
            "time": t4(49), "value": 0}, hard=True)
    cfg.cmd("A-WINDOW-wipe58", "keys.set", {"layer": "WINDOW", "path": "effects/#3/completion",
            "time": t4(58), "value": 0}, hard=True)
    cfg.op("A-WINDOW-scale", "add_keyframe", {"layer": "WINDOW", "path": "transform/scale", "keys": [
        {"time": 0, "value": [115, 115, 0]},
        {"time": t4(49), "value": [115, 115, 0]},
        {"time": t4(53), "value": [100, 100, 0]}]}, hard=True)
    header(cfg, "A")
    cfg.open_comp("block2_hey")
    for w in ("I", "SAID"):
        white_treatment(cfg, w, 3, f"B-{w}")
    header(cfg, "B")
    cfg.op("save", "save_project", {"path": f"{M2}/108-lyric-type-block2-v6.ecproj"}, hard=True)
    json.dump({"ops": cfg.ops}, open(HERE / "build-b2-v3.json", "w"), indent=1)
    print("build-b2-v3:", len(cfg.ops), "ops")

def render_b2():
    cfg = Cfg()
    cfg.op("open", "open_project", {"path": f"{M2}/108-lyric-type-block2-v6.ecproj"}, hard=True)
    for f in range(75):
        cfg.op(f"b2a3-r{f:03d}", "render_frame",
               {"comp": "block2_she_pulled_down_the_window", "time": t4(f),
                "path": f"/tmp/b2a3/f{f:03d}.png", "max_side": 1920})
    json.dump({"ops": cfg.ops}, open(HERE / "render-b2-v3.json", "w"), indent=1)
    print("render-b2-v3:", len(cfg.ops), "ops")

# ---------------------------------------------------------------- block 3
def build_b3():
    cfg = Cfg()
    cfg.op("open", "open_project", {"path": "/tmp/b3-base.ecproj"}, hard=True)
    cfg.open_comp("block3_line1_she_said_where_im_from")
    for w in ("SHE", "SAID", "WHERE", "I'M"):
        white_treatment(cfg, w, 3, f"L1-{w}")
    # FROM (L1): hero red, base punch-in untouched, NO assemble.
    header(cfg, "L1")
    cfg.open_comp("block3_line2_i_told_her_im_not_around")
    for w in ("I", "TOLD", "HER", "I'M", "NOT"):
        white_treatment(cfg, w, 3, f"L2-{w}")
    # AROUND: hero red, base punch-in untouched, NO assemble/break.
    header(cfg, "L2")
    cfg.open_comp("block3_cue4_no_way")
    for w in ("THEN_L0_1", "I_L0_1", "ASKED_L0_1", "WHERE_L0_1", "SHE_L0_1", "SHE_L1_2", "SAID_L1_1"):
        white_treatment(cfg, w, 3, f"C4-{w}")
    # FROM_L0_1: DEMOTED (repeat-hero budget) -> off-white + G3.
    white_treatment(cfg, "FROM_L0_1", 3, "C4-FROM")
    header(cfg, "C4")
    cfg.op("save", "save_project", {"path": f"{M2}/108-lyric-type-block3-take2-v5.ecproj"}, hard=True)
    json.dump({"ops": cfg.ops}, open(HERE / "build-b3-v3.json", "w"), indent=1)
    print("build-b3-v3:", len(cfg.ops), "ops")

def render_b3():
    cfg = Cfg()
    cfg.op("open", "open_project", {"path": f"{M2}/108-lyric-type-block3-take2-v5.ecproj"}, hard=True)
    for comp, n, tag in (("block3_line1_she_said_where_im_from", 60, "b3l13"),
                         ("block3_line2_i_told_her_im_not_around", 48, "b3l23"),
                         ("block3_cue4_no_way", 108, "b3c43")):
        for f in range(n):
            cfg.op(f"{tag}-r{f:03d}", "render_frame",
                   {"comp": comp, "time": t4(f), "path": f"/tmp/{tag}/f{f:03d}.png", "max_side": 1920})
    json.dump({"ops": cfg.ops}, open(HERE / "render-b3-v3.json", "w"), indent=1)
    print("render-b3-v3:", len(cfg.ops), "ops")

if __name__ == "__main__":
    build_b2()
    render_b2()
    build_b3()
    render_b3()
