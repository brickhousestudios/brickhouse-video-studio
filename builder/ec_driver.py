#!/usr/bin/env python3
"""EffectCraft MCP driver for the lyric-type lane. Config-driven ops list.
Modes live in the config: a list of {tool, args} calls executed in order,
each result emitted as an ECJ line. Soft errors are captured, not fatal,
unless an op is marked "hard": true.
"""
import json, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import ec_cli  # noqa: E402

CONFIG = json.load(open(sys.argv[1]))

proc = subprocess.Popen([ec_cli(), "mcp"], stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE, text=True, bufsize=1)
_id = [0]

def emit(obj):
    print("ECJ " + json.dumps(obj), flush=True)

def send(obj):
    proc.stdin.write(json.dumps(obj) + "\n"); proc.stdin.flush()

def rpc(method, params=None):
    _id[0] += 1
    send({"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}})
    while True:
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("server closed during " + method)
        msg = json.loads(line)
        if msg.get("id") == _id[0]:
            if "error" in msg:
                raise RuntimeError(method + ": " + json.dumps(msg["error"])[:600])
            return msg["result"]

def tool(name, args):
    res = rpc("tools/call", {"name": name, "arguments": args})
    text = "".join(b.get("text", "") for b in res.get("content", [])
                   if b.get("type") == "text")
    if res.get("isError"):
        raise RuntimeError(name + " -> " + text[:1200])
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text[:4000]}

def main():
    rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "bh-lyric-type", "version": "1"}})
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    state = tool("get_state", {})
    emit({"event": "state", "gpu": state.get("app", {}).get("gpu"),
          "commands": state.get("app", {}).get("commands")})
    if state.get("app", {}).get("gpu"):
        raise RuntimeError("headless server reports gpu=true; refusing")
    for i, op in enumerate(CONFIG["ops"]):
        label = op.get("label", f"op{i}")
        try:
            if op.get("rpc") == "tools/list":
                r = rpc("tools/list", {})
                emit({"event": "op", "label": label,
                      "result": [t.get("name") for t in r.get("tools", [])]})
                continue
            r = tool(op["tool"], op.get("args", {}))
            emit({"event": "op", "label": label, "result": r})
            if op.get("save_as"):
                CONFIG[op["save_as"]] = r
        except Exception as e:
            emit({"event": "op_error", "label": label, "error": str(e)[:1200]})
            if op.get("hard"):
                raise
    emit({"event": "done"})

try:
    main()
except Exception as e:
    emit({"event": "fatal", "error": str(e)[:1200]})
finally:
    try: proc.stdin.close()
    except Exception: pass
    proc.terminate()
print("ECJ_DONE", flush=True)
