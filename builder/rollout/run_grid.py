#!/usr/bin/env python3
"""Phase-1 grid: build 4 EC driver configs (shadow variants on the 5 white
layers of a COPY of the concept-alt project), base64 them, and emit the M2
shell script that runs them. The caller relays the script via M4->M2 SSH."""
import base64
import json
import os

WORKDIR = os.environ.get("BRICKHOUSE_WORKDIR", "/Volumes/STICK/BrickHouse/lyric-type-2026-10-31")

WHITE = ["AND", "I", "STOP", "AT", "A"]
COMP = "line1_and_i_stop_at_a_light_REDLIGHT_V3"
BASE = "/tmp/grid-base.ecproj"

VARIANTS = {
    "g1": {"op": 100, "soft": 75, "stack": None},
    "g2": {"op": 100, "soft": 120, "stack": None},
    "g3": {"op": 100, "soft": 75, "stack": {"op": 85, "soft": 180}},
    "g4": {"op": 100, "soft": 200, "stack": None},
}

def t4(f):
    return round(f / 30.0, 4)

def build(name, v):
    ops = []
    def op(label, tool, args, hard=False):
        o = {"label": label, "tool": tool, "args": args}
        if hard:
            o["hard"] = True
        ops.append(o)
    op("open", "open_project", {"path": BASE}, hard=True)
    op("comp_open", "execute_command", {"command": "comp.open", "params": {"comp": COMP}}, hard=True)
    for w in WHITE:
        op(f"{w}-op", "set_property", {"layer": w, "path": "effects/#1/opacity", "value": v["op"]})
        op(f"{w}-soft", "set_property", {"layer": w, "path": "effects/#1/softness", "value": v["soft"]})
        if v["stack"]:
            op(f"{w}-add2", "add_effect", {"effect": "Drop Shadow", "layer": w})
            op(f"{w}-ds2-color", "set_property", {"layer": w, "path": "effects/#3/color", "value": [0.02, 0, 0, 1]})
            op(f"{w}-ds2-op", "set_property", {"layer": w, "path": "effects/#3/opacity", "value": v["stack"]["op"]})
            op(f"{w}-ds2-dist", "set_property", {"layer": w, "path": "effects/#3/distance", "value": 0})
            op(f"{w}-ds2-soft", "set_property", {"layer": w, "path": "effects/#3/softness", "value": v["stack"]["soft"]})
            op(f"{w}-ds2-dir", "set_property", {"layer": w, "path": "effects/#3/direction", "value": 135})
    if v["stack"]:
        op("probe-ds3", "get_property", {"layer": "STOP", "path": "effects/#3"})
    op("r41", "render_frame", {"comp": COMP, "time": t4(41), "path": f"/tmp/grid-{name}-f041.png", "max_side": 1920}, hard=True)
    op("r54", "render_frame", {"comp": COMP, "time": t4(54), "path": f"/tmp/grid-{name}-f054.png", "max_side": 1920}, hard=True)
    return {"ops": ops}

lines = []
for name, v in VARIANTS.items():
    cfg = json.dumps(build(name, v))
    b64 = base64.b64encode(cfg.encode()).decode()
    lines.append(f"echo {b64} | base64 -d > /tmp/grid-{name}.json")
lines.append(f"cp '{WORKDIR}/108-lyric-type-line1-concept-alt.ecproj' /tmp/grid-base.ecproj")
lines.append(f"cd '{WORKDIR}'")
for name in VARIANTS:
    lines.append(f"echo '=== {name} ===' >> /tmp/grid.log")
    lines.append(f"python3 ec_driver.py /tmp/grid-{name}.json >> /tmp/grid.log 2>&1")
lines.append("tar -cf /tmp/grid-renders.tar -C /tmp grid-g1-f041.png grid-g1-f054.png grid-g2-f041.png grid-g2-f054.png grid-g3-f041.png grid-g3-f054.png grid-g4-f041.png grid-g4-f054.png")
lines.append("echo GRID_ALL_DONE >> /tmp/grid.log")
print("\n".join(lines))
