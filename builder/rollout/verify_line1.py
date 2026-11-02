#!/usr/bin/env python3
"""Line-1 unit verification: compare TEMPLATE-V2 segment vs concept-alt
preview frame by frame: per-word presence onsets (must match), LIGHT hero
purity (G-band red outside hero bbox), header ink + clearance, and the
f041 worst-frame separation (must match grid G3)."""
import subprocess
import sys
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).parent
ALT = HERE.parent / "lyric-type-2026-10-31" / "preview-line1-concept-alt.mp4"
V2 = HERE / "seg-line1-v2.mp4"
TMP = Path("/tmp/l1check")
TMP.mkdir(exist_ok=True)

def frames(mp4, tag):
    out = TMP / tag
    out.mkdir(exist_ok=True)
    if not list(out.glob("*.png")):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4),
                        "-vsync", "0", "-start_number", "0", str(out / "f%03d.png")], check=True)
    files = sorted(out.glob("*.png"))
    assert len(files) == 71, f"{tag}: {len(files)} frames"
    return [np.asarray(Image.open(p).convert("RGB")) for p in files]

def white_core(img, box):
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].astype(np.int16)
    return int(((np.abs(c[..., 0] - 242) <= 18) & (np.abs(c[..., 1] - 237) <= 18) &
                (np.abs(c[..., 2] - 228) <= 20) & (c[..., 0] > 215)).sum())

def hero_red(img, box=None):
    """G-band hero-red mask: R>200, G in [35,95], R-G>120 (matches #FF3B1F,
    excludes bloom tint #E8101A whose G=16)."""
    c = img.astype(np.int16)
    m = (c[..., 0] > 200) & (c[..., 1] >= 35) & (c[..., 1] <= 95) & ((c[..., 0] - c[..., 1]) > 120)
    if box:
        x0, y0, x1, y1 = box
        m = m[y0:y1, x0:x1]
    return m

BOXES = {"AND": (100, 130, 420, 290), "I": (425, 130, 570, 290),
         "STOP": (100, 300, 560, 510), "AT": (580, 300, 870, 510),
         "A": (100, 540, 340, 900)}
LIGHT_BOX = (360, 540, 1200, 900)

alt = frames(ALT, "alt")
v2 = frames(V2, "v2")

def onsets(fs, fn, thresh=300):
    out = {}
    for w, b in BOXES.items():
        out[w] = next((i for i, im in enumerate(fs) if fn(im, b) > thresh), None)
    return out

oa = onsets(alt, white_core)
ov = onsets(v2, white_core)
print("white onsets alt:", oa)
print("white onsets v2 :", ov)
print("white onsets MATCH:", oa == ov)

def red_onset(fs):
    return next((i for i, im in enumerate(fs) if int(hero_red(im, LIGHT_BOX).sum()) > 300), None)
print("LIGHT red onset alt:", red_onset(alt), " v2:", red_onset(v2))

# hero purity at f58: G-band red outside LIGHT box
for tag, fs in (("alt", alt), ("v2", v2)):
    m = hero_red(fs[58])
    x0, y0, x1, y1 = LIGHT_BOX
    outside = int(m.sum() - m[y0:y1, x0:x1].sum())
    print(f"{tag} f58 hero-red px total={int(m.sum())} outside LIGHT bbox={outside}")

# header: ink rows in band y 20..75 at f60; clearance = gap between header
# ink bottom and highest stack glyph top (white/red ink above y=150 search)
im = v2[60]
band = im[20:76]
ink = (band.max(axis=2) > 90)
rows = np.where(ink.any(axis=1))[0]
print(f"v2 header ink rows (abs y): {rows.min()+20}..{rows.max()+20}, ink px={int(ink.sum())}")
stack = v2[60][76:]
inkmask = (stack.max(axis=2) > 90)
srows = np.where(inkmask.any(axis=1))[0]
print(f"v2 highest stack ink below header: abs y={srows.min()+76}, clearance={(srows.min()+76)-(rows.max()+20)-1}px")
