#!/usr/bin/env python3
"""Assemble rough-cut-v4-2026-11-01.mp4 (PUNCH HOLDS): song 22.64 -> 37.20,
437 frames @30fps over the continuous bounce. Same frame-plan method and
final encode as assemble_rc3.py (crf 14). Map changes vs v3:
  161-200 block2 comp B NEW (block2-v7: HEY holds 20 frames with the push)
  201-217 foot-block2 plain: v3's extraction frames [7:24] shifted to
          [0:17] of the same list (the head-trim absorbs HEY's +7)
  314-424 block3 cue4 NEW (take2-v6: WAY holds 20 frames, re-faded bed)
  425-436 bed tail from the NEW master bed (frames 207-218; fade st 5.8)
Everything else is v3's exact sources (line-1 v2 segment, comp-A rain
PNGs, b3l13/b3l23 frame sets, foot-block extracts).
Run ONCE; hash the output before any check reads it."""
import subprocess
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
GOAL = HERE.parent.parent
LYRIC = HERE.parent / "lyric-type-2026-10-31"
B3 = HERE.parent / "block3-build-2026-11-01"
CLIPS = HERE.parent / "first-clip-2026-10-31"
BOUNCE = GOAL / "files" / "pipeline-2026-10-26" / "bounce-candidate.mp3"
W3 = HERE / "work-rc3"
WORK = HERE / "work-rc4"
FR = WORK / "frames_all_plan"
SEG = WORK / "segs"
OUT = LYRIC / "rough-cut-v4-2026-11-01.mp4"

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

def jpg_range(base, tag, lo, hi):
    d = base / tag
    return [d / f"f{f:03d}.jpg" for f in range(lo, hi + 1)]

def main():
    FR.mkdir(parents=True, exist_ok=True)
    plan = []
    a = extract(CLIPS / "foot-block1.mp4", "segA", vf="fps=30,scale=1920:1080", n=35)
    assert len(a) == 35, len(a)
    plan += a                                                              # 0-34
    plan += extract(HERE / "seg-line1-v2.mp4", "line1")                    # 35-105 (reused v2 segment)
    plan += [W3 / "rain" / f"f{f:03d}.png" for f in range(8, 63)]          # 106-160 (reused v3 rain)
    plan += extract(HERE / "seg-b2b-v4.mp4", "b2b4")                       # 161-200 NEW comp B
    fb = extract(CLIPS / "foot-block2.mp4", "segFB2",
                 vf="fps=30,scale=1920:1080,select='between(n\\,33\\,56)'")
    assert len(fb) == 24, len(fb)
    plan += fb[:17]                                                        # 201-217 (head-trimmed)
    plan += jpg_range(W3, "b3l13", 0, 49)                                  # 218-267 (reused v3)
    plan += jpg_range(W3, "b3l23", 0, 45)                                  # 268-313 (reused v3)
    plan += extract(HERE / "seg-b3c4-v4.mp4", "b3c44")                     # 314-424 NEW cue 4
    bed = extract(B3 / "bed-block3-recede-v4.mp4", "bedv4")
    plan += bed[207:219]                                                   # 425-436 NEW bed tail
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
