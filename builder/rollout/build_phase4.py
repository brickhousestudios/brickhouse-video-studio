#!/usr/bin/env python3
"""Phase 4 (PUNCH HOLDS, BO verdict on v3 via Claude 2026-11-01 22:24 CT):
full-frame punches hold for their SUNG WORD (whisper-measured word-end on
the bounce + 2 frames), never a fixed frame count, with a 108% -> 100%
push (ease-out) across the hold. Same concept template + effects budget
as Phase 3 (build_phase3.py treatments verbatim); ONLY the two punches
change:

- HEY (block2_hey, from /tmp/b2-base.ecproj -> block2-v7): comp extended
  1.1s -> 1.4333s; the old cut key @f26 becomes a hold (100); new hard
  cut @f40 (opacity 0). "hey" measured on the bounce (house whisper,
  two slices 28.3/28.0 offsets): onset 28.74 (== build), end 29.30/29.20
  -> consensus end 29.25 +-0.15; hold_end = 29.25 + 2f = song 29.3167 =
  comp f39.5 -> HEY visible comp f20..39 (20 frames; was 6).
  Push: scale keys 108@f20, 104.8@f24, 101.9@f29, 100.4@f34, 100@f39
  (piecewise-linear ease-out approximation, decaying deltas).
  I SAID still cuts exactly at HEY's landing (untouched).
- WAY (block3_cue4_no_way, from /tmp/b3-base.ecproj -> take2-v6): comp
  extended 3.6s -> 3.8333s; old cut key @f95 becomes a hold (100); new
  hard cut @f109. "way" measured (slices 35.3/35.0 + round-6 record):
  onset 36.12 (== build), ends 36.72/36.66/36.60 -> consensus 36.66
  +-0.15; hold_end = 36.66 + 2f = song 36.7267 = preview f204.8 ->
  WAY visible comp-local f89..108 (20 frames; was 6).
  Push: scale keys 108@f89, 104.1@f94, 101.5@f99, 100.3@f104, 100@f108.
  Bloom/halo envelopes untouched (keyed to the landing, as built).
- BED FADE RE-TIME (cue 4): the bed fade now completes right after WAY
  cuts. New bed trim bed72-c4v4.mp4 = same round-6 recipe with the
  ffmpeg fade shifted st 5.6 -> 5.8 (nominal black at bed f207; measured
  on the VM render: bed <1.0 from f204, 0.00 from f207). Swapped into
  the cue-4 comp's bed layer via layer.replaceSource; the REDLIGHT-halo
  layer keeps the old bed item (its envelope window f88-95 sits where
  the two fades differ only marginally on an already-receded bed).
Emits: build-b2-v4.json, build-b3-v4.json, render-b2-v4.json (comp B
only), render-b3-v4.json (cue 4 only)."""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import workdir  # noqa: E402

HERE = Path(__file__).parent
OW = "#F2EDE4"
HDR = "DRIZZZ  \u2022  108  \u2022  BRICKHOUSE STUDIOS"

def t4(f):
    return round(f / 30.0, 4)


def punch_hold_keys(onset_s, word_end_s, fps, comp_offset):
    """FULL-FRAME PUNCH HOLD (locked rule) as code.

    A full-frame punch lands at onset - 2f (the house landing rule),
    holds for its whole sung word, and cuts 2 frames after the word's
    measured end; across the hold it pushes 108% -> 100% (ease-out).
    comp_offset is the song time (seconds) of the comp's frame 0.

    Returns (out_frame, scale_keys): out_frame is the comp frame of
    the hard cut (the first frame the punch is gone; the punch is
    visible landing..out_frame-1), and scale_keys are add_keyframe
    scale keys {"time", "value": [v, v, 0]} spanning the hold.

    Profile (derived from -- and exactly reproducing -- the two
    shipped v4 cases, HEY and WAY): interior keys sit at
    floor(k * span_f / 4) for k = 1..3, where span_f is the hold's
    fractional span (word_end - onset) * fps + 4; values follow
    round(100 + 8 * (1 - o / span) ** 2.2, 1) over the integer
    visible span, with the endpoints exactly 108 and 100.
    """
    landing = int(math.floor((onset_s - 2.0 / fps - comp_offset) * fps + 0.5))
    last_visible = int(math.floor((word_end_s + 2.0 / fps - comp_offset) * fps))
    span = last_visible - landing
    span_f = (word_end_s - onset_s) * fps + 4.0
    offsets = {0, span}
    for k in (1, 2, 3):
        o = int(math.floor(k * span_f / 4.0))
        if 0 < o < span:
            offsets.add(o)
    keys = []
    for o in sorted(offsets):
        if o == 0:
            v = 108
        elif o == span:
            v = 100
        else:
            v = round(100.0 + 8.0 * (1.0 - o / span) ** 2.2, 1)
        keys.append({"time": round((landing + o) / fps, 4), "value": [v, v, 0]})
    return last_visible + 1, keys

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
    # ---- comp A: phase-3 treatment verbatim (project coherence; segment reused)
    cfg.open_comp("block2_she_pulled_down_the_window")
    for w, idx in (("SHE", 3), ("PULLED", 3), ("DOWN", 4), ("THE", 4)):
        white_treatment(cfg, w, idx, f"A-{w}")
    cfg.cmd("A-WINDOW-wipe49", "keys.set", {"layer": "WINDOW", "path": "effects/#3/completion",
            "time": t4(49), "value": 0}, hard=True)
    cfg.cmd("A-WINDOW-wipe58", "keys.set", {"layer": "WINDOW", "path": "effects/#3/completion",
            "time": t4(58), "value": 0}, hard=True)
    cfg.op("A-WINDOW-scale", "add_keyframe", {"layer": "WINDOW", "path": "transform/scale", "keys": [
        {"time": 0, "value": [115, 115, 0]},
        {"time": t4(49), "value": [115, 115, 0]},
        {"time": t4(53), "value": [100, 100, 0]}]}, hard=True)
    header(cfg, "A")
    # ---- comp B: phase-3 treatment + PUNCH HOLD
    cfg.open_comp("block2_hey")
    cfg.cmd("B-compdur", "comp.settings", {"comp": "block2_hey", "duration": 1.4333}, hard=True)
    for w in ("I", "SAID"):
        white_treatment(cfg, w, 3, f"B-{w}")
    # HEY hold: extend layer out first, then add_keyframe (keys.set CANNOT
    # set values or add keys beyond the last one -- it clamps to the last
    # key; probe-verified 2026-11-01. add_keyframe REPLACES the value of
    # an existing key at the same time and adds new ones freely).
    # Hold + push come from punch_hold_keys(): "hey" measured on the
    # bounce (house whisper, two slices) -- onset 28.74, end consensus
    # 29.25 +-0.15; comp block2_hey frame 0 = song 28.00. It returns
    # visible f20..39 (20 frames) and the cut @f40. Opacity keys: the
    # pre-existing v3 cut key @f26 becomes the plateau start (100),
    # plateau end 100@f39, hard cut 0@f40.
    hey_out, hey_push = punch_hold_keys(28.74, 29.25, 30, 28.00)
    cfg.cmd("B-HEY-out", "layer.timing", {"layers": ["HEY"], "out": 1.4333}, hard=True)
    cfg.op("B-HEY-holdkeys", "add_keyframe", {"layer": "HEY", "path": "transform/opacity", "keys": [
        {"time": t4(26), "value": 100},
        {"time": t4(hey_out - 1), "value": 100},
        {"time": t4(hey_out), "value": 0}]}, hard=True)
    # push: 108 -> 100 ease-out across the hold (piecewise-linear keys)
    cfg.op("B-HEY-push", "add_keyframe", {"layer": "HEY", "path": "transform/scale", "keys": hey_push}, hard=True)
    header(cfg, "B")
    cfg.op("B-readback-comp", "get_comp", {"comp": "block2_hey"})
    cfg.op("B-readback-HEY", "get_layer", {"layer": "HEY"})
    cfg.op("B-readback-HDR", "get_layer", {"layer": "HEADER"})
    cfg.op("save", "save_project", {"path": f"{workdir()}/108-lyric-type-block2-v7.ecproj"}, hard=True)
    json.dump({"ops": cfg.ops}, open(HERE / "build-b2-v4.json", "w"), indent=1)
    print("build-b2-v4:", len(cfg.ops), "ops")

def render_b2():
    cfg = Cfg()
    cfg.op("open", "open_project", {"path": f"{workdir()}/108-lyric-type-block2-v7.ecproj"}, hard=True)
    for f in range(41):
        cfg.op(f"b2b4-r{f:03d}", "render_frame",
               {"comp": "block2_hey", "time": t4(f),
                "path": f"/tmp/b2b4/f{f:03d}.png", "max_side": 1920})
    json.dump({"ops": cfg.ops}, open(HERE / "render-b2-v4.json", "w"), indent=1)
    print("render-b2-v4:", len(cfg.ops), "ops")

# ---------------------------------------------------------------- block 3
def build_b3():
    cfg = Cfg()
    cfg.op("open", "open_project", {"path": "/tmp/b3-base.ecproj"}, hard=True)
    # ---- L1/L2: phase-3 treatment verbatim (segments reused)
    cfg.open_comp("block3_line1_she_said_where_im_from")
    for w in ("SHE", "SAID", "WHERE", "I'M"):
        white_treatment(cfg, w, 3, f"L1-{w}")
    header(cfg, "L1")
    cfg.open_comp("block3_line2_i_told_her_im_not_around")
    for w in ("I", "TOLD", "HER", "I'M", "NOT"):
        white_treatment(cfg, w, 3, f"L2-{w}")
    header(cfg, "L2")
    # ---- cue 4: phase-3 treatment + bed re-time + PUNCH HOLD
    cfg.open_comp("block3_cue4_no_way")
    cfg.cmd("C4-compdur", "comp.settings", {"comp": "block3_cue4_no_way", "duration": 3.8333}, hard=True)
    cfg.cmd("C4-bed-import", "mediaBrowser.import",
            {"paths": [f"{workdir()}/bed72-c4v4.mp4"], "sequence": False}, hard=True)
    cfg.cmd("C4-bed-swap", "layer.replaceSource",
            {"layer": "bed72-c4.mp4", "item": "bed72-c4v4.mp4"}, hard=True)
    for w in ("THEN_L0_1", "I_L0_1", "ASKED_L0_1", "WHERE_L0_1", "SHE_L0_1", "SHE_L1_2", "SAID_L1_1"):
        white_treatment(cfg, w, 3, f"C4-{w}")
    white_treatment(cfg, "FROM_L0_1", 3, "C4-FROM")
    # WAY hold: same punch_hold_keys() recipe as HEY (see comp B).
    # "way" measured on the bounce (house whisper, two slices + the
    # round-6 record) -- onset 36.12, end consensus 36.66 +-0.15; the
    # cue-4 comp's frame 0 = song 33.10. It returns visible f89..108
    # (20 frames) and the cut @f109. Opacity keys: the pre-existing
    # cut key @f95 becomes the plateau start (100), plateau end
    # 100@f108, hard cut 0@f109.
    way_out, way_push = punch_hold_keys(36.12, 36.66, 30, 33.10)
    cfg.cmd("C4-WAY-out", "layer.timing", {"layers": ["WAY"], "out": 3.8333}, hard=True)
    cfg.op("C4-WAY-holdkeys", "add_keyframe", {"layer": "WAY", "path": "transform/opacity", "keys": [
        {"time": t4(95), "value": 100},
        {"time": t4(way_out - 1), "value": 100},
        {"time": t4(way_out), "value": 0}]}, hard=True)
    cfg.op("C4-WAY-push", "add_keyframe", {"layer": "WAY", "path": "transform/scale", "keys": way_push}, hard=True)
    header(cfg, "C4")
    cfg.op("C4-readback-comp", "get_comp", {"comp": "block3_cue4_no_way"})
    cfg.op("C4-readback-WAY", "get_layer", {"layer": "WAY"})
    cfg.op("C4-readback-bednew", "get_layer", {"layer": "bed72-c4v4.mp4"})
    cfg.op("C4-readback-bedold", "get_layer", {"layer": "bed72-c4.mp4"})
    cfg.op("save", "save_project", {"path": f"{workdir()}/108-lyric-type-block3-take2-v6.ecproj"}, hard=True)
    json.dump({"ops": cfg.ops}, open(HERE / "build-b3-v4.json", "w"), indent=1)
    print("build-b3-v4:", len(cfg.ops), "ops")

def render_b3():
    cfg = Cfg()
    cfg.op("open", "open_project", {"path": f"{workdir()}/108-lyric-type-block3-take2-v6.ecproj"}, hard=True)
    for f in range(111):
        cfg.op(f"b3c44-r{f:03d}", "render_frame",
               {"comp": "block3_cue4_no_way", "time": t4(f),
                "path": f"/tmp/b3c44/f{f:03d}.png", "max_side": 1920})
    json.dump({"ops": cfg.ops}, open(HERE / "render-b3-v4.json", "w"), indent=1)
    print("render-b3-v4:", len(cfg.ops), "ops")

if __name__ == "__main__":
    build_b2()
    render_b2()
    build_b3()
    render_b3()
