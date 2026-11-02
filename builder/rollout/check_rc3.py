#!/usr/bin/env python3
"""Rough-cut v3 checks (mirror of check_rc2): stream shape, per-join
picture luma (both sides), black-run map, silencedetect, join-window
audio RMS. Run against the hashed deliverable only.
"""
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).parent
RC = HERE.parent / "lyric-type-2026-10-31" / "rough-cut-v3-2026-11-01.mp4"
FR = HERE / "work-rc3" / "check-frames"
FR.mkdir(parents=True, exist_ok=True)

JOINS = [35, 106, 161, 194, 218, 268, 314, 422]  # first frame of each new segment

def main():
    print(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                          "-show_entries", "stream=nb_read_frames,width,height,r_frame_rate,codec_name",
                          "-of", "default=noprint_wrappers=1", str(RC)],
                         capture_output=True, text=True).stdout)
    print(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0",
                          "-show_entries", "stream=codec_name,sample_rate,channels",
                          "-of", "default=noprint_wrappers=1", str(RC)],
                         capture_output=True, text=True).stdout)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(RC), "-vsync", "0",
                    "-start_number", "0", str(FR / "f%03d.png")], check=True)
    files = sorted(FR.glob("f*.png"))
    print("frames extracted:", len(files))
    lumas = []
    for p in files:
        lumas.append(float(np.asarray(Image.open(p).convert("L"), dtype=np.float32).mean()))
    print("\njoin check (mean luma before/after):")
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
