#!/usr/bin/env python3
"""Phase-2 verification, corrected methods: jump-based white onsets (the
beds' blown streaks false-positive any absolute threshold), plateau-frame
hero centroids, corrected NO box, DOWN/THE rise series."""
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).parent
FR = Path("/tmp/p2vm")
SAM = HERE.parent / "sam-2026-11-01"
LYRIC = HERE.parent / "lyric-type-2026-10-31"

def load(tag):
    d = FR / tag
    return [np.asarray(Image.open(p).convert("RGB")) for p in sorted(d.glob("f*.jpg"))]

def load_pngs(d):
    return [np.asarray(Image.open(p).convert("RGB")) for p in sorted(Path(d).glob("f*.png"))]

def strict(img, box):
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].astype(np.int16)
    return int(((np.abs(c[..., 0] - 242) <= 20) & (np.abs(c[..., 1] - 237) <= 20) &
                (np.abs(c[..., 2] - 228) <= 22) & (c[..., 0] > 210)).sum())

def loose(img, box):
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].astype(np.int16)
    lum = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    return int(((lum > 120) & ((c.max(axis=2) - c.min(axis=2)) < 45)).sum())

def hero_red(img):
    c = img.astype(np.int16)
    return (c[..., 0] > 200) & (c[..., 1] >= 35) & (c[..., 1] <= 95) & ((c[..., 0] - c[..., 1]) > 120)

def centroid(mask):
    ys, xs = np.where(mask)
    return float(xs.mean()), float(ys.mean()), len(xs)

def jump_onset(fs, box):
    prev = strict(fs[0], box)
    for i in range(1, len(fs)):
        cur = strict(fs[i], box)
        if cur - prev > 12000 and cur >= 15000:
            return i
        prev = cur
    return None

R = []
def check(name, cond, detail=""):
    R.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

WHITE_CASES = [
    ("b2a", "PULLED", (1300, 130, 1810, 290), 24),
    ("b2b", "SAID", (200, 700, 700, 900), 11),
    ("b3l1", "SHE", (100, 130, 420, 290), 9), ("b3l1", "SAID", (340, 130, 800, 290), 15),
    ("b3l1", "WHERE", (100, 320, 700, 510), 26), ("b3l1", "I'M", (100, 540, 500, 900), 33),
    ("b3l2", "TOLD", (1200, 130, 1600, 290), 8), ("b3l2", "HER", (1500, 130, 1810, 290), 16),
    ("b3l2", "I'M", (1050, 320, 1450, 510), 23), ("b3l2", "NOT", (1400, 320, 1810, 510), 31),
    ("b3c4", "THEN", (100, 130, 450, 290), 3), ("b3c4", "I", (430, 130, 560, 290), 27),
    ("b3c4", "ASKED", (540, 130, 950, 290), 32), ("b3c4", "WHERE", (100, 320, 700, 510), 42),
    ("b3c4", "SHE(L0)", (100, 540, 500, 900), 47), ("b3c4", "SHE(L1)", (1200, 130, 1500, 290), 59),
    ("b3c4", "SAID", (1470, 130, 1810, 290), 74),
]
cache = {}
for tag, w, box, want in WHITE_CASES:
    if tag not in cache:
        cache[tag] = load(tag)
    got = jump_onset(cache[tag], box)
    check(f"{tag} {w} jump-onset == f{want}", got == want, f"got {got}")

a = cache["b2a"]
old = load_pngs(SAM / "compa-frames")
w_new = centroid(hero_red(a[51])[540:900, 850:1810])
w_old = centroid(hero_red(old[60])[540:900, 850:1810])
w_50 = centroid(hero_red(a[50])[540:900, 850:1810])
w_53 = centroid(hero_red(a[53])[540:900, 850:1810])
print(f"  WINDOW centroid new f51={w_new} old f60={w_old} plateau f50={w_50} f53={w_53}")
check("WINDOW rest centroid == v4", abs(w_new[0] - w_old[0]) + abs(w_new[1] - w_old[1]) < 8,
      f"drift={abs(w_new[0]-w_old[0]) + abs(w_new[1]-w_old[1]):.1f}")
check("WINDOW plateau stable f50~f53", abs(w_50[0] - w_53[0]) + abs(w_50[1] - w_53[1]) < 6,
      f"drift={abs(w_50[0]-w_53[0]) + abs(w_50[1]-w_53[1]):.1f}")

l2 = cache["b3l2"]
tmp = Path("/tmp/p2ref"); tmp.mkdir(exist_ok=True)
p90 = tmp / "preview-block3-recede-v3-90.png"
if not p90.exists():
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(LYRIC / "preview-block3-recede-v3.mp4"),
                    "-vf", "select='eq(n\\,90)'", "-vsync", "0", str(p90)], check=True)
old90 = np.asarray(Image.open(p90).convert("RGB"))
for f in (41, 42):
    an = centroid(hero_red(l2[f])[540:900, 550:1600])
    ao = centroid(hero_red(old90)[540:900, 550:1600])
    print(f"  AROUND centroid new f{f}={an} old preview f90={ao}")
    check(f"AROUND rest centroid f{f} ~= v3", abs(an[0] - ao[0]) + abs(an[1] - ao[1]) < 8,
          f"drift={abs(an[0]-ao[0]) + abs(an[1]-ao[1]):.1f}")

c4 = cache["b3c4"]
no_box = (60, 330, 900, 830)
n85 = int(hero_red(c4[85])[330:830, 60:900].sum())
n81 = int(hero_red(c4[81])[330:830, 60:900].sum())
check("C4 NO red present (solo window f81/f85)", n81 > 20000 and n85 > 20000, f"f81={n81} f85={n85}")

for w, box, lo, hi in (("DOWN", (1050, 320, 1450, 510), 33, 48), ("THE", (1500, 320, 1810, 510), 40, 55)):
    series = {f: loose(a[f], box) for f in range(lo, hi + 1, 3)}
    print(f"  {w} loose series:", series)
new41 = loose(a[41], (1050, 320, 1450, 510)); old41 = loose(old[41], (1050, 320, 1450, 510))
print(f"  DOWN box loose f41: new={new41} old(v4)={old41} (color differs; shape parity only)")
print(f"\n==== {sum(R)}/{len(R)} PASS ====")
