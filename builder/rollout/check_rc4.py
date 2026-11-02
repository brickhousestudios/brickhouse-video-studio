#!/usr/bin/env python3
"""Join + audio continuity check for rough-cut-v4 (mirror of check_rc3
with the v4 join list: the comp-B tail join moved 194 -> 201; the bed
tail join moved 422 -> 425). Run against the hashed deliverable only."""
import io
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

R = Path(__file__).parent
RC = R.parent / "lyric-type-2026-10-31" / "rough-cut-v4-2026-11-01.mp4"
JOINS = [35, 106, 161, 201, 218, 268, 314, 425]

def main():
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(RC), "-vf", "scale=320:180",
                        "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    import re
    pngs = re.findall(rb"\x89PNG\r\n\x1a\n.*?\x00\x00\x00\x00IEND\xaeB`\x82", r.stdout, re.S)
    lumas = [float(np.asarray(Image.open(io.BytesIO(p)).convert("L"), dtype=np.float32).mean())
             for p in pngs]
    print("frames:", len(lumas))
    for j in JOINS:
        print(f"  join @{j}: f{j-1}={lumas[j-1]:.1f}  f{j}={lumas[j]:.1f}")
    black = [i for i, l in enumerate(lumas) if l < 1.0]
    if black:
        runs = []
        s = black[0]; prev = black[0]
        for i in black[1:]:
            if i == prev + 1:
                prev = i
            else:
                runs.append((s, prev)); s = i; prev = i
        runs.append((s, prev))
        print("black runs (luma<1):", runs)
    else:
        print("black runs: none")
    print("final frame luma:", lumas[-1])
    sil = subprocess.run(["ffmpeg", "-i", str(RC), "-af", "silencedetect=noise=-50dB:d=0.1",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    lines = [l.strip() for l in sil.splitlines() if "silence_" in l]
    print("\nsilencedetect (-50dB, 0.1s):", len(lines) // 2, "silences")
    for l in lines:
        print("  ", l.split("] ")[-1])
    print("\njoin audio RMS (dB, 0.4s window centered on join):")
    audio = subprocess.run(["ffmpeg", "-v", "error", "-i", str(RC), "-vn", "-f", "f32le",
                            "-ar", "48000", "-ac", "1", "-"], capture_output=True).stdout
    x = np.frombuffer(audio, dtype=np.float32)
    for j in JOINS:
        c = int(j / 30 * 48000)
        w = x[max(0, c - 9600):c + 9600]
        rms = float(np.sqrt((w ** 2).mean())) if len(w) else 0.0
        print(f"  join @{j} (t={j/30:.2f}s): {20*np.log10(rms + 1e-9):.1f} dB")

if __name__ == "__main__":
    main()
