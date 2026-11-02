#!/usr/bin/env python3
"""Measure STOP/AT glyph-core vs ring luma for given PNG files (same method
as worst_scan.py: off-white core match, ring = dilate27 minus dilate7)."""
import sys
import numpy as np
from PIL import Image, ImageFilter

WORDS = {"STOP": (100, 300, 560, 510), "AT": (580, 300, 870, 510)}

def core_mask(img, box):
    x0, y0, x1, y1 = box
    c = img[y0:y1, x0:x1].astype(np.int16)
    return (np.abs(c[..., 0] - 242) <= 18) & (np.abs(c[..., 1] - 237) <= 18) & \
           (np.abs(c[..., 2] - 228) <= 20) & (c[..., 0] > 215)

def dilate(m, size):
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(size))
    return np.asarray(im) > 0

for path in sys.argv[1:]:
    img = np.asarray(Image.open(path).convert("RGB"))
    luma = (0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2])
    out = []
    for w, box in WORDS.items():
        x0, y0, x1, y1 = box
        core = core_mask(img, box)
        ring = dilate(core, 27) & ~dilate(core, 7)
        sub = luma[y0:y1, x0:x1]
        cl = float(sub[core].mean()); rl = float(sub[ring].mean())
        out.append(f"{w}: core={cl:.1f} ring={rl:.1f} sep={cl-rl:.1f}")
    print(f"{path.split('/')[-1]:28s} " + " | ".join(out))
