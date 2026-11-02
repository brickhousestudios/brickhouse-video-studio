#!/usr/bin/env python3
"""Assemble rough-cut-v3-2026-11-01.mp4: song 22.64 -> 37.20, 437 frames
@30fps over the continuous bounce. Identical segment map to v2
(assemble_rc2.py); only the changed units are new renders:
  0-34    foot-block1 plain (source 0-1.1667s, fps-converted)
  35-105  line 1 concept v2 (seg-line1-v2.mp4)       [REUSED from v2]
  106-160 block2 comp A + SAM rain, comp frames 8-62 [NEW: block2-v6]
  161-193 block2 comp B (HEY)                        [REUSED v2 frames]
  194-217 foot-block2 plain extended (source 1.10-1.90s)
  218-267 block3 line1 f0-49                         [NEW: take2-v5]
  268-313 block3 line2 f0-45                         [NEW: take2-v5]
  314-421 block3 cue4 f0-107                         [NEW: take2-v5]
  422-436 master bed tail frames 204-218 (the fade to black)
Run ONCE; hash the output before any check reads it.
"""
import subprocess
import sys
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).parent
GOAL = HERE.parent.parent
LYRIC = HERE.parent / "lyric-type-2026-10-31"
B3 = HERE.parent / "block3-build-2026-11-01"
CLIPS = HERE.parent / "first-clip-2026-10-31"
BOUNCE = GOAL / "files" / "pipeline-2026-10-26" / "bounce-candidate.mp3"
WORK = HERE / "work-rc3"
FR = WORK / "frames"
SEG = WORK / "segs"
OUT = LYRIC / "rough-cut-v3-2026-11-01.mp4"

def extract(mp4, tag, vf=None, n=None):
    d = SEG / tag
    d.mkdir(parents=True, exist_ok=True)
    if list(d.glob("f*.png")):
        files = sorted(d.glob("f*.png"))
        return files[:n] if n else files
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(mp4)]
    if vf:
        cmd += ["-vf", vf]
    if n:
        cmd += ["-frames:v", str(n)]
    cmd += ["-vsync", "0", "-start_number", "0", str(d / "f%03d.png")]
    subprocess.run(cmd, check=True)
    return sorted(d.glob("f*.png"))

def jpg_range(tag, lo, hi):
    d = WORK / tag
    return [d / f"f{f:03d}.jpg" for f in range(lo, hi + 1)]

def main():
    FR.mkdir(parents=True, exist_ok=True)
    plan = []
    # A: foot-block1 source 0..1.1667 at 30fps -> 35 frames
    a = extract(CLIPS / "foot-block1.mp4", "segA", vf="fps=30,scale=1920:1080", n=35)
    assert len(a) == 35, len(a)
    plan += a
    # line 1 concept v2 (REUSED segment, sha256 ea6eb820...)
    plan += extract(HERE / "seg-line1-v2.mp4", "line1")
    # comp A rain frames (PNG, from composite_rain_v2) f8..62
    rain = Path(sys.argv[1])
    plan += [rain / f"f{f:03d}.png" for f in range(8, 63)]
    # comp B (REUSED v2 frames staged in work-rc3/b2b)
    plan += jpg_range("b2b", 0, 32)
    # foot-block2 extended: converted frames 33..56 (source 1.10..1.90)
    fb = extract(CLIPS / "foot-block2.mp4", "segFB2",
                 vf="fps=30,scale=1920:1080,select='between(n\\,33\\,56)'")
    assert len(fb) == 24, len(fb)
    plan += fb
    # block 3 (NEW renders)
    plan += jpg_range("b3l13", 0, 49)
    plan += jpg_range("b3l23", 0, 45)
    plan += jpg_range("b3c43", 0, 107)
    # bed tail frames 204..218
    bed = extract(B3 / "bed-block3-recede.mp4", "bed")
    plan += bed[204:219]
    assert len(plan) == 437, f"frame plan = {len(plan)}"
    for i, src in enumerate(plan):
        dst = FR / f"f{i:04d}.png"
        if not dst.exists():
            Image.open(src).convert("RGB").save(dst)
    cmd = ["ffmpeg", "-y", "-v", "error", "-framerate", "30", "-i", str(FR / "f%04d.png"),
           "-ss", "22.64", "-t", "14.5667", "-i", str(BOUNCE),
           "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-r", "30",
           "-frames:v", "437", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           str(OUT)]
    subprocess.run(cmd, check=True)
    print("wrote", OUT)

if __name__ == "__main__":
    main()
