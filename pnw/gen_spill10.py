#!/usr/bin/env python3
"""SPILL v10 -- GIF-BEHAVIOR melt (spec relayed 2026-11-05 00:10, BO's
placidplace blood-drip GIF as the motion reference; original GIF pulled
from the M4 Downloads and frame-studied: 92 frames, 2.76s).

What the GIF does that v9 didn't:
- drips are THICK ROPES (root ~30-50px at our scale), not thin strands;
- each drip tapers gently, swells into a rounded teardrop bulb, NECKS
  just above the bulb as it matures, and the bulb DETACHES and falls;
- the source band's bottom edge is a wavy liquid fringe that recedes
  ragged as liquid drains (erosion), never a straight slice;
- the liquid is glossy dark red: burgundy shadow side, bright specular
  streak down one side, white glint on the bulb.
Kept from v9 (BO's corrections): mixture dye (SAM 3.1 tracked rain
carries the red), glass-boundary masking on all liquid, lyric timing,
clean NORTHWOOD handoff, erosion coupled to dye. Detached droplets
that land in the wet zone SPLAT into the dye field -- the mass that
leaves the letters shows up in the rain.
Frames: comp 678..828. Output: frames-verse2-v21r6mix/.
"""
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
for s in sites[::3]:
    s["Lmax"] = float(rng.uniform(70, 122))
order = np.argsort([s["hw"] for s in sites])[::-1]
for k in order[:4]:
    sites[k]["Lmax"] = float(rng.uniform(148, 185))
    sites[k]["detach"] = True
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
WAVE1 = 1.0 + 0.16 * np.sin(xgrid * 0.006 + 2.0) * np.sin(xgrid * 0.0021 + 0.5)

def front_base(m):
    chan = np.minimum(CHAN_BASE, 1.35)
    return y_bot - m * 0.55 * (y_bot - y_top) * chan * WAVE1

def site_state(s, m, f, root_y):
    """Advance one drip site; root_y = the CURRENT eroded edge at the
    site's column -- drips hang from where the letters actually end."""
    g = (m - s["t0"]) / max(0.05, 1.0 - s["t0"])
    if g <= 0:
        return None
    g = min(1.0, g)
    L = s["Lmax"] * (g ** 1.6)
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
    if s["detach"] and g >= 0.93 and s["state"] == "grow":
        s["state"] = "falling"; s["fall"] = 0.0; s["vel"] = 0.0
    if s["state"] == "falling":
        s["vel"] += 1.15
        s["fall"] += s["vel"]
        L *= 0.94                       # stump snaps back a touch
        bulb_y = root_y + L + s["fall"]
        if bulb_y > GLASS_BOTTOM - 26 and not s["landed"]:
            s["landed"] = True
            if OX + 10 < s["x"] < OX + 1270:
                SPLATS.append((s["x"], bulb_y, f))
        if bulb_y < GLASS_BOTTOM - 4:
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
        if st["pinch_u"] is not None:
            w *= 1.0 - st["pinch_amt"] * np.exp(-((u - st["pinch_u"]) / 0.055) ** 2)
            if u > st["pinch_u"]:                              # teardrop bulb
                w = hw * (0.72 + 0.33 * np.sin((u - st["pinch_u"])
                                               / max(0.02, 1 - st["pinch_u"]) * np.pi * 0.5))
        y = root + (L + 26) * u
        left.append((s["x"] - w, y)); right.append((s["x"] + w, y))
    return left, right, root

def draw_liquid(dd, states, alpha_scale):
    for s, st in states:
        a = int(238 * alpha_scale)
        left, right, root = profile_pts(s, st)
        poly = left + right[::-1]
        dd.polygon([(x + 2.2, y) for x, y in poly], fill=OUTLINE + (a,))
        dd.polygon([(x - 2.2, y) for x, y in poly], fill=OUTLINE + (a,))
        dd.polygon(poly, fill=BODY + (a,))
        # specular streak down the left-center of the rope
        hw = s["hw"]
        pts = [(s["x"] - hw * 0.38 * (1 - 0.18 * np.sin((i / 26) * np.pi * 0.62)),
                root + (st["L"] + 26) * (i / 26)) for i in range(27)]
        dd.line(pts, fill=SPEC + (int(a * 0.35),), width=max(3, int(hw * 0.34)))
        dd.line(pts, fill=SPEC_CORE + (int(a * 0.45),), width=2)
        # bulb glint
        tip_y = root + st["L"] + 26
        r = hw * 0.5
        dd.ellipse([s["x"] - r * 0.9, tip_y - r * 1.15, s["x"] - r * 0.05,
                    tip_y - r * 0.3], fill=(255, 244, 238, int(a * 0.75)))
        if st["drop"]:
            d = st["drop"]
            r = d["r"]
            dd.ellipse([d["x"] - r, d["y"] - r * 1.25, d["x"] + r,
                        d["y"] + r * 0.9], fill=BODY + (a,))
            dd.ellipse([d["x"] - r * 0.55, d["y"] - r * 1.05,
                        d["x"] - r * 0.08, d["y"] - r * 0.55],
                       fill=(255, 244, 238, int(a * 0.7)))

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
    frame = plate.convert("RGBA")
    wa = word_alpha(f)
    if wa > 0:
        mb = m * 0.19
        disp = mb * run * ((np.clip(ygrid - y_top, 0, None) /
                            max(1, (y_bot - y_top))) ** 1.9) * 300 + m * 5
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
            front = y_bot - m * 0.55 * (y_bot - y_top) * chan * wave
            soft = np.clip((front - ygrid) / 10.0 + 0.5, 0, 1)
            out[:, :, 3] *= soft
        word = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")
        s = punch(f)
        if abs(s - 1.0) > 0.001:
            nw, nh = int(W * s), int(H * s)
            word = word.resize((nw, nh), Image.LANCZOS)
            canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            canvas.alpha_composite(word, (int(24 - 24 * s), int(714 - 714 * s)))
            word = canvas
        frame = Image.alpha_composite(frame, word)
    if states:
        dl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(dl)
        if m > 0.05 and f <= 752:
            # FRINGE BAND (the GIF's connecting liquid edge): a wavy
            # band welded along the eroding bottom, reaching deeper
            # where drips feed -- word and drips read as ONE liquid.
            chan1 = 0.45 + 1.1 * (run[0] ** 2) \
                * (0.85 + 0.30 * np.sin(xgrid * 0.021 + 1.0)
                   * np.sin(xgrid * 0.007 + 3.0))
            prox1 = np.zeros(W, dtype=np.float32)
            for s, st in states:
                prox1 += (st["L"] / max(1.0, s["Lmax"])) \
                    * np.exp(-((xgrid - s["x"]) ** 2) / (2 * 64.0 ** 2))
            chan1 = chan1 * (1.0 + 0.38 * np.clip(prox1, 0, 1))
            chan1 = np.minimum(chan1, 1.35)
            wave1 = WAVE1
            front1 = y_bot - m * 0.55 * (y_bot - y_top) * chan1 * wave1
            xs_b = np.arange(int(cols_with.min()), int(cols_with.max()), 6)
            top = [(float(x), float(front1[x])) for x in xs_b]
            bot = [(float(x), float(front1[x] + 12 + 26 * np.clip(prox1[x], 0, 1)
                                    + 7 * np.sin(x * 0.02))) for x in xs_b[::-1]]
            dd.polygon(top + bot, fill=BODY + (int(215 * (md if f > 743 else 1.0)),))
        draw_liquid(dd, states,
                    alpha_scale=md if f > 743 else 1.0)
        dl = dl.filter(ImageFilter.GaussianBlur(0.6))
        darr = np.asarray(dl).astype(np.float32)
        darr[:, :, 3] *= GLASS
        dl = Image.fromarray(np.clip(darr, 0, 255).astype(np.uint8), "RGBA")
        frame = Image.alpha_composite(frame, dl)
    frame.convert("RGB").save(OUT / f"f{f:04d}.png")
    if f % 30 == 0:
        print("mixed", f, "m", round(m, 2), "states", len(states),
              "splats", len(SPLATS))
print("spill v10 done")
