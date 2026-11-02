#!/usr/bin/env python3
"""Rain composite v2 for the concept block-2 comp A render.
Same math as the SAM lane's composite_rain.py (droplet mask x text region
x footage, alpha 0.85, footage index floor(f*24/30)); the text REGION now
comes from the locked v4 render's red mask (identical timings/geometry),
unioned with WINDOW's static ink box so the assembled hero is covered
(the v4 wipe region lags the assemble entry by design)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

SAM = Path(sys.argv[1])        # sam-2026-11-01 workdir
NEW = Path(sys.argv[2])        # dir of new comp-A frames (jpg or png)
OUT = Path(sys.argv[3])        # output frames dir
ALPHA = 0.85
W, H = 1920, 1080

def footage_index(f: int) -> int:
    return (f * 24) // 30

def load_rgb(path: Path, size=(W, H)) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB").resize(size), dtype=np.float32)

def red_mask(img: np.ndarray) -> np.ndarray:
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    return (r > 90) & (r - g > 45) & (r - b > 35)

def dilate(m: np.ndarray, size=25) -> np.ndarray:
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(size))
    return np.asarray(im, dtype=np.float32) / 255.0

def main() -> None:
    old_frames = sorted((SAM / "compa-frames").glob("f*.png"))
    new_frames = sorted(NEW.glob("f*.*"))
    foot_frames = sorted((SAM / "foot2-frames").glob("f*.png"))
    mask_dir = SAM / "masks-block2-droplets"
    assert len(old_frames) == 75 and len(new_frames) == 75, (len(old_frames), len(new_frames))
    OUT.mkdir(parents=True, exist_ok=True)
    # WINDOW static ink box from the v4 render at f60 (tier-3 word: y>500)
    m60 = red_mask(load_rgb(old_frames[60]))
    m60[:500] = False
    ys, xs = np.where(m60)
    win_box = np.zeros((H, W), dtype=bool)
    win_box[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = True
    print(f"WINDOW box: x[{xs.min()},{xs.max()}] y[{ys.min()},{ys.max()}]")
    win_region = dilate(win_box)
    report = []
    for f in range(75):
        base = load_rgb(new_frames[f])
        foot = load_rgb(foot_frames[footage_index(f)], size=(1280, 720))
        foot_up = np.asarray(Image.fromarray(foot.astype(np.uint8)).resize((W, H), Image.LANCZOS), dtype=np.float32)
        mp = mask_dir / f"frame-{f:03d}.png"
        if mp.exists():
            m720 = np.asarray(Image.open(mp).convert("L"), dtype=np.float32) / 255.0
        else:
            m720 = np.zeros((720, 1280), dtype=np.float32)
        mask = np.asarray(Image.fromarray((m720 * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), dtype=np.float32) / 255.0
        region = np.maximum(dilate(red_mask(load_rgb(old_frames[f]))), win_region)
        sel = mask * region
        report.append((f, float(sel.mean())))
        a = (sel * ALPHA)[..., None]
        out = base * (1 - a) + foot_up * a
        Image.fromarray(out.astype(np.uint8)).save(OUT / f"f{f:03d}.png")
    report.sort(key=lambda kv: -kv[1])
    print("top droplet-over-text frames:", report[:5])
    (OUT / "rain-overlap-v2.json").write_text(json.dumps(report))

if __name__ == "__main__":
    main()
