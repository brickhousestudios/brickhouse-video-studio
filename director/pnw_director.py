#!/usr/bin/env python3
"""PUT N WORK director run: Muse Wonder designs the display lines for
all six sections of PUT N WORK (DRIXX), step 2 of BO's standing order
(timing -> director plan -> BO verdict -> footage).

Mirrors director/rest_director.py's discipline (the 108 blocks 4-5
chain): reuses director.py's machinery verbatim (RULES, call_wonder,
validate, add_landings, add_hero_color, add_effects, receipts). One
call per section, block state chained inside the candidate by
validate() itself; if a section exhausts the repair loop it is split
by sheet lines (halves, then single lines) with state chained across
the split via validate()'s prior_* arguments -- the same mechanism
cue4/rest chained across per-cue calls.

Words: BO's lyric sheet ONLY (pnw_targets.json). Timings: the V3
timing grid (house whisper-large-v3, song_grid.json) assembled onto
the sheet words -- sheet absolute times NOT used (measured drift
+11.2s -> -31.9s). ASR text never reaches the prompt as lyric.

Effects budget for this song: PNW has NO redlight-motif line (no line
brakes/stops/pulls up at a light; the cops line runs FROM them), so --
exactly as for 108 blocks 4-5 -- the wrapper validation rejects any
motif claim and any redlight=true; scatter must derive False on every
line (asserted after annotation).

Validator measurement (closes the PNW stress test's open item): the
FIRST candidate of each section (attempt 0, before any repair) is
validated with the REAL validate() and its errors recorded verbatim
in the summary as first_pass_validate_errors, separately from the
wrapper's extra checks and from the final clean pass.
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
TARGETS = json.loads((HERE / "pnw_targets.json").read_text())


def strip_annotations(lines):
    return [
        {k: v for k, v in line.items() if k not in ("hero_color", "effects")}
        for line in lines
    ]


def block_stack_streak(lines):
    streak = 0
    for line in reversed(lines):
        if line.get("placement") == "full":
            break
        streak += 1
    return streak


def prior_examples():
    """Format examples for the first section: 108 block 5's committed
    lines (annotations stripped) -- the mechanism rest_director used
    (it seeded block 4 from block 3's lines)."""
    doc = json.loads((HERE / "block5-director.json").read_text())
    return strip_annotations(doc["lines"])


def build_prompt(section, unit, examples, state, errors, bad_text):
    words = " ".join(f"{w['word']}@{w['onset_s']:.2f}s" for w in unit["words"])
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
        + section["staging"]
        + "\n\nFORMAT EXAMPLES -- display lines already directed for this project (match this shape exactly):\n"
        + json.dumps({"lines": examples}, indent=2)
        + "\n\nTARGET -- "
        + unit["label"]
        + " of the song 'Put N Work'. Raw lyric (BO's sheet, the only "
        "word source): \""
        + unit["lyric"]
        + "\"\nMeasured word onsets on the V3 master (seconds, song time; "
        "timing grid, not the sheet's clock): "
        + words
        + state_note
        + "\nSplit the lyric into display lines as the phrasing demands. "
        "Use EVERY word of the lyric exactly once, in order, across your lines. "
        "Display words are uppercase with no periods or commas.\n\n"
        "OUTPUT CONTRACT: reply with ONLY a JSON object, no prose, no code fences:\n"
        '{"lines": [{"line_id": "'
        + section["block_id"]
        + f'-line{first_no}", '
        '"display_groups": [{"words": ["..."], "motion": "punch_in"}], '
        '"placement": "left", "hero_word": "...", "size_tiers_px": [150], '
        '"redlight": false, "reason": "..."}]}'
        + f"\nNumber your lines sequentially starting at "
        f"{section['block_id']}-line{first_no}."
        "\nDo not output colors: the renderer records a hero_color entry per "
        "line from your hero_word (hero #FF3B1F, all other words #F2EDE4)."
        "\nEffects budget: heroes land plain. There is NO redlight-motif "
        "line in this song -- never set \"motif\" on any line, keep "
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


def validate_unit(candidate, unit, state):
    """Returns (validate_errors, wrapper_errors). validate() runs with
    the block state chained via prior_* (empty for a whole-section
    call, where validate chains internally)."""
    v_errors = validate(
        candidate,
        unit,
        prior_heroes=state["heroes"],
        prior_scatter_used=False,
        prior_stack_streak=block_stack_streak(state["lines"]),
    )
    w_errors = []
    lines = candidate.get("lines") if isinstance(candidate, dict) else None
    if isinstance(lines, list) and lines:
        first = lines[0]
        if (isinstance(first, dict) and state["last_placement"]
                and first.get("placement") == state["last_placement"]):
            w_errors.append(
                f"line 0 ({first.get('line_id', '?')}): placement "
                f"'{state['last_placement']}' repeats the previous display "
                "line's placement back-to-back in this block; rotate it"
            )
        for i, line in enumerate(lines):
            if not isinstance(line, dict):
                continue
            tag = f"line {i} ({line.get('line_id', '?')})"
            if line.get("motif") is True:
                w_errors.append(
                    f"{tag}: motif claimed in a song with no "
                    "redlight-motif line -- no PNW line may claim the "
                    "scatter slot; heroes land plain"
                )
            if line.get("redlight") is not False:
                w_errors.append(
                    f"{tag}: redlight must be false throughout this "
                    "song (no braking/stopping line in PUT N WORK)"
                )
    return v_errors, w_errors


async def run_unit(section, unit, examples, state, record):
    """One call unit with the chain's repair loop. Records attempt-0
    validate() errors into record['first_pass'] when record asks for
    it (whole-section first call only). Returns annotated lines."""
    receipts, routes = [], []
    errors = None
    bad_text = None
    candidate = None
    step = f"2-director-{unit['unit_id']}"
    for attempt in range(MAX_REPAIRS + 1):
        prompt = build_prompt(section, unit, examples, state, errors, bad_text)
        text, resp, route = await call_wonder(prompt)
        routes.append(route)
        kind = "wonder_director_call" if attempt == 0 else "wonder_director_repair"
        note = f"route={route}; attempt={attempt}; target={unit['unit_id']}"
        if errors:
            note += "; fixing: " + "; ".join(errors)[:300]
        receipts.append(log_call(step, kind, resp, note=note))
        record["receipts"].extend(receipts[-1:])
        record["routes"].append(route)
        try:
            candidate = parse_candidate(text)
            v_errors, w_errors = validate_unit(candidate, unit, state)
        except Exception as exc:
            candidate = {}
            v_errors = [f"unparseable JSON output: {exc}"]
            w_errors = []
        if attempt == 0 and record.get("capture_first_pass"):
            record["first_pass_validate_errors"] = list(v_errors)
            record["first_pass_wrapper_errors"] = list(w_errors)
            record["capture_first_pass"] = False
        errors = v_errors + w_errors
        if not errors:
            break
        bad_text = text
        print(f"{unit['unit_id']} attempt {attempt}: {len(errors)} error(s)",
              file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
    if errors:
        raise RuntimeError(
            f"{unit['unit_id']} still invalid after repairs: {errors}")
    # Final-verification evidence: re-validate the winning candidate
    # against the same priors; must be clean.
    v2, w2 = validate_unit(candidate, unit, state)
    assert not v2 and not w2, f"final re-validation failed: {v2 + w2}"
    record["final_revalidate"].append(
        {"unit": unit["unit_id"], "validate_errors": v2, "wrapper_errors": w2})
    lines = add_landings(candidate["lines"], unit)
    lines = add_hero_color(lines)
    lines = add_effects(lines, prior_heroes=state["heroes"],
                        prior_scatter_used=False)
    for line in lines:
        assert line["effects"]["scatter"] is False, (
            f"scatter derived True on {line.get('line_id')} -- budget breach")
    return lines


def make_unit(section, sheet_line_idxs, label):
    words, lyric_parts = [], []
    for i in sheet_line_idxs:
        sl = section["sheet_lines"][i]
        lyric_parts.append(sl["raw"])
        words.extend({"word": w["word"], "onset_s": w["onset_s"]}
                     for w in sl["words"])
    suffix = "" if len(sheet_line_idxs) == len(section["sheet_lines"]) else (
        f"-lines{sheet_line_idxs[0] + 1}-{sheet_line_idxs[-1] + 1}")
    return {
        "unit_id": section["block_id"] + suffix,
        "block_id": section["block_id"],
        "label": label,
        "lyric": " ".join(lyric_parts),
        "words": words,
        "sheet_line_idxs": list(sheet_line_idxs),
    }


async def run_span(section, idxs, examples, state, record, depth=0):
    """Run a span of sheet lines as one unit; on repair exhaustion,
    split by sheet lines (halves, then singles) with state chained."""
    if len(idxs) == len(section["sheet_lines"]):
        label = f"the full {section['block_id']} section"
    else:
        label = (f"sheet lines {idxs[0] + 1}-{idxs[-1] + 1} of "
                 f"{section['block_id']}")
    unit = make_unit(section, idxs, label)
    unit_examples = strip_annotations(state["lines"]) if state["lines"] else examples
    try:
        lines = await run_unit(section, unit, unit_examples, state, record)
    except RuntimeError:
        if len(idxs) <= 1:
            raise
        mid = (len(idxs) + 1) // 2
        print(f"{unit['unit_id']}: splitting into halves", file=sys.stderr)
        record["splits"].append(unit["unit_id"])
        lines = []
        for part in (idxs[:mid], idxs[mid:]):
            lines.extend(await run_span(section, part, examples, state,
                                        record, depth + 1))
        return lines
    state["lines"].extend(lines)
    state["heroes"].extend(
        line["hero_word"] for line in lines
        if isinstance(line.get("hero_word"), str) and line["hero_word"].strip()
    )
    state["last_placement"] = lines[-1]["placement"]
    return lines


async def run_section(section, examples):
    state = {"heroes": [], "last_placement": None, "lines": []}
    record = {"receipts": [], "routes": [], "splits": [],
              "final_revalidate": [],
              "capture_first_pass": True,
              "first_pass_validate_errors": None,
              "first_pass_wrapper_errors": None}
    idxs = list(range(len(section["sheet_lines"])))
    failure = None
    try:
        await run_span(section, idxs, examples, state, record)
    except RuntimeError as exc:
        failure = str(exc)
    doc = {
        "block": section["block_id"],
        "track": "PUT N WORK (DRIXX)",
        "section": section["section"],
        "source_lyric": section["lyric"],
        "timing_source": section["timing_source"],
        "landing_rule": "landing = onset - 2 frames @ 30fps",
        "model": MODEL,
        "generated_ct": now_ct(),
        "api_routes": record["routes"],
        "receipt_request_ids": [r["request_id"] for r in record["receipts"]],
        "lines": state["lines"],
    }
    out_path = HERE / f"{section['block_id']}-director.json"
    out_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    summary = {
        "block": section["block_id"],
        "section": section["section"],
        "sheet_lines": len(section["sheet_lines"]),
        "display_lines": len(state["lines"]),
        "heroes": state["heroes"],
        "scatter_used": False,
        "calls": len(record["receipts"]),
        "cost_usd": round(sum(r["cost_usd"] for r in record["receipts"]), 6),
        "splits": record["splits"],
        "first_pass_validate_errors": record["first_pass_validate_errors"],
        "first_pass_wrapper_errors": record["first_pass_wrapper_errors"],
        "final_revalidate": record["final_revalidate"],
        "failure": failure,
        "receipts": record["receipts"],
    }
    print(json.dumps({k: v for k, v in summary.items() if k != "receipts"},
                     indent=2), file=sys.stderr)
    return summary, strip_annotations(state["lines"])


async def main():
    examples = prior_examples()
    summaries = []
    for section in TARGETS["sections"]:
        summary, lines = await run_section(section, examples)
        summaries.append(summary)
        if lines:
            examples = lines
    total = {
        "total_cost_usd": round(sum(s["cost_usd"] for s in summaries), 6),
        "total_calls": sum(s["calls"] for s in summaries),
        "first_pass_validate_reject_count": sum(
            len(s["first_pass_validate_errors"] or []) for s in summaries),
        "first_pass_wrapper_reject_count": sum(
            len(s["first_pass_wrapper_errors"] or []) for s in summaries),
        "sections_failed": [s["block"] for s in summaries if s["failure"]],
    }
    (HERE / "pnw-director-summary.json").write_text(
        json.dumps({"sections": summaries, "totals": total}, indent=2) + "\n",
        encoding="utf-8")
    print(json.dumps(total, indent=2))
    if total["sections_failed"]:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
