#!/usr/bin/env python3
"""SPILL v10.7 -- OVERRIDE SPEC (BO, 2026-11-05 01:00). Flat graphic, locked to the glass. (1) Horizontal cut DELETED: erosion front is prox-only (stems), fringe gated to stem columns, noise drain removed -- letter tops and inter-stem bottoms stay solid. (2) L-stem starts staggered 2-4f. (3) Midpoint waist pinch on stems. (4) Travel clamped 120-180px: beads ease OUT to a stop ON the glass, then fade to zero as NORTHWOOD lands (f744-758). Nothing falls off-screen, no bottom splats. (5) Liquid is FLAT #D81E1E -- no bevel, glow, or specular -- and the only warp is a 2-4px displacement of the plate behind the text, driven by the liquid field gradient. Base: v10.6 conduits."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

WDIR = Path("/Volumes/STICK/BrickHouse/lyric-type-2026-10-31/pnw-2026-11-04")
PLATE = WDIR / "frames-verse2-v21r6clean"
OUT = WDIR / "frames-verse2-v21r6mix"
OUT.mkdir(exist_ok=True)
SAM = Path("/tmp/sam-full")
W, H = 1920, 1080
OX, OY = 320, 180
FONT = "/Users/brickhousestudios/Library/Fonts/Anton-Regular.ttf"
TEXT, SIZE, POS = "SPILLLLLLLLLL", 406, (24, 714)
RED = np.array([255, 59, 31], dtype=np.float32)
BODY = (178, 22, 10)
OUTLINE = (110, 8, 4)
SPEC = (255, 176, 156)
SPEC_CORE = (255, 236, 226)

def mask_at(sidx):
    p = SAM / f"frame-{sidx:03d}.png"
    m = np.zeros((H, W), dtype=np.float32)
    if p.exists():
        m[OY:OY + 720, OX:OX + 1280] = (
            np.asarray(Image.open(p).convert("L"), dtype=np.float32) / 255.0)
    return m

def dye_field(sidx):
    mk = mask_at(sidx)
    halo = np.asarray(Image.fromarray((mk * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(14)), dtype=np.float32) / 255.0
    trail = np.zeros((H, W), dtype=np.float32)
    for ds in (-6, -4, -2, 0, 2, 4, 6):
        trail = np.maximum(trail, mask_at(max(7, min(140, sidx + ds))))
    trail = np.asarray(Image.fromarray((trail * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(8)), dtype=np.float32) / 255.0
    return np.maximum(np.maximum(mk, halo * 0.85), trail * 0.8), mk

acc = None
for p in sorted(SAM.glob("frame-*.png")):
    mm = np.asarray(Image.open(p).convert("L"), dtype=np.float32) / 255.0
    acc = mm if acc is None else np.maximum(acc, mm)
wet_img = Image.fromarray((acc * 255).astype(np.uint8)).filter(
    ImageFilter.MaxFilter(21)).filter(ImageFilter.GaussianBlur(10))
WET = np.zeros((H, W), dtype=np.float32)
WET[OY:OY + 720, OX:OX + 1280] = np.asarray(wet_img, dtype=np.float32) / 255.0

img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(img).text(POS, TEXT, font=ImageFont.truetype(FONT, SIZE),
                         fill=(255, 59, 31, 255), anchor="ls")
base = np.asarray(img).astype(np.float32)
alpha0 = base[:, :, 3]
ys, xs = np.nonzero(alpha0 > 0)
y_top, y_bot = int(ys.min()), int(ys.max())
rng = np.random.default_rng(20261105)
xgrid = np.arange(W, dtype=np.float32)
riv = (0.5 + 0.28 * np.sin(xgrid * 0.011 + 1.7) * np.sin(xgrid * 0.0043 + 0.4)
       + 0.22 * np.sin(xgrid * 0.031 + 4.1))
for _ in range(16):
    c = rng.uniform(60, 1980)
    wdt = rng.uniform(5, 17)
    riv += rng.uniform(0.35, 0.75) * np.exp(-((xgrid - c) ** 2) / (2 * wdt ** 2))
riv = np.clip(riv, 0.12, 1.0).astype(np.float32)
run = (0.18 + 0.82 * riv)[None, :]
ygrid = np.arange(H, dtype=np.float32)[:, None]
depth = np.clip((ygrid - y_top) / max(1, (y_bot - y_top)), 0, 1)

# ---- drip sites from the word's own bottom profile ------------------
ybot_col = np.full(W, y_top, dtype=np.float32)
cols_with = np.nonzero((alpha0 > 0).any(axis=0))[0]
ink_cols = cols_with
for x in cols_with:
    ybot_col[x] = np.nonzero(alpha0[:, x] > 0)[0].max()
# contiguous ink runs near the bottom = letter bottoms
row = alpha0[y_bot - 6, :] > 0
runs = []
inrun = False
for x in range(W):
    if row[x] and not inrun:
        start = x; inrun = True
    elif not row[x] and inrun:
        runs.append((start, x - 1)); inrun = False
if inrun:
    runs.append((start, W - 1))
sites = []
for (a, b) in runs:
    cx = (a + b) / 2 + float(rng.uniform(-14, 14))
    sites.append({"x": float(cx),
                  "root_y": float(ybot_col[int(round(cx))]),
                  "t0": float(rng.uniform(0.05, 0.48)),
                  "hw": float(rng.uniform(16, 27)),
                  "detach": False, "state": "grow", "fall": 0.0,
                  "vel": 0.0, "landed": False})
for cx in sorted(rng.choice(ink_cols, size=5, replace=False).tolist()):
    sites.append({"x": float(cx),
                  "root_y": float(ybot_col[int(cx)]),
                  "t0": float(rng.uniform(0.10, 0.55)),
                  "hw": float(rng.uniform(13, 20)),
                  "detach": False, "state": "grow", "fall": 0.0,
                  "vel": 0.0, "landed": False})
# GIF length distribution: many stubs, some mids, FEW dominant runners
for s in sites:
    s["Lmax"] = float(rng.uniform(25, 62))
    s["detach_g"] = float(rng.uniform(0.86, 0.99))   # staggered separation
    s["accel"] = 1.3
for s in sites[::3]:
    s["Lmax"] = float(rng.uniform(70, 122))
    s["accel"] = 1.15
order = np.argsort([s["hw"] for s in sites])[::-1]
for k in order[:4]:
    sites[k]["Lmax"] = float(rng.uniform(148, 185))
    sites[k]["detach"] = True
    sites[k]["detach_g"] = 0.93
    sites[k]["accel"] = 1.5
for k in order[:3]:                      # TIER 1: heavy anchors
    sites[k]["Lmax"] = float(rng.uniform(200, 240))
    sites[k]["anchor"] = True
    sites[k]["accel"] = 2.3
    sites[k]["detach_g"] = 0.90

# ---- v10.6 CONDUIT REGISTRY: 8 stems on letter anatomy, x order
# S-Trough, P-Stem, L1..L6/7 feet. (mass, start, snap) preview frames.
REGISTRY = [(0.80, 36, 47), (1.00, 31, 41), (0.75, 33, 44),
            (0.50, 35, 46), (0.95, 38, 49), (0.45, 41, 52),
            (0.70, 44, 55), (0.60, 47, 58)]
_xs = sorted(range(len(sites)), key=lambda i: sites[i]["x"])
for _rank, _i in enumerate(_xs[:8]):
    _mass, _st, _sn = REGISTRY[_rank]
    sites[_i].update({"conduit": True, "mass": _mass,
                      "f_start": 678 + _st, "f_snap": 678 + _sn,
                      "Lmax": 62.0 + 108.0 * _mass, "accel": 3.2,
                      "anchor": False, "detach_g": 2.0})
print("sites:", len(sites), "runs:", len(runs))

zone_ramp = np.clip((ygrid - 300) / 180.0, 0, 1)
band = ((ygrid >= y_top - 20) & (ygrid <= y_bot)).astype(np.float32)
gx = np.clip((np.arange(W, dtype=np.float32)[None, :] - (OX - 6)) / 12.0, 0, 1) \
    * np.clip(((OX + 1280 + 6) - np.arange(W, dtype=np.float32)[None, :]) / 12.0, 0, 1)
gy = np.clip((ygrid - (OY - 6)) / 12.0, 0, 1) * np.clip(((OY + 720 + 6) - ygrid) / 12.0, 0, 1)
GLASS = (gx * gy).astype(np.float32)
GLASS_BOTTOM = OY + 720

def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)

def m_word(f):
    return float(smooth(700, 738, f))

def word_alpha(f):
    if f < 700:
        return 0.0
    return float(1 - smooth(736, 743, f))

def m_dye(f):
    if f <= 743:
        return float(smooth(700, 730, f))
    return float(max(0.15, 1 - (f - 743) / 85.0 * 0.85))

PUNCH = [(700, 108.0), (705, 104.2), (710, 101.6), (715, 100.3), (739, 100.0)]
def punch(f):
    if f <= 700:
        return 1.08
    for (f0, v0), (f1, v1) in zip(PUNCH, PUNCH[1:]):
        if f0 <= f <= f1:
            return (v0 + (v1 - v0) * (f - f0) / (f1 - f0)) / 100.0
    return 1.0

SPLATS = []  # (x, y, f_land) -- detached mass handed to the rain

# erosion front WITHOUT the prox coupling (drips root here; the word's
# own erosion adds prox on top inside the frame loop)
CHAN_BASE = 0.45 + 1.1 * (run[0] ** 2) \
    * (0.85 + 0.30 * np.sin(xgrid * 0.021 + 1.0) * np.sin(xgrid * 0.007 + 3.0))
WAVE1 = 1.0 + 0.10 * np.sin(xgrid * 0.006 + 2.0) * np.sin(xgrid * 0.0021 + 0.5)

PROX_S = np.zeros(W, dtype=np.float32)
for _s in sites:
    PROX_S += (_s["Lmax"] / 240.0) * np.exp(
        -((xgrid - _s["x"]) ** 2) / (2 * 70.0 ** 2))
PROX_S = np.clip(PROX_S, 0, 1)


_NF = []
for _kw in (90, 45, 22, 11):
    _r = rng.random(W).astype(np.float32)
    _k = np.exp(-0.5 * (np.arange(-_kw * 2, _kw * 2 + 1) / _kw) ** 2)
    _k /= _k.sum()
    _NF.append(np.convolve(_r, _k, mode="same"))


def drain_noise(f):
    """Evolving fractal drain: 4 octaves, rotating weights, choked
    95-120 so the front breaks into descending cellular filaments."""
    n = np.zeros(W, dtype=np.float32)
    ws = 0.0
    for k, fld in enumerate(_NF):
        w = 0.55 + 0.45 * np.sin(2 * np.pi * f / (26.0 * (k + 1)) + k * 1.7)
        n += w * fld
        ws += w
    n /= ws
    n = (n - n.min()) / max(1e-6, n.max() - n.min())
    return np.clip((n - 0.37) / 0.10, 0, 1)


def front_base(m):
    chan = np.minimum(CHAN_BASE, 1.35)
    depth = np.clip(0.92 * PROX_S * (0.55 + 0.45 * chan), 0, 1.25)
    return y_bot - m * 0.55 * (y_bot - y_top) * depth

# ---- Phase C/D residue: beads clinging to the rain paths ------------
BEADS = []
_fb1 = front_base(1.0)
for s in sites:
    if len(BEADS) >= 12:
        break
    if not (OX + 30 < s["x"] < OX + 1250):
        continue
    lo = max(0, int(s["x"]) - 40); hi = min(W - 1, int(s["x"]) + 40)
    bx = lo + int(np.argmax(run[0, lo:hi]))          # snap to the rivulet
    BEADS.append({"x": float(bx),
                  "y0": float(_fb1[bx] + rng.uniform(8, 64)),
                  "f0": int(rng.integers(744, 763)),
                  "speed": float(rng.uniform(1.5, 4.0)),
                  "r": float(rng.uniform(5, 11))})
# ---- fringe breakup gaps (seeded) ------------------------------------
GAPS = [(float(rng.uniform(80, 1860)), float(rng.uniform(26, 62)))
        for _ in range(13)]

def breakup(f):
    return float(smooth(736, 746, f))

def site_state(s, m, f, root_y):
    """Advance one drip site; root_y = the CURRENT eroded edge at the
    site's column -- drips hang from where the letters actually end."""
    if s.get("conduit") and f < s["f_start"]:
        return None
    g = (m - s["t0"]) / max(0.05, 1.0 - s["t0"])
    if g <= 0 and not s.get("conduit"):
        return None
    g = min(1.0, max(0.0, g))
    L = s["Lmax"] * (g ** 1.6)
    if s.get("conduit"):
        u_c = min(1.0, max(0.0, (f - s["f_start"])
                           / max(1, s["f_snap"] - s["f_start"])))
        L = s["Lmax"] * (0.15 * u_c + 0.85 * u_c ** 3)  # cubic stretch
        g = u_c                                          # pinch reads u
    if f > 743:  # after the word clears, attached liquid DRAINS away --
        drain = max(0.0, 1 - (f - 743) / 20.0)   # only dye + droplets remain
        L *= drain
        if drain <= 0.03 and s["state"] == "grow":
            return None
    L = min(L, GLASS_BOTTOM - 8 - root_y)
    if L < 6:
        return None
    pinch_u, pinch_amt = None, 0.0
    if g > 0.78:
        pinch_u = 0.90 - 0.06 * (g - 0.78) / 0.22
        pinch_amt = 0.30 * (g - 0.78) / 0.22
    drop = None
    if (g >= s["detach_g"] or (s.get("conduit") and f >= s["f_snap"])) \
            and s["state"] == "grow":
        s["state"] = "falling"; s["fall"] = 0.0; s["vel"] = 0.0
        s["f_detach"] = f
        if s.get("anchor"):
            # slipstream: two smaller beads follow the anchor down
            for j in (-1, 1):
                BEADS.append({"x": float(s["x"] + j * rng.uniform(8, 22)),
                              "y0": float(root_y + L * 0.75),
                              "f0": int(f + rng.integers(2, 6)),
                              "speed": float(rng.uniform(5.0, 7.0)),
                              "r": float(rng.uniform(5, 8))})
    if s["state"] == "falling":
        # OVERRIDE: travel clamped to 120-180px, ease-OUT to a full
        # stop ON the glass. Nothing leaves the pane; no splats.
        if "fall_D" not in s:
            s["fall_D"] = 120.0 + 60.0 * (s.get("mass")
                                          or min(1.0, s["Lmax"] / 200.0))
            s["fall_T"] = 0
        s["fall_T"] += 1
        u_f = min(1.0, s["fall_T"] / 16.0)
        s["fall"] = s["fall_D"] * (1 - (1 - u_f) ** 2)
        retract = max(0.0, 1 - (f - s.get("f_detach", f))
                      / (4.0 if s.get("conduit") else 10.0))
        L *= 0.94 * (retract ** 0.5)    # stump snaps back, then is gone
        bulb_y = root_y + L + s["fall"]
        bulb_y = min(bulb_y, GLASS_BOTTOM - 12)
        drop = {"x": s["x"], "y": bulb_y, "r": s["hw"] * 1.18,
                "fade": 1.0}
    return {"g": g, "L": L, "pinch_u": pinch_u, "pinch_amt": pinch_amt,
            "drop": drop, "root_y": root_y}

def profile_pts(s, st):
    """(left, right) outline points of the attached drip, root->tip."""
    L, hw = st["L"], s["hw"]
    root = st["root_y"] - 26         # root buried inside the letter
    n = 26
    left, right = [], []
    for i in range(n + 1):
        u = i / n
        w = hw * (1.0 - 0.18 * np.sin(u * np.pi * 0.62))       # gentle taper
        if s.get("conduit"):
            gu = st["g"]
            if u < 0.62:
                w *= 1.05 - 0.35 * gu
            # MIDPOINT WAIST: pinch at the stem's center, bulb below
            w *= 1.0 - 0.48 * gu * np.exp(-((u - 0.50) / 0.13) ** 2)
            if u > 0.62:          # bulb keeps the mass
                w *= 0.95 + 0.30 * s.get("mass", 0.7)
        if st["pinch_u"] is not None:
            w *= 1.0 - st["pinch_amt"] * np.exp(-((u - st["pinch_u"]) / 0.055) ** 2)
            if u > st["pinch_u"]:                              # teardrop bulb
                w = hw * (0.72 + 0.33 * np.sin((u - st["pinch_u"])
                                               / max(0.02, 1 - st["pinch_u"]) * np.pi * 0.5))
        y = root + (L + 26) * u
        left.append((s["x"] - w, y)); right.append((s["x"] + w, y))
    return left, right, root

# ------------------------------------------------------------------
# v10.5 liquid pipeline: density field -> blur -> alpha threshold.
# Shapes weld where they overlap (surface tension); thin necks snap.
# ------------------------------------------------------------------
TRAIL = np.zeros((H, W), dtype=np.float32)
SPLATTER = []
for _ in range(46):                       # TIER 3: micro-splatter
    SPLATTER.append({"x": int(rng.uniform(OX + 26, OX + 1254)),
                     "y": int(rng.uniform(430, 880)),
                     "r": float(rng.uniform(1.5, 3.6)),
                     "f0": int(rng.integers(716, 752)),
                     "a": int(rng.integers(45, 95))})


def draw_field(states, f, m):
    """Draw every liquid shape into a uint8 density field image."""
    fld = Image.new("L", (W, H), 0)
    dd = ImageDraw.Draw(fld)
    if m > 0.05 and f <= 746:
        # fringe band (chunked, v10.4 breakup gaps), welded UP into
        # the word's eroded bottom so the blur bridges the seam
        chan1 = 0.45 + 1.1 * (run[0] ** 2) \
            * (0.85 + 0.30 * np.sin(xgrid * 0.021 + 1.0)
               * np.sin(xgrid * 0.007 + 3.0))
        prox1 = np.zeros(W, dtype=np.float32)
        for s, st in states:
            prox1 += (st["L"] / max(1.0, s["Lmax"])) \
                * np.exp(-((xgrid - s["x"]) ** 2) / (2 * 64.0 ** 2))
        chan1 = np.minimum(chan1 * (1.0 + 0.38 * np.clip(prox1, 0, 1)), 1.35)
        depth1 = np.clip(0.20 * chan1 * WAVE1
                         + 0.85 * PROX_S * (0.55 + 0.45 * chan1), 0, 1.25)
        front1 = y_bot - m * 0.55 * (y_bot - y_top) * depth1
        b = breakup(f)
        x0, x1 = int(cols_with.min()), int(cols_with.max())
        for xc in range(x0, x1, 30):
            gapd = 0.0
            for (gx_, gw_) in GAPS:
                gapd = max(gapd, np.exp(-((xc + 15 - gx_) / gw_) ** 2))
            if b * gapd > 0.88 or prox1[xc] < 0.16:
                continue
            xs_c = np.arange(xc, min(xc + 30, x1) + 1, 6)
            reach = (12 + 26 * np.clip(prox1[xc], 0, 1)) * (1 - 0.7 * b)
            top = [(float(x), float(front1[x] - 16)) for x in xs_c]
            bot = [(float(x), float(front1[x] + reach
                                    + 7 * np.sin(x * 0.02))) for x in xs_c[::-1]]
            dd.polygon(top + bot, fill=205)
    for wscale, val in ((1.0, 190), (0.58, 255)):
        for s, st in states:
            left, right, root = profile_pts(s, st)
            cl = [(s["x"] + (px - s["x"]) * wscale, py) for px, py in left]
            cr = [(s["x"] + (px - s["x"]) * wscale, py) for px, py in right]
            dd.polygon(cl + cr[::-1], fill=val)
            tip_y = root + st["L"] + 20
            r = s["hw"] * 0.55 * wscale
            dd.ellipse([s["x"] - r, tip_y - r, s["x"] + r, tip_y + r],
                       fill=val)
    fade = 1.0 - float(smooth(744, 758, f))   # out as NORTHWOOD lands
    for s, st in states:      # falling drops: slight smear, then fade
        d = st["drop"]
        if d is None or fade <= 0.02:
            continue
        vel = 5.0
        for k, val in ((2, 90), (1, 160), (0, 255)):
            yy = d["y"] - vel * 0.42 * k
            r = d["r"] * (1 - 0.10 * k)
            dd.ellipse([d["x"] - r * 0.85, yy - r * 1.1,
                        d["x"] + r * 0.85, yy + r * 0.95],
                       fill=int(val * fade))
    for bd in BEADS:          # beads: rain sliders + slipstream
        age = f - bd["f0"]
        if age < 0:
            continue
        y = bd["y0"] + bd["speed"] * age
        if y > GLASS_BOTTOM - 16 or age > 52:
            continue
        y = min(y, bd["y0"] + 170.0)          # travel clamp
        r = bd["r"]
        dd.ellipse([bd["x"] - r * 0.8, y - r * 1.15, bd["x"] + r * 0.8,
                    y + r * 0.85], fill=int(225 * fade))
    return fld


def build_liquid(fld, bed_lum=None):
    """Blur + threshold; FLAT #D81E1E (override spec: no bevel, no
    glow, no specular -- a graphic shape locked to the glass)."""
    fb = np.asarray(fld.filter(ImageFilter.GaussianBlur(9))).astype(np.float32)
    t = np.clip((fb - 112.0) / 28.0, 0, 1)
    alpha = (t * 255).astype(np.uint8)
    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    rgb[:, :, 0] = 216; rgb[:, :, 1] = 30; rgb[:, :, 2] = 30
    return Image.fromarray(np.dstack([rgb, alpha]), "RGBA")


def refract(arr, drops):
    """Bend the plate a few px under each falling drop (lens warp)."""
    dx = np.zeros((H, W), dtype=np.float32)
    dy = np.zeros((H, W), dtype=np.float32)
    for d in drops:
        r = d["r"] * 2.1
        x0 = max(0, int(d["x"] - r)); x1 = min(W, int(d["x"] + r))
        y0 = max(0, int(d["y"] - r)); y1 = min(H, int(d["y"] + r))
        if x1 <= x0 or y1 <= y0:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1]
        wgt = np.exp(-(((xx - d["x"]) / r) ** 2
                       + ((yy - d["y"]) / r) ** 2) * 2.2)
        dx[y0:y1, x0:x1] += (xx - d["x"]) * 0.21 * wgt
        dy[y0:y1, x0:x1] += (yy - d["y"]) * 0.21 * wgt + 3.4 * wgt
    xi = np.clip(np.arange(W)[None, :] - dx, 0, W - 1).astype(np.int32)
    yi = np.clip(np.arange(H)[:, None] - dy, 0, H - 1).astype(np.int32)
    return arr[yi, xi]


def sag_warp(rgba, pool):
    """Pool phase: bottom rows sag (rivulet-weighted), tops thin."""
    arr = np.asarray(rgba).astype(np.float32)
    yy = np.arange(H, dtype=np.float32)[:, None]
    band = np.clip((yy - (y_bot - 95)) / 135.0, 0, 1) ** 1.5
    off = pool * 11.0 * band * (0.55 + 0.7 * run[0][None, :])
    yi = np.clip(yy - off, 0, H - 1).astype(np.int32)
    xi = np.arange(W, dtype=np.int32)[None, :]
    out = arr[yi, xi]
    topness = np.clip(1 - (yy - y_top) / (y_bot - y_top), 0, 1)
    out[:, :, 3] *= (1 - 0.22 * pool * topness)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


for f in range(678, 829):
    plate = Image.open(PLATE / f"f{f:04d}.png").convert("RGB")
    m = m_word(f)
    # advance drip physics FIRST so landings feed this frame's dye;
    # roots ride the erosion front (post-743 they slide down the glass)
    states = []
    if f >= 700:
        fb = front_base(m if f <= 743 else 1.0)
        for s in sites:
            ry = float(fb[int(round(s["x"]))]) - 8
            if f > 743:
                ry += (f - 743) * 6.0
            st = site_state(s, m if f <= 743 else 1.0, f, ry)
            if st:
                states.append((s, st))
    md = m_dye(f)
    if md > 0:
        arr = np.asarray(plate).astype(np.float32)
        sidx = int(round((f - 590) * 0.8))
        sidx = max(7, min(140, sidx))
        mk, _sharp = dye_field(sidx)
        spread = 30 + md * 520
        below = np.clip(1 - np.maximum(0.0, ygrid - y_bot) / spread, 0, 1)
        boost = 1 + 0.6 * np.clip(1 - np.abs(ygrid - (y_bot + 30)) / 90.0, 0, 1)
        wgt = zone_ramp * np.maximum(band, below) * boost
        eroded_frac = m * 0.55 if f <= 743 else 0.55
        k = (mk * wgt * (0.25 + 0.75 * md) * (0.7 + 0.6 * eroded_frac))[:, :, None]
        # detached-droplet splats: mass arrives in the rain
        for (sx, sy, fl) in SPLATS:
            age = f - fl
            if 0 <= age <= 40:
                splat = np.exp(-(((xgrid[None, :] - sx) / 30.0) ** 2)
                               - (((ygrid - sy) / 55.0) ** 2)) \
                    * (1 - age / 40.0) * 0.5
                k = k + splat[:, :, None] * md
        k = np.clip(k, 0, 1) * GLASS[:, :, None]
        lum = (0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1]
               + 0.114 * arr[:, :, 2]) / 255.0
        dye = RED[None, None, :] * (0.35 + 0.85 * lum[:, :, None])
        hot = np.clip(lum - 0.72, 0, 1) * 1.2
        dye = dye + hot[:, :, None] * 255.0
        arr = arr * (1 - k) + dye * k
        plate = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    drops_now = [st["drop"] for s, st in states if st["drop"]]
    # WET TRAILS: drops and beads deposit; the field decays ~15 frames
    TRAIL *= 0.962
    if drops_now or states:
        tmp = Image.new("L", (W, H), 0)
        td = ImageDraw.Draw(tmp)
        for d in drops_now:
            r = d["r"] * 1.7
            td.ellipse([d["x"] - r * 0.7, d["y"] - r, d["x"] + r * 0.7,
                        d["y"] + r], fill=150)
        for bd in BEADS:
            age = f - bd["f0"]
            if 0 <= age <= 52:
                y = bd["y0"] + bd["speed"] * age
                if y < GLASS_BOTTOM - 16:
                    td.ellipse([bd["x"] - 5, y - 7, bd["x"] + 5, y + 7],
                               fill=80)
        TRAIL[:] = np.clip(TRAIL + np.asarray(tmp, dtype=np.float32)
                           / 255.0 * 0.55, 0, 1)
    if TRAIL.max() > 0.02 or f >= 716:
        tl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        td2 = ImageDraw.Draw(tl)
        for sp in SPLATTER:
            if f >= sp["f0"]:
                td2.ellipse([sp["x"] - sp["r"], sp["y"] - sp["r"],
                             sp["x"] + sp["r"], sp["y"] + sp["r"]],
                            fill=BODY + (sp["a"],))
        tarr = np.asarray(tl).astype(np.float32)
        tarr[:, :, 0] = 216; tarr[:, :, 1] = 30; tarr[:, :, 2] = 30
        _sm = np.zeros_like(TRAIL)
        for _k in range(0, 44, 4):      # 45px vertical smear, decaying
            _sm = np.maximum(_sm, np.roll(TRAIL, _k, axis=0) * (1 - _k / 62.0))
        tarr[:, :, 3] = np.maximum(tarr[:, :, 3],
                                   np.clip(_sm, 0, 1) * 68)
        tarr[:, :, 3] *= GLASS
        tl = Image.fromarray(np.clip(tarr, 0, 255).astype(np.uint8),
                             "RGBA").filter(ImageFilter.GaussianBlur(1.2))
        plate = Image.alpha_composite(plate.convert("RGBA"), tl).convert("RGB")
    frame = plate.convert("RGBA")
    wa = word_alpha(f)
    if wa > 0:
        mb = m * 0.19
        disp = mb * run * ((np.clip(ygrid - y_top, 0, None) /
                            max(1, (y_bot - y_top))) ** 1.9) * 130 + m * 5
        src = np.clip(np.round(ygrid - disp).astype(np.int32), 0, H - 1)
        out = np.take_along_axis(base, src[:, :, None], axis=0)
        out[:, :, 3] *= (1 - m * (depth ** 1.5) * 0.45 - m * WET * 0.18)
        out[:, :, 3] *= (1 - 0.18 * m * m) * wa
        if m > 0:
            chan = 0.45 + 1.1 * (run ** 2) \
                * (0.85 + 0.30 * np.sin(xgrid * 0.021 + 1.0)[None, :]
                   * np.sin(xgrid * 0.007 + 3.0)[None, :])
            # drip-coupled erosion: columns feeding a long drip lose more
            prox = np.zeros(W, dtype=np.float32)
            for s, st in states:
                prox += (st["L"] / max(1.0, s["Lmax"])) \
                    * np.exp(-((xgrid - s["x"]) ** 2) / (2 * 64.0 ** 2))
            chan = chan * (1.0 + 0.38 * np.clip(prox, 0, 1)[None, :])
            chan = np.minimum(chan, 1.35)
            wave = 1.0 + 0.16 * np.sin(xgrid * 0.006 + 2.0)[None, :] \
                * np.sin(xgrid * 0.0021 + 0.5)[None, :]
            depth_w = np.clip(0.92 * np.clip(prox, 0, 1)[None, :]
                                * (0.55 + 0.45 * chan), 0, 1.25)
            front = y_bot - m * 0.55 * (y_bot - y_top) * depth_w
            soft = np.clip((front - ygrid) / 10.0 + 0.5, 0, 1)
            out[:, :, 3] *= soft
        word = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
        pool = float(smooth(704, 724, f)) * (1 - float(smooth(726, 740, f)))
        if pool > 0.01 and m < 0.35:
            word = sag_warp(word, pool)
        s = punch(f)
        if abs(s - 1.0) > 0.001:
            nw, nh = int(W * s), int(H * s)
            word = word.resize((nw, nh), Image.LANCZOS)
            canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            canvas.alpha_composite(word, (int(24 - 24 * s), int(714 - 714 * s)))
            word = canvas
        frame = Image.alpha_composite(frame, word)
    if states or f >= 744:
        fld = draw_field(states, f, m)
        # subtle 2-4px warp of the plate directly behind the liquid,
        # driven by the field's own gradient (override spec point 5)
        _fb = np.asarray(fld.filter(ImageFilter.GaussianBlur(9)),
                         dtype=np.float32) / 255.0
        if _fb.max() > 0.05:
            _gx = np.gradient(_fb, axis=1)
            _gy = np.gradient(_fb, axis=0)
            _dx = np.clip(_gx * 550.0, -4, 4)
            _dy = np.clip(_gy * 550.0, -4, 4)
            _xi = np.clip(np.arange(W)[None, :] - _dx, 0, W - 1).astype(np.int32)
            _yi = np.clip(np.arange(H)[:, None] - _dy, 0, H - 1).astype(np.int32)
            _base = np.asarray(frame.convert("RGB"))[_yi, _xi]
            _keep = np.asarray(frame)[:, :, 3]
            frame = Image.fromarray(np.dstack([_base, _keep]), "RGBA")
        liq = build_liquid(fld)
        larr = np.asarray(liq).astype(np.float32)
        if f > 743:
            larr[:, :, 3] *= md
        larr[:, :, 3] *= GLASS
        liq = Image.fromarray(np.clip(larr, 0, 255).astype(np.uint8), "RGBA")
        frame = Image.alpha_composite(frame, liq)
    frame.convert("RGB").save(OUT / f"f{f:04d}.png")
    if f % 30 == 0:
        print("mixed", f, "m", round(m, 2), "states", len(states),
              "splats", len(SPLATS))
print("spill v10 done")
