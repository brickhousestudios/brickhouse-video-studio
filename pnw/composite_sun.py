#!/usr/bin/env python3
"""Composite the sunrise into verse1: text matte = |A - B| (A = current
film frames, B = bed-only render). Bed pixels get the sun (screen blend);
text pixels (incl. drop shadows) stay from A untouched.
Run ON the M2 in $W. Output: frames-verse1-v21r5/ (full copy of r4 frames
with comp frames 40..130 replaced; the shortened sun is gone by f105)."""
import numpy as np
from PIL import Image, ImageFilter
from pathlib import Path
import shutil

W = Path("/Volumes/STICK/BrickHouse/lyric-type-2026-10-31/pnw-2026-11-04")
A_DIR, B_DIR = W / "frames-verse1-v21r4", W / "frames-verse1-bedonly"
OUT = W / "frames-verse1-v21r5"
SUN = Path("/tmp/sun-frames")
if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(A_DIR, OUT)
print("copied r4 frames")

for f in range(40, 131):
    a = np.asarray(Image.open(A_DIR / f"f{f:04d}.png").convert("RGB")).astype(np.int16)
    b = np.asarray(Image.open(B_DIR / f"f{f:04d}.png").convert("RGB")).astype(np.float32)
    sun = np.asarray(Image.open(SUN / f"sun-f{f:04d}.png").convert("RGBA")).astype(np.float32)
    diff = np.abs(a - b.astype(np.int16)).max(axis=2)
    matte = Image.fromarray((diff > 12).astype(np.uint8) * 255).filter(
        ImageFilter.GaussianBlur(1.2))
    m = (np.asarray(matte).astype(np.float32) / 255.0)[:, :, None]
    sa = (sun[:, :, 3:4] / 255.0)
    # screen blend sun over bed
    bed_sun = 255 - (255 - b) * (1 - sun[:, :, :3] * sa / 255.0)
    out = a * m + bed_sun * (1 - m)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB").save(OUT / f"f{f:04d}.png")
    if f % 50 == 0:
        print("composited", f, "matte px:", int((diff > 12).sum()))
print("sun composite done")
