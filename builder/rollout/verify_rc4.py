#!/usr/bin/env python3
"""Rough-cut v4 verification FROM THE SHIPPED FILE. Ports verify_rc3.py's
machinery verbatim (strict masks, per-word boxes, jump-onset landings,
scatter census, color truth, headers) — the segment map is unchanged, so
every v3 expectation carries over — and adds the v4 headline checks:
HEY/WAY on-screen frame counts (v3: 6 each) and the 108% -> 100% push
contraction + ease profile across each hold, plus the re-timed black
tail (first <1.0 within ~3 frames after WAY's last frame, 0.00 finals)."""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
V4 = HERE.parent / "lyric-type-2026-10-31" / "rough-cut-v4-2026-11-01.mp4"
FR = HERE / "work-rc4" / "check-frames"
FR.mkdir(parents=True, exist_ok=True)
if len(list(FR.glob("f*.png"))) < 437:
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(V4),
                    "-vsync", "0", "-start_number", "0", str(FR / "f%03d.png")], check=True)
FS = [np.asarray(Image.open(p).convert("RGB")) for p in sorted(FR.glob("f*.png"))]
print("frames loaded:", len(FS))

def hero_red(img):
    c = img.astype(np.int16)
    return (c[..., 0] > 200) & (c[..., 1] >= 35) & (c[..., 1] <= 95) & ((c[..., 0] - c[..., 1]) > 120)

def strict(img, box):
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].astype(np.int16)
    return int(((np.abs(c[..., 0] - 242) <= 20) & (np.abs(c[..., 1] - 237) <= 20) &
                (np.abs(c[..., 2] - 228) <= 22) & (c[..., 0] > 210)).sum())

def red_n(img, box):
    x0, y0, x1, y1 = box
    return int(hero_red(img[y0:y1, x0:x1]).sum())

def centroid(mask):
    ys, xs = np.where(mask)
    return float(xs.mean()), float(ys.mean()), len(xs)

def iou(a, b):
    return float((a & b).sum() / max(1, (a | b).sum()))

R = []
def check(name, cond, detail=""):
    R.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

def jump_onset(counter, lo, hi):
    vals = {f: counter(f) for f in range(lo, hi + 1)}
    mx = max(vals.values())
    prev = vals[lo]
    for f in range(lo + 1, hi + 1):
        if vals[f] - prev > 0.35 * mx and vals[f] > 0.5 * mx:
            return f, vals
        prev = vals[f]
    return None, vals

def luma(f):
    return float(np.asarray(Image.fromarray(FS[f]).convert("L"), dtype=np.float32).mean())

check("frame count == 437", len(FS) == 437, str(len(FS)))

# ---------------------------------------------------------------- headline
print("\n== punch holds (headline) ==")
def on_screen(lo, hi, settle_f):
    settle = int(hero_red(FS[settle_f]).sum())
    return [f for f in range(lo, hi + 1) if int(hero_red(FS[f]).sum()) >= 0.5 * settle], settle
hey_frames, hey_settle = on_screen(175, 206, 199)
check("HEY on screen == 20 frames (v3: 6)", hey_frames == list(range(181, 201)),
      f"{hey_frames[0]}..{hey_frames[-1]} n={len(hey_frames)} settle={hey_settle}")
way_frames, way_settle = on_screen(398, 431, 421)
check("WAY on screen == 20 frames (v3: ~6)", way_frames == list(range(403, 423)),
      f"{way_frames[0]}..{way_frames[-1]} n={len(way_frames)} settle={way_settle}")

def red_bbox(f):
    ys, xs = np.where(hero_red(FS[f]))
    return int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
for tag, (f0, f1, f2) in (("HEY", (181, 190, 199)), ("WAY", (403, 412, 421))):
    b0, b1, b2 = red_bbox(f0), red_bbox(f1), red_bbox(f2)
    print(f"  {tag} ink box W x H: landing {b0}, mid {b1}, hold-end {b2}")
    check(f"{tag} push contracts (width)", b0[0] > b1[0] > b2[0],
          f"{b0[0]} > {b1[0]} > {b2[0]} ratio {b0[0]/b2[0]:.3f}")
    dim = 0 if tag == "HEY" else 1  # WAY width saturates at frame edges; ease reads on height
    check(f"{tag} push ease-out (decaying deltas, {'width' if dim == 0 else 'height'})",
          (b0[dim] - b1[dim]) > (b1[dim] - b2[dim]), f"d1={b0[dim]-b1[dim]} d2={b1[dim]-b2[dim]}")

print("\n== black tail ==")
lt = {n: round(luma(n), 3) for n in range(418, 437)}
print("  tail lumas:", lt)
first_lt1 = next(n for n in range(418, 437) if lt[n] < 1.0)
check("first luma < 1.0 within ~3 frames after WAY's cut (422)", first_lt1 in (423, 424, 425), f"f{first_lt1}")
check("0.00 from f425 to end", all(lt[n] == 0.0 for n in range(425, 437)))

# ---------------------------------------------------------------- landings
print("\n== landings (assembly frames, == v3) ==")
WHITE = [
    ("PULLED-A", (1300, 130, 1810, 290), 122),
    ("SAID-B", (200, 700, 700, 900), 172),
    ("SHE-L1", (100, 130, 420, 290), 227), ("SAID-L1", (340, 130, 800, 290), 233),
    ("WHERE-L1", (100, 320, 700, 510), 244), ("I'M-L1", (100, 540, 500, 900), 251),
    ("I-L2", (1180, 130, 1330, 290), 272),
    ("TOLD-L2", (1200, 130, 1600, 290), 276), ("HER-L2", (1500, 130, 1810, 290), 284),
    ("I'M-L2", (1050, 320, 1450, 510), 291), ("NOT-L2", (1400, 320, 1810, 510), 299),
    ("THEN-C4", (100, 130, 450, 290), 317), ("I-C4", (430, 130, 560, 290), 341),
    ("ASKED-C4", (540, 130, 950, 290), 346), ("WHERE-C4", (100, 320, 700, 510), 356),
    ("SHE-C4-L0", (100, 540, 500, 900), 361), ("SHE-C4-L1", (1200, 130, 1500, 290), 373),
    ("SAID-C4", (1470, 130, 1810, 290), 388),
    ("FROM-C4(white)", (700, 540, 1400, 900), 366),
]
for name, box, exp in WHITE:
    got, _ = jump_onset(lambda f, b=box: strict(FS[f], b), exp - 4, exp + 4)
    check(f"{name} onset == f{exp}", got == exp, f"got {got}")
RED = [
    ("WINDOW", (850, 540, 1810, 900), 147), ("FROM-L1", (550, 540, 1250, 900), 259),
    ("AROUND", (550, 540, 1600, 900), 308), ("NO", (60, 330, 900, 830), 395),
]
for name, box, exp in RED:
    got, _ = jump_onset(lambda f, b=box: red_n(FS[f], b), exp - 4, exp + 4)
    check(f"{name} onset == f{exp}", got == exp, f"got {got}")
for name, exp, lo, hi in (("WAY", 403, 399, 407), ("HEY", 181, 177, 185)):
    got, _ = jump_onset(lambda f: int(hero_red(FS[f]).sum()), lo, hi)
    check(f"{name} onset == f{exp}", got == exp, f"got {got}")

# ---------------------------------------------------------------- scatter census
print("\n== scatter census ==")
def _mask(img, box, kind):
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1]
    if kind == "red":
        return hero_red(c)
    cc = c.astype(np.int16)
    return ((np.abs(cc[..., 0] - 242) <= 20) & (np.abs(cc[..., 1] - 237) <= 20) &
            (np.abs(cc[..., 2] - 228) <= 22) & (cc[..., 0] > 210))

def ink_of(img, box, kind):
    return int(_mask(img, box, kind).sum())

def census2(name, box, land, settle_f, kind, exit_pair=None, bed_baseline=None):
    s = ink_of(FS[settle_f], box, kind)
    pre2, pre1 = ink_of(FS[land - 2], box, kind), ink_of(FS[land - 1], box, kind)
    at = ink_of(FS[land], box, kind)
    cl = centroid(_mask(FS[land], box, kind)); cs = centroid(_mask(FS[settle_f], box, kind))
    drift = abs(cl[0] - cs[0]) + abs(cl[1] - cs[1])
    if bed_baseline is None:
        pre_ok = pre2 < 0.02 * s and pre1 < 0.02 * s
        pre_detail = f"pre2={pre2} pre1={pre1} settled={s}"
    else:
        pre_shape = iou(_mask(FS[land - 1], box, kind), _mask(FS[settle_f], box, kind))
        pre_ok = pre1 <= 1.3 * bed_baseline and pre_shape < 0.10
        pre_detail = f"pre1={pre1} bed-baseline={bed_baseline} pre-vs-glyph IoU={pre_shape:.3f}"
    check(f"{name}: no incoming scatter", pre_ok, pre_detail)
    check(f"{name}: full word at landing", at > 0.55 * s, f"at={at} settled={s}")
    print(f"        ({name} settle drift land->settled = {drift:.1f}px — informational)")
    if exit_pair:
        fa, fb = exit_pair
        ia = iou(_mask(FS[fa], box, kind), _mask(FS[fb], box, kind))
        check(f"{name}: no break-apart at exit (post-settle IoU f{fa}~f{fb})", ia > 0.90, f"IoU={ia:.3f}")

FBED = (700, 540, 1400, 900)
bed_base = max(ink_of(FS[340], FBED, "white"), ink_of(FS[350], FBED, "white"))
census2("WINDOW", (850, 540, 1810, 900), 147, 153, "red", exit_pair=(158, 160))
census2("FROM-L1", (550, 540, 1250, 900), 259, 265, "red", exit_pair=(265, 267))
census2("AROUND", (550, 540, 1600, 900), 308, 312, "red", exit_pair=(312, 313))
census2("FROM-C4", FBED, 366, 372, "white", bed_baseline=bed_base)
fc_pre = ink_of(FS[394], (700, 540, 1400, 900), "white")
fc_at = ink_of(FS[395], (700, 540, 1400, 900), "white")
check("FROM-C4 present full @f394, cleared @f395 (NO landing)", fc_pre > 10000 and fc_at < 0.05 * fc_pre,
      f"f394={fc_pre} f395={fc_at}")
LB = (390, 540, 1190, 900)
c_rest = centroid(_mask(FS[95], LB, "red"))
c_mid = centroid(_mask(FS[85], LB, "red"))
c_exit = centroid(_mask(FS[105], LB, "red"))
d_mid = abs(c_mid[0] - c_rest[0]) + abs(c_mid[1] - c_rest[1])
d_exit = abs(c_exit[0] - c_rest[0]) + abs(c_exit[1] - c_rest[1])
check("LIGHT control: scattered mid-assemble @f85", d_mid > 25, f"drift={d_mid:.1f}px")
check("LIGHT control: breaking at exit @f105", d_exit > 18, f"drift={d_exit:.1f}px")

# ---------------------------------------------------------------- color truth
print("\n== color truth ==")
fb = (700, 540, 1400, 900)
w_cnt = ink_of(FS[370], fb, "white")
r_cnt = ink_of(FS[370], fb, "red")
m = _mask(FS[370], fb, "white")
crop = FS[370][540:900, 700:1400]
med = tuple(int(np.median(crop[..., i][m])) for i in range(3)) if w_cnt else (0, 0, 0)
check("FROM-C4 core is off-white", w_cnt > 12000 and all(abs(med[i] - t) <= 14 for i, t in enumerate((242, 237, 228))),
      f"white={w_cnt} medianRGB={med}")
check("FROM-C4 red-core ~0 in box", r_cnt < 1000, f"red={r_cnt}")
for name, f, box in (("WINDOW", 155, (850, 540, 1810, 900)), ("FROM-L1", 264, (550, 540, 1250, 900)),
                     ("AROUND", 312, (550, 540, 1600, 900)), ("NO", 398, (60, 330, 900, 830)),
                     ("LIGHT", 195 - 100, LB)):
    check(f"{name} red core present @f{f}", ink_of(FS[f], box, "red") > 8000, f"red={ink_of(FS[f], box, 'red')}")
check("WAY red core present @f407 (mid-hold)", int(hero_red(FS[407]).sum()) > 400000, f"red={int(hero_red(FS[407]).sum())}")
check("HEY red core present @f185 (mid-hold)", int(hero_red(FS[185]).sum()) > 200000, f"red={int(hero_red(FS[185]).sum())}")

# ---------------------------------------------------------------- headers
print("\n== headers ==")
for name, f in (("line1", 70), ("compA", 130), ("compB", 175), ("compB-tail", 195),
                ("L1", 240), ("L2", 290), ("C4", 360), ("C4-tail", 420)):
    img = FS[f].astype(np.float32)
    lum = img[64:70, 122:1798].mean(axis=2)
    cols = int((lum > 110).sum(axis=0).astype(bool).sum())
    band = int(((img[28:68].mean(axis=2) > 110)).sum())
    check(f"header present ({name} @f{f})", cols > 900, f"rule-cols={cols} band-bright={band}")

print(f"\n==== {sum(R)}/{len(R)} PASS ====")
sys.exit(0 if all(R) else 1)
