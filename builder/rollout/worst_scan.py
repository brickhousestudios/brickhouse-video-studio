#!/usr/bin/env python3
"""Phase-1 worst-frame scan: for STOP and AT (off-white words) in the concept
alt preview, per frame measure glyph-core luma vs dilated-ring luma.
Separation = core - ring (small = washed into the surround)."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

FR = Path(sys.argv[1])  # frames dir f%03d.png starting at f000
WORDS = {"STOP": (100, 300, 560, 510), "AT": (580, 300, 870, 510)}

def core_mask(img, box):
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].astype(np.int16)
    m = (np.abs(c[..., 0] - 242) <= 18) & (np.abs(c[..., 1] - 237) <= 18) & \
        (np.abs(c[..., 2] - 228) <= 20) & (c[..., 0] > 215)
    return m

def dilate(m, size):
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(size))
    return np.asarray(im) > 0

rows = []
for f in range(34, 71):
    img = np.asarray(Image.open(FR / f"f{f:03d}.png").convert("RGB"))
    luma = (0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2])
    rec = {"frame": f}
    for w, box in WORDS.items():
        x0, y0, x1, y1 = box
        core = core_mask(img, box)
        if core.sum() < 200:
            rec[w] = None
            continue
        ring = dilate(core, 27) & ~dilate(core, 7)
        sub = luma[y0:y1, x0:x1]
        cl = float(sub[core].mean())
        rl = float(sub[ring].mean()) if ring.sum() else float("nan")
        rec[w] = (core.sum(), cl, rl, cl - rl)
    rows.append(rec)

def sep(rec, w):
    return rec[w][3] if rec.get(w) else 1e9

rows.sort(key=lambda r: min(sep(r, "STOP"), sep(r, "AT")))
print("WORST 8 frames (by min(STOP,AT) separation):")
for r in rows[:8]:
    s = []
    for w in ("STOP", "AT"):
        v = r[w]
        s.append(f"{w}: n={v[0]} core={v[1]:.1f} ring={v[2]:.1f} sep={v[3]:.1f}" if v else f"{w}: n/a")
    print(f"  f{r['frame']:03d}  " + " | ".join(s))
print("\nBEST frame:")
r = rows[-1]
print(f"  f{r['frame']:03d}  " + " | ".join(
    f"{w}: core={r[w][1]:.1f} ring={r[w][2]:.1f} sep={r[w][3]:.1f}" if r[w] else f"{w}: n/a" for w in ("STOP", "AT")))
