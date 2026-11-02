#!/usr/bin/env python3
"""Phase-2 verification on the rendered frame sets (JPG q95 from the M2).
Checks per unit: white-word onsets vs locked landings, hero assemble
(centroid at rest == locked render's centroid; scatter at open; break at
exit), hero purity (G-band red outside hero bbox), header presence."""
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).parent
FR = Path("/tmp/p2vm")            # extracted frame dirs land here
LYRIC = HERE.parent / "lyric-type-2026-10-31"
B3 = HERE.parent / "block3-build-2026-11-01"

def load(tag):
    d = FR / tag
    files = sorted(d.glob("f*.jpg")) or sorted(d.glob("f*.png"))
    return [np.asarray(Image.open(p).convert("RGB")) for p in files]

def load_mp4_frames(mp4, wanted):
    out = {}
    tmp = Path("/tmp/p2ref")
    tmp.mkdir(exist_ok=True)
    for f in wanted:
        p = tmp / f"{mp4.stem}-{f}.png"
        if not p.exists():
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4),
                            "-vf", f"select='eq(n\\,{f})'", "-vsync", "0", str(p)], check=True)
        out[f] = np.asarray(Image.open(p).convert("RGB"))
    return out

def white_core(img, box):
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].astype(np.int16)
    return int(((np.abs(c[..., 0] - 242) <= 20) & (np.abs(c[..., 1] - 237) <= 20) &
                (np.abs(c[..., 2] - 228) <= 22) & (c[..., 0] > 210)).sum())

def ink_loose(img, box):
    """Presence for 70%-rest smear words: bright low-sat pixels."""
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].astype(np.int16)
    return int(((c[..., 0] > 120) & ((c.max(axis=2) - c.min(axis=2)) < 45)).sum())

def hero_red(img):
    c = img.astype(np.int16)
    return (c[..., 0] > 200) & (c[..., 1] >= 35) & (c[..., 1] <= 95) & ((c[..., 0] - c[..., 1]) > 120)

def centroid(mask):
    ys, xs = np.where(mask)
    return (float(xs.mean()), float(ys.mean()), len(xs))

def onset(fs, fn, box, thresh=300):
    return next((i for i, im in enumerate(fs) if fn(im, box) > thresh), None)

def header_check(img, tag):
    band = img[20:76]
    ink = band.max(axis=2) > 90
    rows = np.where(ink.any(axis=1))[0]
    print(f"  {tag} header ink rows y {rows.min()+20}..{rows.max()+20} px={int(ink.sum())}")

R = []
def check(name, cond, detail=""):
    R.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

# ---------------------------------------------------------------- block2 A
print("== block2 comp A ==")
a = load("b2a")
check("SHE onset f9", onset(a, white_core, (1000, 130, 1290, 290)) == 9)
check("PULLED onset f24", onset(a, white_core, (1300, 130, 1810, 290)) == 24)
check("DOWN present f41", ink_loose(a[41], (1050, 320, 1450, 510)) > 4000, f"={ink_loose(a[41], (1050,320,1450,510))}")
check("DOWN absent f33", ink_loose(a[33], (1050, 320, 1450, 510)) < 800, f"={ink_loose(a[33], (1050,320,1450,510))}")
check("THE present f48", ink_loose(a[48], (1500, 320, 1810, 510)) > 3000, f"={ink_loose(a[48], (1500,320,1810,510))}")
win = (850, 540, 1810, 900)
c42 = centroid(hero_red(a[42])[540:900, 850:1810])
c49 = centroid(hero_red(a[49])[540:900, 850:1810])
c55 = centroid(hero_red(a[55])[540:900, 850:1810])
c62 = centroid(hero_red(a[62])[540:900, 850:1810])
print(f"  WINDOW centroids: f42={c42} f49={c49} f55={c55} f62={c62}")
d_rest = abs(c49[0] - c55[0]) + abs(c49[1] - c55[1])
check("WINDOW settled by f49 (centroid stable)", d_rest < 6, f"drift={d_rest:.1f}px")
d_open = abs(c42[0] - c55[0]) + abs(c42[1] - c55[1])
check("WINDOW scattered at open f42", d_open > 25, f"drift={d_open:.1f}px")
d_exit = abs(c62[0] - c55[0]) + abs(c62[1] - c55[1])
check("WINDOW breaking at f62", d_exit > 20, f"drift={d_exit:.1f}px")
m = hero_red(a[55])
ys, xs = np.where(m)
out = int(m.sum() - m[ys.min()-4:ys.max()+5, xs.min()-4:xs.max()+5].sum())
check("WINDOW purity f55 (red outside own bbox)", out == 0, f"outside={out}")
header_check(a[30], "compA")

# ---------------------------------------------------------------- block2 B
print("== block2 comp B ==")
b = load("b2b")
check("I onset f4", onset(b, white_core, (100, 700, 260, 900)) == 4)
check("SAID onset f11", onset(b, white_core, (200, 700, 700, 900)) == 11)
check("I/SAID cut at HEY f20", white_core(b[21], (100, 700, 700, 900)) < 300,
      f"f21 ink={white_core(b[21], (100,700,700,900))}")
hey20 = int(hero_red(b[20]).sum()); hey26 = int(hero_red(b[26]).sum())
check("HEY red f20 present", hey20 > 500000, f"={hey20}")
check("HEY gone f26", hey26 < 300, f"={hey26}")
ys, xs = np.where(hero_red(b[20]))
print(f"  HEY ink bbox x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}] (header band y28-67 overlap: {ys.min() < 68})")
header_check(b[10], "compB")

# ---------------------------------------------------------------- block3
print("== block3 (refs from shipped v3 preview) ==")
prev = LYRIC / "preview-block3-recede-v3.mp4"
ref = load_mp4_frames(prev, [41, 90, 148])
l1 = load("b3l1")
check("L1 SHE onset f9", onset(l1, white_core, (100, 130, 420, 290)) == 9)
check("L1 SAID onset f15", onset(l1, white_core, (340, 130, 800, 290)) == 15)
check("L1 WHERE onset f26", onset(l1, white_core, (100, 320, 700, 510)) == 26)
check("L1 I'M onset f33", onset(l1, white_core, (100, 540, 500, 900)) == 33)
fb = (550, 540, 1250, 900)
n41_new = centroid(hero_red(l1[41])[540:900, 550:1250])
n41_old = centroid(hero_red(ref[41])[540:900, 550:1250])
print(f"  FROM centroid new f41={n41_new} old f41={n41_old}")
check("L1 FROM rest centroid == v3", abs(n41_new[0] - n41_old[0]) + abs(n41_new[1] - n41_old[1]) < 8)
c34 = centroid(hero_red(l1[34])[540:900, 550:1250])
check("L1 FROM scattered at open f34", abs(c34[0] - n41_new[0]) + abs(c34[1] - n41_new[1]) > 25,
      f"drift={abs(c34[0]-n41_new[0]) + abs(c34[1]-n41_new[1]):.1f}px")
c49 = centroid(hero_red(l1[49])[540:900, 550:1250])
check("L1 FROM breaking at f49", abs(c49[0] - n41_new[0]) + abs(c49[1] - n41_new[1]) > 18,
      f"drift={abs(c49[0]-n41_new[0]) + abs(c49[1]-n41_new[1]):.1f}px")
mm = hero_red(l1[44]); ys, xs = np.where(mm)
out = int(mm.sum() - mm[ys.min()-4:ys.max()+5, xs.min()-4:xs.max()+5].sum())
check("L1 purity f44", out == 0, f"outside={out}")
header_check(l1[30], "L1")

l2 = load("b3l2")
check("L2 I onset f4", onset(l2, white_core, (1100, 130, 1250, 290)) == 4)
check("L2 TOLD onset f8", onset(l2, white_core, (1200, 130, 1600, 290)) == 8)
check("L2 HER onset f16", onset(l2, white_core, (1500, 130, 1810, 290)) == 16)
check("L2 I'M onset f23", onset(l2, white_core, (1050, 320, 1450, 510)) == 23)
check("L2 NOT onset f31", onset(l2, white_core, (1400, 320, 1810, 510)) == 31)
ab = (550, 540, 1600, 900)
a40_new = centroid(hero_red(l2[40])[540:900, 550:1600])
a40_old = centroid(hero_red(ref[90])[540:900, 550:1600])
print(f"  AROUND centroid new f40={a40_new} old(preview f90)={a40_old}")
check("L2 AROUND rest centroid == v3", abs(a40_new[0] - a40_old[0]) + abs(a40_new[1] - a40_old[1]) < 8)
a45 = centroid(hero_red(l2[45])[540:900, 550:1600])
check("L2 AROUND breaking at f45", abs(a45[0] - a40_new[0]) + abs(a45[1] - a40_new[1]) > 15,
      f"drift={abs(a45[0]-a40_new[0]) + abs(a45[1]-a40_new[1]):.1f}px")
header_check(l2[20], "L2")

c4 = load("b3c4")
check("C4 THEN onset f3", onset(c4, white_core, (100, 130, 450, 290)) == 3)
check("C4 I onset f27", onset(c4, white_core, (430, 130, 560, 290)) == 27)
check("C4 ASKED onset f32", onset(c4, white_core, (540, 130, 950, 290)) == 32)
check("C4 WHERE onset f42", onset(c4, white_core, (100, 320, 700, 510)) == 42)
check("C4 SHE(L0) onset f47", onset(c4, white_core, (100, 540, 500, 900)) == 47)
check("C4 SHE(L1) onset f59", onset(c4, white_core, (1200, 130, 1500, 290)) == 59)
check("C4 SAID onset f74", onset(c4, white_core, (1470, 130, 1810, 290)) == 74)
f52_new = centroid(hero_red(c4[52])[540:900, 700:1400])
f52_old = centroid(hero_red(ref[148])[540:900, 700:1400])
print(f"  C4 FROM centroid new f52={f52_new} old(preview f148)={f52_old}")
check("C4 FROM rest centroid == v3", abs(f52_new[0] - f52_old[0]) + abs(f52_new[1] - f52_old[1]) < 8)
no88 = int(hero_red(c4[88])[320:510, 1150:1810].sum())
no89 = int(hero_red(c4[89])[320:510, 1150:1810].sum())
check("C4 NO red present f88", no88 > 8000, f"={no88}")
check("C4 NO cleared f89", no89 < 200, f"={no89}")
way = hero_red(c4[92]); ys, xs = np.where(way)
check("C4 WAY giant f92", xs.max() - xs.min() > 1700, f"width={xs.max()-xs.min()} y[{ys.min()},{ys.max()}]")
lum105 = float(c4[105].mean())
check("C4 black at f105 (preview f201)", lum105 < 2.0, f"mean luma={lum105:.2f}")
header_check(c4[60], "C4")

fails = [r for r in R if not r[1]]
print(f"\n==== {len(R) - len(fails)}/{len(R)} PASS ====")
for n, _, d in fails:
    print("FAILED:", n, d)
