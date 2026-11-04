#!/usr/bin/env python3
"""Rest-of-song director run (blocks 4-5 of track 108): Muse Wonder
designs the display lines for cues 5-10.

Reuses director.py's machinery verbatim (rules, validator, landings,
hero_color, effects budget, receipts) via import, and mirrors
cue4_director.py's discipline: one call per cue, with the block's
running state (heroes already headlined, scatter slot, last placement)
chained into every later call of the same block via validate()'s
prior_* arguments and add_effects()' priors. Block 5 starts fresh.

Word onsets: BOUNCE-true timings from the 2026-11-02 rest-of-song pass
(hidden_files/rest-of-song-2026-11-02/TIMINGS.md + timings.json) -- house
whisper-large-v3 on per-cue slices of the bounce; the SRT grid is NOT
used (the bounce's ~0.2-0.4s early lead decays to ~0 by cues 9-10, so no
constant shift exists to apply). Two flagged values: cue 7's first word
uses the TIMINGS-corrected onset 43.50 (the raw 43.18 chunk absorbs the
tail of "disappeared", +-0.3); cue 9's "You know" comes from the
2026-11-02 repair slice (76-90s): phrase onset pinned at 81.66, the
You/know split at 81.99 is a merged-chunk midpoint (estimated +-0.2),
and "what's" onset is the corrected 82.32.

Effects budget for these blocks: NO line in cues 5-10 is a
redlight-motif line (nothing brakes or stops), so the wrapper
validation additionally rejects any motif claim and any redlight=true;
scatter must derive False on every line (asserted after annotation).
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

import director
from director import (RULES, add_effects, add_hero_color, add_landings,
                      call_wonder, log_call, now_ct, parse_candidate,
                      validate, MODEL)

MAX_REPAIRS = 2


def _w(word, onset):
    return {"word": word, "onset_s": onset}


CUES = {
    5: {
        "lyric": "Girl, what you doing, how you get here?",
        "board_window_srt_s": [37.08, 39.94],
        "words": [_w("GIRL", 36.72), _w("WHAT", 37.46), _w("YOU", 37.74),
                  _w("DOING", 37.94), _w("HOW", 38.54), _w("YOU", 38.80),
                  _w("GET", 39.18), _w("HERE", 39.44)],
    },
    6: {
        "lyric": "She told me she was in town, but I disappeared.",
        "board_window_srt_s": [40.10, 43.26],
        "words": [_w("SHE", 39.98), _w("TOLD", 40.22), _w("ME", 40.48),
                  _w("SHE", 40.72), _w("WAS", 40.94), _w("IN", 41.50),
                  _w("TOWN", 41.70), _w("BUT", 42.06), _w("I", 42.18),
                  _w("DISAPPEARED", 42.44)],
    },
    7: {
        "lyric": "I told her, let me take you around, I won't show you now.",
        "board_window_srt_s": [43.90, 47.40],
        "words": [_w("I", 43.50), _w("TOLD", 43.98), _w("HER", 44.30),
                  _w("LET", 44.50), _w("ME", 44.68), _w("TAKE", 44.92),
                  _w("YOU", 45.20), _w("AROUND", 45.44), _w("I", 45.88),
                  _w("WON'T", 45.98), _w("SHOW", 46.06), _w("YOU", 46.38),
                  _w("NOW", 46.82)],
    },
    8: {
        "lyric": "She told me that she got me and had no doubt.",
        "board_window_srt_s": [47.70, 51.16],
        "words": [_w("SHE", 47.44), _w("TOLD", 47.96), _w("ME", 48.42),
                  _w("THAT", 48.70), _w("SHE", 48.88), _w("GOT", 49.10),
                  _w("ME", 49.40), _w("AND", 49.62), _w("HAD", 49.80),
                  _w("NO", 50.20), _w("DOUBT", 50.64)],
    },
    9: {
        "lyric": "You know what's going on, years we have been down the line.",
        "board_window_srt_s": [82.24, 85.58],
        "words": [_w("YOU", 81.66), _w("KNOW", 81.99), _w("WHAT'S", 82.32),
                  _w("GOING", 82.68), _w("ON", 82.96), _w("YEARS", 83.42),
                  _w("WE", 83.74), _w("HAVE", 83.96), _w("BEEN", 84.22),
                  _w("DOWN", 84.58), _w("THE", 85.02), _w("LINE", 85.22)],
    },
    10: {
        "lyric": "Got married, have kids, and it's crazy.",
        "board_window_srt_s": [85.58, 88.32],
        "words": [_w("GOT", 86.00), _w("MARRIED", 86.30), _w("HAVE", 86.68),
                  _w("KIDS", 87.04), _w("AND", 87.62), _w("IT'S", 87.86),
                  _w("CRAZY", 88.06)],
    },
}

BLOCKS = [
    {
        "block_id": "block4",
        "cues": [5, 6, 7, 8],
        "board_window_srt_s": [37.08, 51.16],
        "staging": (
            "STAGING CONTEXT for this block: block 4 is the song's second "
            "exchange (36.7-51.0s), following block 3, whose last word "
            "(WAY) punched full-frame and cut to black. Here she answers: "
            "her questions back at him, his offer, her reply. The block "
            "plays as one continuous section, display lines flowing cue "
            "by cue. Nothing in these lines brakes, stops, or pulls up "
            "short -- there is NO redlight-motif line in this block: "
            "redlight is false on every line, no line claims the motif "
            "scatter, and every hero lands plain."
        ),
        "timing_source": (
            "house whisper-large-v3 on the bounce, per-cue slices "
            "(rest-of-song TIMINGS 2026-11-02, bounce-true onsets; SRT "
            "grid not used -- the bounce lead decays from ~-0.36s at "
            "cue 5 to ~0 by cues 9-10). Cue 7 first-word onset 43.50 is "
            "the TIMINGS-corrected estimate (raw chunk 43.18 absorbs "
            "the tail of 'disappeared', +-0.3)"
        ),
    },
    {
        "block_id": "block5",
        "cues": [9, 10],
        "board_window_srt_s": [82.24, 88.32],
        "staging": (
            "STAGING CONTEXT for this block: block 5 is the coda "
            "(81.7-88.4s), after the song's long break: years have "
            "passed -- 'you know what's going on, years we have been "
            "down the line' -- then the payoff, 'got married, have "
            "kids, and it's crazy.' This is a FRESH block: hero words "
            "and placements start over (heroes from earlier blocks may "
            "be reused here). Nothing brakes or stops in these lines -- "
            "NO redlight-motif line: redlight is false on every line, "
            "no motif claims, and every hero lands plain."
        ),
        "timing_source": (
            "house whisper-large-v3 on the bounce (rest-of-song TIMINGS "
            "2026-11-02) + cue-9 repair slice 76-90s: 'You know' phrase "
            "onset pinned 81.66 (one merged chunk; You/know split at "
            "81.99 estimated +-0.2), what's onset corrected to 82.32, "
            "remaining cue-9 onsets re-based on the repair pass "
            "(anchors agree <=0.04s)"
        ),
    },
]


def strip_annotations(lines):
    return [
        {k: v for k, v in line.items() if k not in ("hero_color", "effects")}
        for line in lines
    ]


def block_stack_streak(lines):
    """Consecutive non-full placements at the end of the block so
    far -- chained into validate() as prior_stack_streak so the
    rotation rule binds across per-cue calls, not just within one
    candidate."""
    streak = 0
    for line in reversed(lines):
        if line.get("placement") == "full":
            break
        streak += 1
    return streak


def prior_block_lines():
    """Format examples for block 4: block 3's committed lines (both
    halves), annotations stripped -- the same mechanism cue4 used."""
    lines = []
    for name in ("block3-director.json", "block3-cue4-director.json"):
        doc = json.loads((HERE / name).read_text())
        lines.extend(doc["lines"])
    return strip_annotations(lines)


def build_prompt(target, examples, state, block, errors, bad_text):
    words = " ".join(f"{w['word']}@{w['onset_s']:.2f}s" for w in target["words"])
    heroes = ", ".join(state["heroes"]) if state["heroes"] else "none yet"
    state_note = (
        f"\nBlock state: {len(state['lines'])} display line(s) of THIS "
        f"block are already directed. Heroes already headlined in THIS "
        f"block (never repeat one): {heroes}."
    )
    if state["last_placement"]:
        state_note += (
            f" The previous display line in this block used placement "
            f"\"{state['last_placement']}\" -- your first line must not "
            f"repeat it."
        )
    streak = block_stack_streak(state["lines"])
    if streak:
        due = "next" if streak >= 2 else "within the next two lines"
        state_note += (
            f" The block currently ends with a run of {streak} stack "
            f"line(s) and no full-frame line in the run -- the "
            f"rotation rule allows at most 2 stacks back-to-back, so "
            f"plan a full-frame line {due}."
        )
    first_no = len(state["lines"]) + 1
    prompt = (
        RULES
        + "\n\n"
        + block["staging"]
        + "\n\nFORMAT EXAMPLES -- display lines already directed for this song (match this shape exactly):\n"
        + json.dumps({"lines": examples}, indent=2)
        + "\n\nTARGET -- the next cue of "
        + block["block_id"]
        + ". Raw lyric: \""
        + target["lyric"]
        + "\"\nMeasured word onsets on the bounce (seconds, song time): "
        + words
        + state_note
        + "\nSplit the lyric into display lines as the phrasing demands. "
        "Use EVERY word of the lyric exactly once, in order, across your lines. "
        "Display words are uppercase with no periods or commas.\n\n"
        "OUTPUT CONTRACT: reply with ONLY a JSON object, no prose, no code fences:\n"
        '{"lines": [{"line_id": "'
        + block["block_id"]
        + f'-line{first_no}", '
        '"display_groups": [{"words": ["..."], "motion": "punch_in"}], '
        '"placement": "left", "hero_word": "...", "size_tiers_px": [150], '
        '"redlight": false, "reason": "..."}]}'
        + f"\nNumber your lines sequentially starting at "
        f"{block['block_id']}-line{first_no}."
        "\nDo not output colors: the renderer records a hero_color entry per "
        "line from your hero_word (hero #FF3B1F, all other words #F2EDE4)."
        "\nEffects budget: heroes land plain. There is NO redlight-motif "
        "line in this block -- never set \"motif\" on any line, keep "
        "\"redlight\": false throughout, and never output an \"effects\" "
        "record (the renderer derives it in code, like hero_color). Never "
        "repeat a hero word within the block."
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


def validate_block(candidate, target, state):
    errors = validate(
        candidate,
        target,
        prior_heroes=state["heroes"],
        prior_scatter_used=state["scatter_used"],
        prior_stack_streak=block_stack_streak(state["lines"]),
    )
    lines = candidate.get("lines") if isinstance(candidate, dict) else None
    if isinstance(lines, list) and lines:
        first = lines[0]
        if state["last_placement"] and first.get("placement") == state["last_placement"]:
            errors.append(
                f"line 0 ({first.get('line_id', '?')}): placement "
                f"'{state['last_placement']}' repeats the previous display "
                "line's placement back-to-back in this block; rotate it"
            )
        for i, line in enumerate(lines):
            if not isinstance(line, dict):
                continue
            tag = f"line {i} ({line.get('line_id', '?')})"
            if line.get("motif") is True:
                errors.append(
                    f"{tag}: motif claimed in a block with no "
                    "redlight-motif line -- no line in cues 5-10 may "
                    "claim the scatter slot; heroes land plain"
                )
            if line.get("redlight") is not False:
                errors.append(
                    f"{tag}: redlight must be false throughout this "
                    "block (no braking/stopping line in cues 5-10)"
                )
    return errors


async def run_cue(target, examples, state, block):
    receipts, routes, rejects = [], [], []
    errors = None
    bad_text = None
    candidate = None
    step = f"2-director-{target['block_id']}"
    for attempt in range(MAX_REPAIRS + 1):
        prompt = build_prompt(target, examples, state, block, errors, bad_text)
        text, resp, route = await call_wonder(prompt)
        routes.append(route)
        kind = "wonder_director_call" if attempt == 0 else "wonder_director_repair"
        note = f"route={route}; attempt={attempt}; target={target['block_id']}"
        if errors:
            note += "; fixing: " + "; ".join(errors)[:300]
        receipts.append(log_call(step, kind, resp, note=note))
        try:
            candidate = parse_candidate(text)
            errors = validate_block(candidate, target, state)
        except Exception as exc:
            candidate = {}
            errors = [f"unparseable JSON output: {exc}"]
        if not errors:
            break
        rejects.append(list(errors))
        bad_text = text
        print(f"{target['block_id']} attempt {attempt}: {len(errors)} validation error(s)", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
    if errors:
        raise RuntimeError(f"{target['block_id']} director output still invalid after repairs: {errors}")
    return candidate, receipts, routes, rejects


async def run_block(block, examples):
    state = {"heroes": [], "scatter_used": False, "last_placement": None, "lines": []}
    all_receipts, all_routes, all_rejects = [], [], []
    for cue_no in block["cues"]:
        cue = CUES[cue_no]
        target = {
            "block_id": f"{block['block_id']}-cue{cue_no}",
            "lyric": cue["lyric"],
            "board_window_srt_s": cue["board_window_srt_s"],
            "words": cue["words"],
        }
        cue_examples = strip_annotations(state["lines"]) if state["lines"] else examples
        candidate, receipts, routes, rejects = await run_cue(target, cue_examples, state, block)
        all_receipts.extend(receipts)
        all_routes.extend(routes)
        all_rejects.extend(rejects)
        lines = add_landings(candidate["lines"], target)
        lines = add_hero_color(lines)
        lines = add_effects(
            lines,
            prior_heroes=state["heroes"],
            prior_scatter_used=state["scatter_used"],
        )
        for line in lines:
            assert line["effects"]["scatter"] is False, (
                f"scatter derived True on {line.get('line_id')} -- budget breach"
            )
        state["lines"].extend(lines)
        state["heroes"].extend(
            line["hero_word"] for line in lines
            if isinstance(line.get("hero_word"), str) and line["hero_word"].strip()
        )
        state["scatter_used"] = state["scatter_used"] or any(
            line["effects"]["scatter"] for line in lines
        )
        state["last_placement"] = lines[-1]["placement"]
    doc = {
        "block": block["block_id"],
        "track": "108 VOX1_01",
        "source_lyric": " ".join(CUES[c]["lyric"] for c in block["cues"]),
        "board_window_srt_s": block["board_window_srt_s"],
        "timing_source": block["timing_source"],
        "landing_rule": "landing = onset - 2 frames @ 30fps",
        "model": MODEL,
        "generated_ct": now_ct(),
        "api_routes": all_routes,
        "receipt_request_ids": [r["request_id"] for r in all_receipts],
        "lines": state["lines"],
    }
    out_path = HERE / f"{block['block_id']}-director.json"
    out_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    summary = {
        "block": block["block_id"],
        "lines": len(state["lines"]),
        "heroes": state["heroes"],
        "scatter_used": state["scatter_used"],
        "calls": len(all_receipts),
        "cost_usd": round(sum(r["cost_usd"] for r in all_receipts), 6),
        "rejects": all_rejects,
        "receipts": all_receipts,
    }
    print(json.dumps(summary, indent=2))
    return state["lines"], summary


async def main():
    examples = prior_block_lines()
    summaries = []
    for block in BLOCKS:
        lines, summary = await run_block(block, examples)
        summaries.append(summary)
        examples = strip_annotations(lines)
    total = round(sum(s["cost_usd"] for s in summaries), 6)
    print(json.dumps({"total_cost_usd": total,
                      "total_calls": sum(s["calls"] for s in summaries)}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
