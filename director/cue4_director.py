#!/usr/bin/env python3
"""Cue-4 director run (block 3, second half): Muse Wonder designs the
'Then I asked where she from, she said no way' display line(s).

Reuses director.py's machinery verbatim (rules, validator, landings,
receipts) via import. Differences from the block-3 run, all in the prompt
and the target: the examples are the two ALREADY-BUILT block-3 lines
(block3-line1 LEFT, block3-line2 RIGHT), a staging note pins the recede-
to-black context, and one extra validation rule applies — the first
display line here must NOT use placement "right" (it would repeat
block3-line2's placement back-to-back inside one continuous shot).

Word onsets: house whisper-large-v3 on the bounce, two overlapping
windows (31.0-38.5 and 32.5-39.5), cross-checked 2026-11-01; most agree
<=0.02s. THEN's chunk is long (sustained pickup) — onset 33.28 carries
the standing +-0.15s sung-vocal uncertainty. "No way" was heard by
whisper as 'norway' in one window (BO's ear rules the lyric: no way);
NO onset 35.87, WAY onset 36.12, WAY ends 36.60.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import director
from director import (RULES, add_effects, add_hero_color, add_landings,
                      call_wonder, log_call, now_ct, parse_candidate,
                      validate, MODEL)

HERE = Path(__file__).parent
MAX_REPAIRS = 2

TARGET = {
    "block_id": "block3-cue4",
    "lyric": "Then I asked where she from, she said no way.",
    "board_window_srt_s": [33.86, 36.88],
    "words": [
        {"word": "THEN", "onset_s": 33.28},
        {"word": "I", "onset_s": 34.08},
        {"word": "ASKED", "onset_s": 34.24},
        {"word": "WHERE", "onset_s": 34.56},
        {"word": "SHE", "onset_s": 34.74},
        {"word": "FROM", "onset_s": 34.89},
        {"word": "SHE", "onset_s": 35.14},
        {"word": "SAID", "onset_s": 35.63},
        {"word": "NO", "onset_s": 35.87},
        {"word": "WAY", "onset_s": 36.12},
    ],
}

STAGING = """STAGING CONTEXT for this target: this line is the back half of
block 3, ONE continuous shot with the two display lines given below as
examples — block3-line1 used placement LEFT and block3-line2 used
placement RIGHT. Your first display line here must NOT use "right": that
would repeat the previous line's placement back-to-back. The background
footage under this line is receding — bright streaks pulling away into
darkness — and the frame reaches full black exactly as "no way" ends, so
the last words land over near-darkness and the song's bridge then enters
out of black. "No way" is the turn of the whole exchange."""


def build_prompt(target, errors, bad_text):
    block3 = json.loads((HERE / "block3-director.json").read_text())
    words = " ".join(f"{w['word']}@{w['onset_s']:.2f}s" for w in target["words"])
    prompt = (
        RULES
        + "\n\n"
        + STAGING
        + "\n\nFORMAT EXAMPLES — the two display lines already built for THIS shot (match this shape exactly):\n"
        + json.dumps(
            {"lines": [
                {k: v for k, v in line.items() if k not in ("hero_color", "effects")}
                for line in block3["lines"]
            ]},
            indent=2,
        )
        + "\n\nTARGET — the next display line(s) of block 3. Raw lyric: \""
        + target["lyric"]
        + "\"\nMeasured word onsets on the bounce (seconds, song time): "
        + words
        + "\nSplit the lyric into display lines as the phrasing demands. "
        "Use EVERY word of the lyric exactly once, in order, across your lines. "
        "Display words are uppercase with no periods or commas.\n\n"
        "OUTPUT CONTRACT: reply with ONLY a JSON object, no prose, no code fences:\n"
        '{"lines": [{"line_id": "block3-line3", '
        '"display_groups": [{"words": ["..."], "motion": "punch_in"}], '
        '"placement": "left", "hero_word": "...", "size_tiers_px": [150], '
        '"redlight": false, "reason": "..."}]}'
        "\nDo not output colors: the renderer records a hero_color entry per "
        "line from your hero_word (hero #FF3B1F, all other words #F2EDE4)."
        "\nEffects budget: heroes land plain. You may set \"motif\": true on "
        "at most ONE line -- only a redlight-motif line -- to claim the "
        "block's single scatter treatment; never output an \"effects\" "
        "record (the renderer derives it in code, like hero_color). Never "
        "repeat a hero word within the block -- the two lines above "
        "already headlined theirs."
    )
    if errors:
        prompt += (
            "\n\nYOUR PREVIOUS OUTPUT FAILED VALIDATION. Fix every problem and "
            "return the full corrected JSON only.\nProblems:\n- "
            + "\n- ".join(errors)
            + "\nPrevious output was:\n"
            + (bad_text or "")[:4000]
        )
    return prompt


def _prior_block():
    """Block state from block 3's first half (the committed block3
    lines): their hero words, and whether the block's single scatter
    slot is already taken. Lines 3-5 are judged as part of that block,
    so a hero repeated from lines 1-2 (FROM, AROUND) fails validation
    here and the renderer-side demotion never has to fire on a fresh
    run."""
    block3 = json.loads((HERE / "block3-director.json").read_text())
    heroes = [line.get("hero_word") for line in block3["lines"]]
    scatter_used = any(
        (line.get("effects") or {}).get("scatter") for line in block3["lines"]
    )
    return heroes, scatter_used


def validate_cue4(candidate, target):
    prior_heroes, prior_scatter = _prior_block()
    errors = validate(
        candidate,
        target,
        prior_heroes=prior_heroes,
        prior_scatter_used=prior_scatter,
    )
    try:
        first = candidate["lines"][0]
        if first.get("placement") == "right":
            errors.append(
                "first line: placement 'right' repeats block3-line2's placement "
                "back-to-back in the same shot; choose left or full"
            )
    except Exception:
        pass
    return errors


async def main():
    receipts = []
    errors = None
    bad_text = None
    routes = []
    candidate = None
    for attempt in range(MAX_REPAIRS + 1):
        prompt = build_prompt(TARGET, errors, bad_text)
        text, resp, route = await call_wonder(prompt)
        routes.append(route)
        kind = "wonder_director_call" if attempt == 0 else "wonder_director_repair"
        note = f"route={route}; attempt={attempt}; target=block3-cue4"
        if errors:
            note += "; fixing: " + "; ".join(errors)[:300]
        receipts.append(log_call("2-director-block3-cue4", kind, resp, note=note))
        try:
            candidate = parse_candidate(text)
            errors = validate_cue4(candidate, TARGET)
        except Exception as exc:
            candidate = {}
            errors = [f"unparseable JSON output: {exc}"]
        if not errors:
            break
        bad_text = text
        print(f"attempt {attempt}: {len(errors)} validation error(s)", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
    if errors:
        raise RuntimeError(f"cue4 director output still invalid after repairs: {errors}")
    lines = add_landings(candidate["lines"], TARGET)
    lines = add_hero_color(lines)
    prior_heroes, prior_scatter = _prior_block()
    lines = add_effects(
        lines, prior_heroes=prior_heroes, prior_scatter_used=prior_scatter
    )
    doc = {
        "block": TARGET["block_id"],
        "track": "108 VOX1_01",
        "source_lyric": TARGET["lyric"],
        "board_window_srt_s": TARGET["board_window_srt_s"],
        "timing_source": (
            "house whisper-large-v3 on the bounce (two overlapping segments "
            "31.0-38.5 / 32.5-39.5, onsets cross-checked <=0.02s on 8 of 10 "
            "words, +-~0.15s); bounce sings ahead of the SRT grid"
        ),
        "landing_rule": "landing = onset - 2 frames @ 30fps",
        "model": MODEL,
        "generated_ct": now_ct(),
        "api_routes": routes,
        "receipt_request_ids": [r["request_id"] for r in receipts],
        "lines": lines,
    }
    out_path = HERE / "block3-cue4-director.json"
    out_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    print(json.dumps({"lines": len(lines), "receipts": receipts}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
