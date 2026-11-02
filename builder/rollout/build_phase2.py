#!/usr/bin/env python3
"""Phase 2: concept-template re-render builds for block 2 (v5) and block 3
(take2-v4). Emits EC driver configs: build-b2.json, build-b3.json,
render-b2.json, render-b3.json.

Concept template (locked): non-hero words off-white #F2EDE4 + Phase-1
white shadow treatment (Drop Shadow #1 opacity 88->100 plus a SECOND
stacked Drop Shadow opacity 85 / softness 180); stack heroes red +
per-char scatter-assemble (animator keys: full offsets @open, 12%
@land-1, 0 @land, 0 @hold, exit offsets @exit) with the punch scale
flattened and the opacity step moved to the assemble-open frame;
header strip in every comp (alt's exact ops)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import workdir  # noqa: E402

HERE = Path(__file__).parent
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

def assemble(cfg, layer, letters, open_f, land_f, hold_f, exit_f, tag, has_scale=True):
    """letters: list of (assemble_pos, assemble_rot, exit_pos, exit_rot)."""
    # opacity step moves to the assemble-open frame (hold key first)
    cfg.cmd(f"{tag}-op-hold", "keys.set", {"layer": layer, "path": "transform/opacity",
            "time": t4(land_f - 1), "newTime": t4(open_f - 1)}, hard=True)
    cfg.cmd(f"{tag}-op-step", "keys.set", {"layer": layer, "path": "transform/opacity",
            "time": t4(land_f), "newTime": t4(open_f)}, hard=True)
    if has_scale:
        cfg.cmd(f"{tag}-sc0", "keys.set", {"layer": layer, "path": "transform/scale",
                "time": 0, "value": [100, 100, 0]}, hard=True)
        cfg.cmd(f"{tag}-scl", "keys.set", {"layer": layer, "path": "transform/scale",
                "time": t4(land_f), "value": [100, 100, 0]}, hard=True)
    n = len(letters)
    for k, (A, rA, E, rE) in enumerate(letters):
        seg = "animator" if k == 0 else f"animator#{k + 1}"
        base = f"text/animators/{seg}"
        cfg.cmd(f"{tag}-anim{k}", "layer.addTextAnimator",
                {"layer": layer, "properties": ["position", "rotation"], "name": f"ASM_{tag}_{k}"}, hard=True)
        cfg.op(f"{tag}-sel{k}s", "set_property", {"layer": layer, "path": f"{base}/selectors/rangeSelector/start",
               "value": round(100 * k / n, 2)}, hard=True)
        cfg.op(f"{tag}-sel{k}e", "set_property", {"layer": layer, "path": f"{base}/selectors/rangeSelector/end",
               "value": round(100 * (k + 1) / n, 2)}, hard=True)
        cfg.op(f"{tag}-sel{k}sm", "set_property", {"layer": layer, "path": f"{base}/selectors/rangeSelector/advanced/smoothness",
               "value": 0}, hard=True)
        a12 = [round(A[0] * 0.12), round(A[1] * 0.12), 0]
        cfg.op(f"{tag}-pos{k}", "add_keyframe", {"layer": layer, "path": f"{base}/properties/position", "keys": [
            {"time": t4(open_f), "value": [A[0], A[1], 0]},
            {"time": t4(land_f - 1), "value": a12},
            {"time": t4(land_f), "value": [0, 0, 0]},
            {"time": t4(hold_f), "value": [0, 0, 0]},
            {"time": t4(exit_f), "value": [E[0], E[1], 0]}]}, hard=True)
        cfg.op(f"{tag}-rot{k}", "add_keyframe", {"layer": layer, "path": f"{base}/properties/rotation", "keys": [
            {"time": t4(open_f), "value": rA},
            {"time": t4(land_f - 1), "value": round(rA * 0.12)},
            {"time": t4(land_f), "value": 0},
            {"time": t4(hold_f), "value": 0},
            {"time": t4(exit_f), "value": rE}]}, hard=True)

def header(cfg, tag):
    cfg.cmd(f"{tag}-header", "layer.newText",
            {"text": HDR, "name": "HEADER", "position": [122, 54], "font": "Anton",
             "style": "Regular", "size": 30, "fill": OW, "allCaps": True,
             "justify": "left", "tracking": 200}, hard=True)
    cfg.op(f"{tag}-header-op", "set_property", {"layer": "HEADER", "path": "transform/opacity", "value": 55}, hard=True)
    cfg.cmd(f"{tag}-rule", "layer.newSolid", {"name": "HEADER-RULE", "color": OW, "width": 1676, "height": 2}, hard=True)
    cfg.op(f"{tag}-rule-pos", "set_property", {"layer": "HEADER-RULE", "path": "transform/position", "value": [960, 67, 0]}, hard=True)
    cfg.op(f"{tag}-rule-op", "set_property", {"layer": "HEADER-RULE", "path": "transform/opacity", "value": 55}, hard=True)

# letter tables: (assemble pos, assemble rot, exit pos, exit rot)
WINDOW_L = [((-60, -65), -22, (-95, 25), -28), ((5, -95), 14, (-20, 80), 18),
            ((30, 70), -16, (30, -85), 22), ((55, -60), 20, (70, 60), -14),
            ((80, 45), -26, (100, -40), 26), ((100, -35), 18, (125, 30), -24)]
FROM_L = [((-55, -70), -24, (-90, 30), -30), ((10, -90), 14, (-15, 85), 18),
          ((35, 70), -16, (40, -80), 22), ((70, -50), 20, (95, 55), -16)]
AROUND_L = [((-60, -60), -20, (-95, 35), -26), ((5, -95), 16, (-20, 80), 20),
            ((30, 75), -18, (35, -85), 24), ((55, -55), 22, (75, 60), -12),
            ((80, 40), -24, (105, -35), 28), ((100, -40), 16, (130, 25), -22)]

# ---------------------------------------------------------------- block 2
def build_b2():
    cfg = Cfg()
    cfg.op("open", "open_project", {"path": "/tmp/b2-base.ecproj"}, hard=True)
    cfg.open_comp("block2_she_pulled_down_the_window")
    for w, idx in (("SHE", 3), ("PULLED", 3), ("DOWN", 4), ("THE", 4)):
        white_treatment(cfg, w, idx, f"A-{w}")
    # WINDOW: wipe neutralized (completion pinned to 0), then assemble
    cfg.cmd("A-WINDOW-wipe49", "keys.set", {"layer": "WINDOW", "path": "effects/#3/completion",
            "time": t4(49), "value": 0}, hard=True)
    cfg.cmd("A-WINDOW-wipe58", "keys.set", {"layer": "WINDOW", "path": "effects/#3/completion",
            "time": t4(58), "value": 0}, hard=True)
    assemble(cfg, "WINDOW", WINDOW_L, 42, 49, 54, 62, "A-WIN", has_scale=False)
    header(cfg, "A")
    cfg.open_comp("block2_hey")
    for w in ("I", "SAID"):
        white_treatment(cfg, w, 3, f"B-{w}")
    header(cfg, "B")
    cfg.op("save", "save_project", {"path": f"{workdir()}/108-lyric-type-block2-v5.ecproj"}, hard=True)
    json.dump({"ops": cfg.ops}, open(HERE / "build-b2.json", "w"), indent=1)
    print("build-b2:", len(cfg.ops), "ops")

def render_b2():
    cfg = Cfg()
    cfg.op("open", "open_project", {"path": f"{workdir()}/108-lyric-type-block2-v5.ecproj"}, hard=True)
    for comp, n, tag in (("block2_she_pulled_down_the_window", 75, "b2a"),
                         ("block2_hey", 33, "b2b")):
        for f in range(n):
            cfg.op(f"{tag}-r{f:03d}", "render_frame",
                   {"comp": comp, "time": t4(f), "path": f"/tmp/{tag}/f{f:03d}.png", "max_side": 1920})
    json.dump({"ops": cfg.ops}, open(HERE / "render-b2.json", "w"), indent=1)
    print("render-b2:", len(cfg.ops), "ops")

# ---------------------------------------------------------------- block 3
def build_b3():
    cfg = Cfg()
    cfg.op("open", "open_project", {"path": "/tmp/b3-base.ecproj"}, hard=True)
    cfg.open_comp("block3_line1_she_said_where_im_from")
    for w in ("SHE", "SAID", "WHERE", "I'M"):
        white_treatment(cfg, w, 3, f"L1-{w}")
    assemble(cfg, "FROM", FROM_L, 34, 41, 45, 49, "L1-FROM")
    header(cfg, "L1")
    cfg.open_comp("block3_line2_i_told_her_im_not_around")
    for w in ("I", "TOLD", "HER", "I'M", "NOT"):
        white_treatment(cfg, w, 3, f"L2-{w}")
    assemble(cfg, "AROUND", AROUND_L, 33, 40, 42, 45, "L2-AROUND")
    header(cfg, "L2")
    cfg.open_comp("block3_cue4_no_way")
    for w in ("THEN_L0_1", "I_L0_1", "ASKED_L0_1", "WHERE_L0_1", "SHE_L0_1", "SHE_L1_2", "SAID_L1_1"):
        white_treatment(cfg, w, 3, f"C4-{w}")
    assemble(cfg, "FROM_L0_1", FROM_L, 45, 52, 73, 81, "C4-FROM")
    header(cfg, "C4")
    cfg.op("save", "save_project", {"path": f"{workdir()}/108-lyric-type-block3-take2-v4.ecproj"}, hard=True)
    json.dump({"ops": cfg.ops}, open(HERE / "build-b3.json", "w"), indent=1)
    print("build-b3:", len(cfg.ops), "ops")

def render_b3():
    cfg = Cfg()
    cfg.op("open", "open_project", {"path": f"{workdir()}/108-lyric-type-block3-take2-v4.ecproj"}, hard=True)
    for comp, n, tag in (("block3_line1_she_said_where_im_from", 60, "b3l1"),
                         ("block3_line2_i_told_her_im_not_around", 48, "b3l2"),
                         ("block3_cue4_no_way", 108, "b3c4")):
        for f in range(n):
            cfg.op(f"{tag}-r{f:03d}", "render_frame",
                   {"comp": comp, "time": t4(f), "path": f"/tmp/{tag}/f{f:03d}.png", "max_side": 1920})
    json.dump({"ops": cfg.ops}, open(HERE / "render-b3.json", "w"), indent=1)
    print("render-b3:", len(cfg.ops), "ops")

if __name__ == "__main__":
    build_b2()
    render_b2()
    build_b3()
    render_b3()
