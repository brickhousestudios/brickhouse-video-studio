#!/usr/bin/env python3
"""Phase 1 finish: apply the G3 white-word shadow treatment to the 5 white
layers of a fresh copy of the concept-alt project, Save-As
108-lyric-type-TEMPLATE-V2.ecproj, render comp frames f0..f70.
Emits the EC driver config JSON on stdout."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import workdir  # noqa: E402

WHITE = ["AND", "I", "STOP", "AT", "A"]
COMP = "line1_and_i_stop_at_a_light_REDLIGHT_V3"
SRC = "/tmp/tv2-base.ecproj"

def t4(f):
    return round(f / 30.0, 4)

ops = []
def op(label, tool, args, hard=False):
    o = {"label": label, "tool": tool, "args": args}
    if hard:
        o["hard"] = True
    ops.append(o)

op("open", "open_project", {"path": SRC}, hard=True)
op("comp_open", "execute_command", {"command": "comp.open", "params": {"comp": COMP}}, hard=True)
for w in WHITE:
    op(f"{w}-op", "set_property", {"layer": w, "path": "effects/#1/opacity", "value": 100})
    # softness of #1 stays 75 (locked); stacked second shadow appended after grain
    op(f"{w}-add2", "add_effect", {"effect": "Drop Shadow", "layer": w})
    op(f"{w}-ds2-color", "set_property", {"layer": w, "path": "effects/#3/color", "value": [0.02, 0, 0, 1]})
    op(f"{w}-ds2-op", "set_property", {"layer": w, "path": "effects/#3/opacity", "value": 85})
    op(f"{w}-ds2-dist", "set_property", {"layer": w, "path": "effects/#3/distance", "value": 0})
    op(f"{w}-ds2-soft", "set_property", {"layer": w, "path": "effects/#3/softness", "value": 180})
    op(f"{w}-ds2-dir", "set_property", {"layer": w, "path": "effects/#3/direction", "value": 135})
op("save", "save_project", {"path": str(workdir() / "108-lyric-type-TEMPLATE-V2.ecproj")}, hard=True)
for f in range(71):
    op(f"r{f:03d}", "render_frame", {"comp": COMP, "time": t4(f), "path": f"/tmp/l1v2/f{f:03d}.png", "max_side": 1920})
print(json.dumps({"ops": ops}))
