# Muse Image (muse-image-1.0) world plates + PIL type for the 108 cards.
#
# BrickHouse, 2026-11-02. The model paints ONLY the black-and-white world
# (the prompts forbid text); every letter is composited here in code with
# Anton, so the type is exact and in the locked look:
#   hero red #FF3B1F, other text off-white #F2EDE4, header strip
#   "DRIZZZ \u2022 108 \u2022 BRICKHOUSE STUDIOS" (Anton 30px, off-white @55%,
#   hairline rule y66-68) at the top of every card, 1920x1080.
#
# API pattern follows sam_api.py (same client(), key stays in memory).
# Every generation call is receipted to receipts.log next to this file.
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sam_api

MODEL = "muse-image-1.0"
PRICE_USD_PER_IMAGE = 0.01
PRICE_BASIS = "per image, Meta Model API published pricing (checked 2026-11-02)"
REPO = Path(__file__).resolve().parent
RECEIPTS = REPO / "receipts.log"
OUT = REPO / "out" / "cards-2026-11-02"

W, H = 1920, 1080
RED = (255, 59, 31)          # #FF3B1F
OFFWHITE = (242, 237, 228)   # #F2EDE4
HEADER_TEXT = "DRIZZZ \u2022 108 \u2022 BRICKHOUSE STUDIOS"
HEADER_PX = 30
HEADER_ALPHA = 140           # 55% of 255
MARGIN = 48

FONT_CANDIDATES = [
    Path("/tmp/Anton-Regular.ttf"),
    Path.home() / "Library" / "Fonts" / "Anton-Regular.ttf",
]

PLATES = {
    "title": (
        "Black and white photograph, abstract night driving: long-exposure "
        "light streaks sweeping across wet asphalt, rain droplets on dark "
        "glass, deep blacks, high contrast monochrome, cinematic and moody, "
        "no people, no readable cars, no text, no letters, no words, "
        "no typography, no signs"
    ),
    "end": (
        "Black and white photograph, a quiet dark road at night after rain, "
        "a distant headlight glow blooming through mist, rain-speckled glass "
        "texture, deep black monochrome, cinematic stillness, no people, "
        "no text, no letters, no words, no typography, no signs"
    ),
}


def font_path() -> Path:
    for cand in FONT_CANDIDATES:
        if cand.exists():
            return cand
    raise RuntimeError("Anton-Regular.ttf not found in FONT_CANDIDATES")


def font(px: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(font_path()), px)


def now_ct() -> str:
    return datetime.now(ZoneInfo("America/Chicago")).isoformat(timespec="seconds")


def log_receipt(step: str, request_id: str | None, usage: dict, note: str) -> None:
    entry = {
        "ts_ct": now_ct(),
        "step": step,
        "kind": "muse_image_call",
        "model": MODEL,
        "request_id": request_id,
        "units": 1,
        "unit": "image",
        "unit_price_usd": PRICE_USD_PER_IMAGE,
        "unit_price_basis": PRICE_BASIS,
        "cost_usd": PRICE_USD_PER_IMAGE,
        "note": note + f"; usage={json.dumps(usage)}",
    }
    with RECEIPTS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    print("RECEIPT", step, request_id, "cost", PRICE_USD_PER_IMAGE)


async def gen_plate(name: str, prompt: str) -> tuple[Path, dict]:
    async with sam_api.client() as api:
        raw = await api.with_raw_response.images.generate(
            model=MODEL, prompt=prompt, size="1920x1080", n=1
        )
        resp = raw.parse()
        request_id = raw.http_response.headers.get("x-request-id")
    usage = resp.usage.model_dump() if resp.usage else {}
    blob = base64.b64decode(resp.data[0].b64_json)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"plate-{name}-raw.webp"
    path.write_bytes(blob)
    log_receipt(f"3-image-cards-{name}", request_id, usage,
                f"plate for {name} card; raw saved {path.name}")
    return path, {"request_id": request_id, "usage": usage,
                  "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest()}


def cover_plate(path: Path) -> Image.Image:
    """Load a plate, force true monochrome, cover-fit to 1920x1080."""
    im = Image.open(path).convert("L")
    scale = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)),
                   Image.LANCZOS)
    x = (im.width - W) // 2
    y = (im.height - H) // 2
    return im.crop((x, y, x + W, y + H)).convert("RGB")


def fit_font(draw: ImageDraw.ImageDraw, text: str, target_h: int) -> ImageFont.FreeTypeFont:
    lo, hi = 8, 2000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        bb = draw.textbbox((0, 0), text, font=font(mid))
        if bb[3] - bb[1] <= target_h:
            lo = mid
        else:
            hi = mid - 1
    return font(lo)


def stamp(base: Image.Image, text: str, fnt: ImageFont.FreeTypeFont,
          cx: float, top: float, fill: tuple[int, int, int]) -> tuple[int, int]:
    """Draw text centered at cx with a stacked soft dark glow (locked G3
    spirit: heavy blurred black under the glyphs) and return (w, h)."""
    probe = ImageDraw.Draw(base)
    bb = probe.textbbox((0, 0), text, font=fnt)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    x = cx - w / 2 - bb[0]
    y = top - bb[1]
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((x, y + 10), text, font=fnt, fill=(0, 0, 0, 150))
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(34)))
    glow2 = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd2 = ImageDraw.Draw(glow2)
    gd2.text((x, y + 6), text, font=fnt, fill=(0, 0, 0, 190))
    base.alpha_composite(glow2.filter(ImageFilter.GaussianBlur(13)))
    d = ImageDraw.Draw(base)
    d.text((x, y), text, font=fnt, fill=fill + (255,))
    return w, h


def add_header(base: Image.Image) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.text((MARGIN, 20), HEADER_TEXT, font=font(HEADER_PX),
           fill=OFFWHITE + (HEADER_ALPHA,))
    d.rectangle([MARGIN, 66, W - MARGIN, 68], fill=OFFWHITE + (HEADER_ALPHA,))
    base.alpha_composite(overlay)


def build_title(plate: Image.Image) -> Image.Image:
    card = plate.convert("RGBA")
    d = ImageDraw.Draw(card)
    hero_f = fit_font(d, "108", 470)  # ~44% of frame height
    bb = d.textbbox((0, 0), "108", font=hero_f)
    hero_h = bb[3] - bb[1]
    hero_top = 452 - hero_h / 2
    stamp(card, "108", hero_f, W / 2, hero_top, RED)
    sub_f = font(118)
    bb2 = d.textbbox((0, 0), "DRIZZZ", font=sub_f)
    stamp(card, "DRIZZZ", sub_f, W / 2, hero_top + hero_h + 46, OFFWHITE)
    add_header(card)
    return card.convert("RGB")


def build_end(plate: Image.Image) -> Image.Image:
    card = plate.convert("RGBA")
    d = ImageDraw.Draw(card)
    accent_f = fit_font(d, "108", 205)
    bb = d.textbbox((0, 0), "108", font=accent_f)
    accent_h = bb[3] - bb[1]
    accent_top = 352 - accent_h / 2
    stamp(card, "108", accent_f, W / 2, accent_top, RED)
    name_f = font(148)
    stamp(card, "BRICKHOUSE STUDIOS", name_f, W / 2,
          accent_top + accent_h + 52, OFFWHITE)
    add_header(card)
    return card.convert("RGB")


async def main() -> None:
    meta: dict[str, dict] = {}
    plates: dict[str, Image.Image] = {}
    for name, prompt in PLATES.items():
        path, info = await gen_plate(name, prompt)
        raw = Image.open(path)
        info["plate_px"] = list(raw.size)
        info["plate_path"] = str(path)
        meta[name] = info
        plates[name] = cover_plate(path)
    title = build_title(plates["title"])
    end = build_end(plates["end"])
    for name, im in (("title", title), ("end", end)):
        out = OUT / f"{name}-card.png"
        im.save(out, optimize=True)
        meta[name]["card_path"] = str(out)
        meta[name]["card_sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
        meta[name]["card_bytes"] = out.stat().st_size
    print("SUMMARY " + json.dumps(meta, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
