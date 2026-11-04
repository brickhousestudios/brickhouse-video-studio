#!/usr/bin/env python3
"""Resumable chunked pull of a file from the M2 via the hub.
12MB base64 chunks; per-chunk length assert; resumes from the local
file size; whole-file sha256 verification at the end.
Usage: pull_v52.py <remote_path> <local_path>"""
import base64, hashlib, json, os, subprocess, sys, time

SRC = sys.argv[1]
DST = sys.argv[2]
CHUNK = int(os.environ.get("PULL_CHUNK_MB", "4")) * 1024 * 1024
HUB = ["/home/hatch/workspace/m4hub/venv/bin/python",
       "/home/hatch/workspace/m4hub/hubcall2.py",
       "m2-all-mcp-hub", "desktop_start_process"]

def hub(cmd, timeout_ms=55000):
    args = json.dumps({"command": cmd, "timeout_ms": timeout_ms})
    r = subprocess.run(HUB + [args, "120"], capture_output=True, text=True,
                       cwd="/home/hatch/workspace/m4hub", timeout=110)
    return r.stdout

def remote_size_sha():
    for attempt in range(8):
        try:
            out = hub(f"stat -f %z {SRC}; shasum -a 256 {SRC} | cut -d' ' -f1")
        except subprocess.TimeoutExpired:
            out = ""
        nums = [l.strip() for l in out.splitlines() if l.strip().isdigit()]
        shas = [l.strip() for l in out.splitlines()
                if len(l.strip()) == 64 and all(c in "0123456789abcdef" for c in l.strip())]
        if nums and shas:
            return int(nums[0]), shas[0]
        print(f"  size/sha probe failed (try {attempt+1})", flush=True)
        time.sleep(5)
    raise RuntimeError("remote_size_sha failed after retries")

def pull_chunk(off, n):
    script = (f"import base64,sys\n"
              f"f=open('{SRC}','rb'); f.seek({off})\n"
              f"sys.stdout.write(base64.b64encode(f.read({n})).decode())\n")
    b64 = base64.b64encode(script.encode()).decode()
    cmd = f"echo {b64} | base64 -d > /tmp/pullc.py; python3 /tmp/pullc.py"
    for attempt in range(8):
        try:
            out = hub(cmd)
        except subprocess.TimeoutExpired:
            print(f"  chunk @{off}: hub timeout (try {attempt+1})", flush=True)
            time.sleep(5)
            continue
        lines = [l.strip() for l in out.splitlines()
                 if len(l.strip()) > 100 and all(
                     c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
                     for c in l.strip())]
        try:
            data = base64.b64decode("".join(lines))
        except Exception:
            data = b""
        if len(data) == n:
            return data
        print(f"  chunk @{off}: got {len(data)}/{n} (try {attempt+1})", flush=True)
        time.sleep(3)
    raise RuntimeError(f"chunk @{off} failed after retries")

def main():
    size, sha = remote_size_sha()
    print(f"remote: {size} bytes sha256 {sha}", flush=True)
    have = os.path.getsize(DST) if os.path.exists(DST) else 0
    if have > size:
        os.remove(DST)
        have = 0
    if have == size and size > 0:
        h = hashlib.sha256(open(DST, "rb").read()).hexdigest()
        print("already complete, sha match:", h == sha, flush=True)
        return
    f = open(DST, "r+b" if have else "wb")
    if have:
        f.seek(have)
    off = have
    while off < size:
        n = min(CHUNK, size - off)
        data = pull_chunk(off, n)
        f.write(data)
        f.flush()
        off += n
        print(f"pulled {off}/{size}", flush=True)
    f.close()
    h = hashlib.sha256(open(DST, "rb").read()).hexdigest()
    print("DONE local sha256:", h, "match:", h == sha, flush=True)

if __name__ == "__main__":
    main()
