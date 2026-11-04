#!/usr/bin/env python3
"""Hub-call helper: runs a shell command on the M2 via the M4 hub.
Usage: echo '<cmd>' | python3 h2.py [timeout_ms]  (cmd read from stdin,
one line) — prints the process's initial output."""
import json, subprocess, sys

timeout_ms = int(sys.argv[1]) if len(sys.argv) > 1 else 25000
cmd = sys.stdin.read().strip()
args = json.dumps({"command": cmd, "timeout_ms": timeout_ms})
r = subprocess.run(["/home/hatch/workspace/m4hub/venv/bin/python",
                    "/home/hatch/workspace/m4hub/hubcall2.py",
                    "m2-all-mcp-hub", "desktop_start_process", args, "120"],
                   capture_output=True, text=True,
                   cwd="/home/hatch/workspace/m4hub", timeout=115)
print(r.stdout)
if r.stderr:
    print(r.stderr, file=sys.stderr)
