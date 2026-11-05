#!/usr/bin/env python3
"""Sunrise core frames for PNW verse1 (post-composite over bed-only render).

A three.js-style glow sun swelling out of the tunnel's vanishing point:
pale-gold core -> hero-red corona, slow noise shimmer. Timeline (comp
frames @30fps, verse1 starts song 35.2s): kindle f48-60 ("till the sun"),
swell f60-80 ("sun come UP" -- UP lands f76), peak f80-88, FADE f88-105,
gone after f105. SHORTENED 2026-11-04 23:34 per review of the actual
clip: the sun punctuates UP only; it does not follow later lyrics (the
earlier dawn-hold to f180/f250 still dominated at clip 5.25s).
SHAPE v4 (2026-11-05 00:02, BO on ChatGPT's version: 'we want it
right'): NO disc at all -- a pure soft BLOOM like tunnel light: warm
pale core, gaussian falloff, no rim, dimmer than v3 (never blows out),
centered (1150, 500) at the P's right edge. Envelope kept: kindle
f48-62, swell to peak f80-88, fade f88-108, gone after f108.
Output: sun-frames/sun-f%04d.png for comp frames 40..250 (RGBA 1920x1080).
"""
import numpy as np
from PIL import Image
from pathlib import Path

OUT = Path("/tmp/sun-frames")
OUT.mkdir(exist_ok=True)
W, H = 1920, 1080
CX, CY = 1100, 485
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2)
rng = np.random.default_rng(41)
# angular shimmer profile (static noise, pulsed by phase)
ang = np.arctan2(yy - CY, xx - CX)
shimmer_base = (0.5 + 0.5 * np.sin(ang * 9 + 1.3) * np.sin(ang * 23 + 4.0)
                + 0.35 * np.sin(ang * 41 + 2.2))

def phase(f):
    """returns (radius, strength) for comp frame f -- radius now scales
    the bloom's gaussian core; strength caps at 0.85 (theirs never
    blows out)."""
    if f < 48:
        return 120.0, 0.0
    if f < 62:   # kindle
        t = (f - 48) / 14
        return 120 + 30 * t, 0.45 * t
    if f < 80:   # swell -- peak lands just after UP (f76)
        t = (f - 62) / 18
        t = t * t * (3 - 2 * t)
        return 150 + 45 * t, 0.45 + 0.47 * t
    if f < 88:   # peak hold behind UP
        return 195.0, 0.92
    if f < 108:  # fade out
        t = (f - 88) / 20
        t = t * t * (3 - 2 * t)
        return 195 - 15 * t, 0.92 * (1 - t)
    return 160.0, 0.0

CORE = np.array([255, 216, 150], dtype=np.float32)   # warm amber core (v4.1)
MID = np.array([255, 150, 60], dtype=np.float32)     # amber (v4 bloom mid)
EDGE = np.array([255, 59, 31], dtype=np.float32)     # hero red #FF3B1F

for f in range(40, 131):
    rad, s = phase(f)
    if s <= 0:
        Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(OUT / f"sun-f{f:04d}.png")
        continue
    pulse = 1 + 0.03 * np.sin(f * 0.35) + 0.02 * np.sin(f * 0.13 + 2)
    rr = r / (rad * pulse)
    # v4 BLOOM: no disc, no rim -- gaussian core + faint wide halo,
    # slight angular shimmer so it feels like tunnel light, not a sticker
    core = np.exp(-(rr ** 2) * 1.9)
    halo = np.exp(-((r / 540.0) ** 2) * 1.6) * 0.30
    shim = 0.92 + 0.08 * shimmer_base
    a = np.clip(core + halo, 0, 1) * shim * s
    # color: pale warm core -> amber -> deep orange by gaussian weight
    t1 = np.clip((1 - core) * 1.5, 0, 1)[:, :, None]
    col = CORE[None, None, :] * (1 - t1) + MID[None, None, :] * t1
    t2 = np.clip((rr - 0.9) / 1.8, 0, 1)[:, :, None]
    col = col * (1 - t2) + EDGE[None, None, :] * t2
    out = np.dstack([col, a * 255]).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(OUT / f"sun-f{f:04d}.png")
    if f % 40 == 0:
        print("sun frame", f, "r", round(rad), "s", round(float(s), 2))
print("sun frames done")
