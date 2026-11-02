#!/usr/bin/env python3
"""Muse Wonder "director" for the BrickHouse lyric-type template (STEP 2).

Calls muse-wonder-1.0 through the Meta Model API Responses API, reusing
sam_api.client() -- the exact same runtime auth path as the SAM work in this
repo (env MODEL_API_KEY or the M4 login-keychain item). The key is held in
memory only by sam_api.client(); this module never prints, logs, or writes it.

The director turns lyric lines + BO's locked rules into per-line JSON that
drives the EffectCraft template (SUB C consumes it):
  line_id, display_groups (tiers of words + a motion per group),
  placement (left|right|full), hero_word, size_tiers_px, redlight, reason.
  Each line also carries a hero_color record, derived in code from
  hero_word (never from the model): the hero renders #FF3B1F red, every
  other word in the line renders #F2EDE4 off-white.
  Each line also carries an effects record, derived in code at block
  level (BO's effects budget, locked 2026-11-01): the scatter
  treatment (hero letters scatter in, assemble, break apart) belongs
  ONLY to the block's one motif line -- a line the model flags
  "motif": true, tied to the redlight motif -- and a hero word that
  repeats an earlier hero in the same block is demoted (its hero_color
  record's hero_word becomes null: every word in that line renders
  off-white, no red word that line).
Model output is validated against a schema in code; invalid output is sent
back for repair (each attempt is a separate, receipted API call). Per-word
landings are computed HERE, never by the model: landing = onset - 2 frames
at 30fps, from measured bounce timings.

Receipts: every API call appends one JSONL row to receipts.log in the same
format as the SAM calls (ts CT, model, request id, units, $). Wonder pricing
basis (Meta developer pricing page, 2026-11-01): $4.00 / 1M input tokens,
$0.20 / 1M cached input tokens, $20.00 / 1M output tokens. The API returns
usage but no cost field, so $ is computed from usage at those rates.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# sam_api is imported lazily inside call_wonder() (the only API-calling
# path) so this module -- validate(), derive_records(), add_effects() and
# the offline tests -- imports cleanly without sam_api / meta_sam_parser.

HERE = Path(__file__).parent
MODEL = "muse-wonder-1.0"
FPS = 30
LEAD_FRAMES = 2
MAX_REPAIRS = 2

PRICE_IN = 4.00 / 1_000_000
PRICE_CACHED_IN = 0.20 / 1_000_000
PRICE_OUT = 20.00 / 1_000_000

MOTIONS = {"punch_in", "smear_in", "wipe_down", "full_frame_punch", "stack_build"}
PLACEMENTS = {"left", "right", "full"}
HERO_FILL = "#FF3B1F"
OTHERS_FILL = "#F2EDE4"

# ---------------------------------------------------------------- rules text
RULES = """You are the director for a BrickHouse lyric video built in EffectCraft.
You turn lyric lines into on-screen kinetic type. Follow these locked rules:

WORLD RULE (no stock, no reenactment): the background footage carries the
WORLD / MOOD / TEXTURE of the song. It NEVER illustrates the lyric literally.
The WORDS on screen perform the line. Your job is only the words: how they
group, where they sit, how they move, which word is the hero.

TEMPLATE (locked): font Anton, all caps, with a soft dark glow behind the
letters, over black-and-white footage. Display text carries NO periods and
NO commas. Text is BIG: a stack fills 40-70% of the frame height; it is
never subtitle-sized.

HERO COLOR (locked): color follows the hero. The ONE hero word of each line
renders in hero red #FF3B1F; EVERY other word in the line renders in
off-white #F2EDE4. A full-frame punch word is its line's hero and stays red.
You designate the hero (hero_word); the renderer assigns the two fills from
that designation deterministically, and a hero_color record is written into
the JSON in code -- never output colors yourself. Pick the hero as the word
that deserves the only red in the line.

EFFECTS BUDGET (locked): heroes land PLAIN by default -- a hero word lands
in red the same way the other words land in off-white, and cuts out hard.
No scatter, no break-apart. The ONE exception is the scatter treatment
(the hero's letters scatter in, assemble on the vocal, and break apart on
exit): it is a motif effect, reserved for a line tied to the redlight
motif, and at most ONE line in a block may claim it. To claim that block's
single scatter slot, set "motif": true on that line; leave every other
line without it. Never claim scatter on a line that is not the motif line.

NO REPEATED HERO (locked): a hero word may not repeat within a block. If
the word you would pick as this line's hero already headlined an earlier
line of the same block, pick a DIFFERENT word in this line as the hero.
Two lines in one block never share a hero word.

FULL-FRAME PUNCH HOLD (locked): a full-frame punch holds for its whole sung word — its out-point is the word's measured end on the bounce + 2 frames, never a fixed frame count — and pushes 108% -> 100% (ease-out) across the hold.

PLACEMENT rotates line to line: left stack -> right stack -> full frame.
Never use the same placement for two display lines in a row.

MOTION: words land ONE AT A TIME, about 2 frames before each consonant onset
(timed to the bounce; landings are computed by the caller, not by you). Use
ONLY these proven moves:
- punch_in: a word/group punches in and settles (the default build move)
- stack_build: a group builds word by word small->big inside a stack
- smear_in: a group smears in and rests dimmer (a quieter, ghosted tier)
- wipe_down: a group wipes downward into place
- full_frame_punch: ONE word fills the whole frame and holds for its sung word + 2 frames (see FULL-FRAME PUNCH HOLD), hard cut

SIZE TIERS (px, Anton cap height guide): small tier ~150, mid tier ~230,
hero tier 320-450 in stacks; a full-frame punch is 1100-1300. The HERO WORD
is the word the line turns on; it gets the biggest tier in its line.

REDLIGHT ("red = stop" motif): redlight=true ONLY when the song itself
brakes, stops, or pulls up short in that line. The effect is a white-hot core
with a deep-red halo arriving with the hero word. Most lines are false.

CADENCE: something on screen changes every 1-3 seconds, no exceptions.

REASONS: give one short reason per line, plain language, no hype."""

EXAMPLES = [
    {
        "line_id": "line1",
        "display_groups": [
            {"words": ["AND", "I"], "motion": "punch_in"},
            {"words": ["STOP", "AT"], "motion": "punch_in"},
            {"words": ["A", "LIGHT"], "motion": "stack_build"},
        ],
        "placement": "left",
        "hero_word": "LIGHT",
        "size_tiers_px": [150, 230, 400],
        "redlight": True,
        "reason": "The song brakes at the light; LIGHT is the hero and the redlight motif lands with it.",
    },
    {
        "line_id": "line2",
        "display_groups": [
            {"words": ["SHE", "PULLED"], "motion": "punch_in"},
            {"words": ["DOWN", "THE"], "motion": "smear_in"},
            {"words": ["WINDOW"], "motion": "wipe_down"},
        ],
        "placement": "right",
        "hero_word": "WINDOW",
        "size_tiers_px": [150, 230, 400],
        "redlight": False,
        "reason": "WINDOW is the action and wipes downward like the glass; DOWN THE ghosts in quieter.",
    },
    {
        "line_id": "line2-tag",
        "display_groups": [{"words": ["I", "SAID"], "motion": "punch_in"}],
        "placement": "left",
        "hero_word": "SAID",
        "size_tiers_px": [175],
        "redlight": False,
        "reason": "A small fast tag in its own spot right before the punch.",
    },
    {
        "line_id": "line2-punch",
        "display_groups": [{"words": ["HEY"], "motion": "full_frame_punch"}],
        "placement": "full",
        "hero_word": "HEY",
        "size_tiers_px": [1250],
        "redlight": False,
        "reason": "One word eats the whole frame for a few frames, then hard cut.",
    },
]

# ------------------------------------------------------------------- targets
# Block 3 of track 108. Word onsets measured on the BOUNCE with the house
# whisper-large-v3 lane (two overlapping segments, cross-checked; +-0.15s).
# The bounce sings ahead of the SRT grid (board window 30.14-33.42 SRT).
BLOCK3 = {
    "block_id": "block3",
    "lyric": "She said where I'm from, I told her I'm not around.",
    "board_window_srt_s": [30.14, 33.42],
    "words": [
        {"word": "SHE", "onset_s": 30.26},
        {"word": "SAID", "onset_s": 30.45},
        {"word": "WHERE", "onset_s": 30.84},
        {"word": "I'M", "onset_s": 31.05},
        {"word": "FROM", "onset_s": 31.32},
        {"word": "I", "onset_s": 31.77},
        {"word": "TOLD", "onset_s": 31.90},
        {"word": "HER", "onset_s": 32.16},
        {"word": "I'M", "onset_s": 32.39},
        {"word": "NOT", "onset_s": 32.67},
        {"word": "AROUND", "onset_s": 32.96},
    ],
}
TARGETS = {"block3": BLOCK3}


# ------------------------------------------------------------------ receipts
def now_ct() -> str:
    return datetime.now(ZoneInfo("America/Chicago")).isoformat(timespec="seconds")


def append_receipt(row: dict) -> None:
    with open(HERE / "receipts.log", "a", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")


def log_call(step: str, kind: str, resp: dict, note: str | None = None) -> dict:
    usage = resp.get("usage") or {}
    in_tok = usage.get("input_tokens") or 0
    out_tok = usage.get("output_tokens") or 0
    cached = ((usage.get("input_tokens_details") or {}).get("cached_tokens")) or 0
    fresh_in = max(in_tok - cached, 0)
    cost = fresh_in * PRICE_IN + cached * PRICE_CACHED_IN + out_tok * PRICE_OUT
    row = {
        "ts_ct": now_ct(),
        "step": step,
        "kind": kind,
        "model": resp.get("model") or MODEL,
        "request_id": resp.get("id"),
        "units": usage.get("total_tokens") or (in_tok + out_tok),
        "unit": "tokens",
        "input_tokens": in_tok,
        "cached_input_tokens": cached,
        "output_tokens": out_tok,
        "unit_price_usd": {"input": 4.0, "cached_input": 0.2, "output": 20.0},
        "unit_price_basis": "per 1M tokens, Meta developer pricing page 2026-11-01",
        "cost_usd": round(cost, 6),
    }
    if note:
        row["note"] = note
    append_receipt(row)
    return row


# ------------------------------------------------------------------ api call
def build_prompt(target: dict, errors: list[str] | None, bad_text: str | None) -> str:
    words = " ".join(
        f"{w['word']}@{w['onset_s']:.2f}s" for w in target["words"]
    )
    prompt = (
        RULES
        + "\n\nFORMAT EXAMPLES (already built and approved; match this shape exactly):\n"
        + json.dumps({"lines": EXAMPLES}, indent=2)
        + "\n\nTARGET — block 3 of the song. Raw lyric: \""
        + target["lyric"]
        + "\"\nMeasured word onsets on the bounce (seconds, song time): "
        + words
        + "\nSplit the lyric into display lines as the phrasing demands. "
        "Use EVERY word of the lyric exactly once, in order, across your lines. "
        "Display words are uppercase with no periods or commas.\n\n"
        "OUTPUT CONTRACT: reply with ONLY a JSON object, no prose, no code fences:\n"
        '{"lines": [{"line_id": "block3-line1", '
        '"display_groups": [{"words": ["..."], "motion": "punch_in"}], '
        '"placement": "left", "hero_word": "...", "size_tiers_px": [150], '
        '"redlight": false, "reason": "..."}]}'
        "\nDo not output colors: the renderer records a hero_color entry per "
        "line from your hero_word (hero #FF3B1F, all other words #F2EDE4)."
        "\nEffects budget: heroes land plain. You may set \"motif\": true on "
        "at most ONE line of the block -- only a redlight-motif line -- to "
        "claim its single scatter treatment; never output an \"effects\" "
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


async def call_wonder(prompt: str) -> tuple[str, dict, str]:
    """One Responses API call. Returns (text, response_dict, route)."""
    import sam_api  # lazy: only the API generation path needs the SAM client

    async with sam_api.client() as api:
        try:
            raw = await api.with_raw_response.responses.create(
                model=MODEL,
                input=[
                    {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}],
                    }
                ],
            )
            resp = raw.parse()
            data = resp.model_dump()
            return data.get("output_text") or extract_text(data), data, "non-streaming"
        except Exception as exc:
            if "stream" not in str(exc).lower():
                raise
            # Live-surface fallback: some models on this API require streaming.
            stream = await api.responses.create(
                model=MODEL,
                stream=True,
                input=[
                    {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}],
                    }
                ],
            )
            text_parts: list[str] = []
            final: dict = {}
            async with stream:
                async for event in stream:
                    data = (
                        event.model_dump()
                        if hasattr(event, "model_dump")
                        else dict(event)
                    )
                    if data.get("type") == "response.output_text.delta":
                        text_parts.append(data.get("delta") or "")
                    if data.get("type") == "response.completed":
                        final = data.get("response") or {}
            return "".join(text_parts), final, "streaming-fallback"


def extract_text(data: dict) -> str:
    parts: list[str] = []
    for item in data.get("output") or []:
        for content in item.get("content") or []:
            if content.get("type") == "output_text":
                parts.append(content.get("text") or "")
    return "".join(parts)


# ---------------------------------------------------------------- validation
def normalize(word: str) -> str:
    return re.sub(r"[.,!?'’]", "", word.strip().upper())


def validate(
    candidate: dict,
    target: dict,
    prior_heroes: list[str] | None = None,
    prior_scatter_used: bool = False,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(candidate, dict) or not isinstance(candidate.get("lines"), list):
        return ["top level must be an object with a 'lines' array"]
    lines = candidate["lines"]
    if not lines:
        return ["'lines' is empty"]
    # Effects-budget block state (BO, locked 2026-11-01): heroes already
    # used in this block, and whether its single scatter slot is taken.
    # prior_* carry the state of earlier lines of the same block that are
    # not part of this candidate (cue4_director passes block 3's first
    # half). The renderer-side backstop is add_effects().
    seen_heroes: list[str] = [normalize(h) for h in (prior_heroes or [])]
    scatter_used = bool(prior_scatter_used)
    motif_claims = 1 if scatter_used else 0
    target_seq = [normalize(w["word"]) for w in target["words"]]
    got_seq: list[str] = []
    prev_placement: str | None = None
    for i, line in enumerate(lines):
        tag = f"line {i} ({line.get('line_id', '?')})"
        if not isinstance(line, dict):
            errors.append(f"{tag}: not an object")
            continue
        for field in ("line_id", "display_groups", "placement", "hero_word",
                      "size_tiers_px", "redlight", "reason"):
            if field not in line:
                errors.append(f"{tag}: missing field '{field}'")
        groups = line.get("display_groups") or []
        if not (1 <= len(groups) <= 4):
            errors.append(f"{tag}: display_groups must have 1-4 groups")
        line_words: list[str] = []
        for g in groups:
            if not isinstance(g, dict) or not isinstance(g.get("words"), list) or not g["words"]:
                errors.append(f"{tag}: each group needs a non-empty 'words' list")
                continue
            if g.get("motion") not in MOTIONS:
                errors.append(f"{tag}: motion '{g.get('motion')}' not in {sorted(MOTIONS)}")
            for w in g["words"]:
                if re.search(r"[.,!?]", str(w)):
                    errors.append(f"{tag}: display word '{w}' contains punctuation")
                line_words.append(normalize(str(w)))
        got_seq.extend(line_words)
        placement = line.get("placement")
        if placement not in PLACEMENTS:
            errors.append(f"{tag}: placement '{placement}' not in {sorted(PLACEMENTS)}")
        if placement is not None and placement == prev_placement:
            errors.append(f"{tag}: placement repeats the previous line ('{placement}')")
        prev_placement = placement
        if placement == "full":
            if len(groups) != 1 or (groups and groups[0].get("motion") != "full_frame_punch"):
                errors.append(f"{tag}: full placement needs exactly one full_frame_punch group")
        tiers = line.get("size_tiers_px") or []
        if len(tiers) != len(groups):
            errors.append(f"{tag}: size_tiers_px length {len(tiers)} != groups {len(groups)}")
        for t in tiers:
            if not isinstance(t, int) or not (100 <= t <= 1300):
                errors.append(f"{tag}: size tier '{t}' not an int in 100..1300")
        hero = normalize(str(line.get("hero_word", "")))
        if hero not in line_words:
            errors.append(f"{tag}: hero_word '{line.get('hero_word')}' is not one of the line's words")
        elif len(tiers) == len(groups) and groups:
            hero_gi = next(
                gi for gi, g in enumerate(groups)
                if hero in [normalize(str(w)) for w in g.get("words", [])]
            )
            if tiers and tiers[hero_gi] != max(tiers):
                errors.append(f"{tag}: hero group's tier {tiers[hero_gi]} is not the max {max(tiers)}")
            if len(tiers) > 1 and list(tiers).count(max(tiers)) > 1:
                errors.append(f"{tag}: hero tier must be the unique max")
        motif = line.get("motif")
        if motif is not None and not isinstance(motif, bool):
            errors.append(f"{tag}: motif must be a boolean when present")

        if motif is True and line.get("redlight") is not True:
            errors.append(f"{tag}: motif scatter only on a redlight line")
        if line.get("scatter") is True and motif is not True:
            errors.append(
                f"{tag}: scatter claimed without motif -- the scatter "
                "treatment belongs only to the block's one motif line "
                "(set \"motif\": true on that line, and on no other)"
            )
        if hero and hero in seen_heroes:
            errors.append(
                f"{tag}: hero_word '{line.get('hero_word')}' repeats an "
                "earlier hero in this block -- a hero word may not repeat "
                "within a block; pick a different hero for this line"
            )
        hero_color = line.get("hero_color")
        effects = line.get("effects")
        if hero_color is not None or effects is not None:
            hero_raw = line.get("hero_word")
            if isinstance(hero_raw, str) and hero_raw.strip():
                expected_color, expected_effects = derive_records(
                    line, seen_heroes, scatter_used
                )
                if hero_color is not None and hero_color != expected_color:
                    errors.append(
                        f"{tag}: hero_color {hero_color!r} does not match the "
                        f"deterministic record {expected_color!r} (colors derive "
                        "from hero_word in code, never from model output)"
                    )
                if effects is not None and effects != expected_effects:
                    errors.append(
                        f"{tag}: effects {effects!r} does not match the "
                        f"deterministic record {expected_effects!r} (effects "
                        "derive from the block budget in code, never from "
                        "model output)"
                    )
        if hero:
            seen_heroes.append(hero)
        if motif is True:
            motif_claims += 1
            scatter_used = True
        if not isinstance(line.get("redlight"), bool):
            errors.append(f"{tag}: redlight must be a boolean")
        reason = line.get("reason")
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 240:
            errors.append(f"{tag}: reason must be a non-empty string <= 240 chars")
    if motif_claims > 1:
        errors.append(
            f"effects budget: {motif_claims} motif/scatter claims in this "
            "block; at most ONE line per block may claim the motif scatter "
            "slot"
        )
    if got_seq != target_seq:
        errors.append(
            "word sequence mismatch: got ["
            + " ".join(got_seq)
            + "] but the lyric is ["
            + " ".join(target_seq)
            + "] (every lyric word exactly once, in order)"
        )
    return errors


def parse_candidate(text: str) -> dict:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object found in model output")
    return json.loads(cleaned[start : end + 1])


# ------------------------------------------------------------------ landings
def add_landings(lines: list[dict], target: dict) -> list[dict]:
    onsets = target["words"]
    pos = 0
    out: list[dict] = []
    for line in lines:
        landings: list[dict] = []
        for group in line["display_groups"]:
            for word in group["words"]:
                onset = onsets[pos]["onset_s"]
                landing_s = onset - LEAD_FRAMES / FPS
                landings.append(
                    {
                        "word": word,
                        "onset_s": onset,
                        "landing_s": round(landing_s, 3),
                        "landing_frame": round(landing_s * FPS),
                    }
                )
                pos += 1
        out.append({**line, "landings": landings})
    if pos != len(onsets):
        raise RuntimeError(f"landing assignment consumed {pos} of {len(onsets)} words")
    return out


# --------------------------------------------------------------- hero color
def hero_color_record(line: dict) -> dict:
    hero = line.get("hero_word")
    if not isinstance(hero, str) or not hero.strip():
        raise RuntimeError(
            f"line {line.get('line_id', '?')}: no designated hero_word; "
            "hero_color cannot be recorded"
        )
    return {"hero_word": hero, "hero_fill": HERO_FILL, "others_fill": OTHERS_FILL}


def add_hero_color(lines: list[dict]) -> list[dict]:
    """Record per-line colors deterministically from the hero designation.

    Concept template (locked 2026-11-01, BO): ONLY the line's hero word
    renders HERO_FILL red; every other word renders OTHERS_FILL off-white.
    Derived here in code from hero_word -- never from model prose -- and
    written into the JSON right after hero_word. Raises if a line has no
    designated hero (validate() already rejects that upstream).
    """
    out: list[dict] = []
    for line in lines:
        record = hero_color_record(line)
        new_line: dict = {}
        for key, value in line.items():
            if key == "hero_color":
                continue
            new_line[key] = value
            if key == "hero_word":
                new_line["hero_color"] = record
        if "hero_color" not in new_line:
            new_line["hero_color"] = record
        out.append(new_line)
    return out


# ------------------------------------------------------------ effects budget
def derive_records(line: dict, seen_heroes: list[str], scatter_used: bool) -> tuple[dict, dict]:
    """Deterministic (hero_color, effects) records for one line, given the
    block state BEFORE it: the block's earlier heroes (normalized) and
    whether its scatter slot is already taken.

    Demotion: if the line's hero repeats an earlier hero in the block,
    the hero_color record's hero_word becomes None (renderer rule: null
    = every word in the line renders others_fill, no red word that line)
    and demoted_from/reason say why. Scatter: true only when the line
    claims the motif slot ("motif": true) and the slot is still free.
    """
    record = hero_color_record(line)
    demoted = normalize(str(line.get("hero_word", ""))) in seen_heroes
    if demoted:
        record = {
            "hero_word": None,
            "hero_fill": HERO_FILL,
            "others_fill": OTHERS_FILL,
            "demoted_from": line.get("hero_word"),
            "reason": "repeat_hero_in_block",
        }
    scatter = line.get("motif") is True and line.get("redlight") is True and not scatter_used
    return record, {"scatter": scatter, "hero_demoted": demoted}


def add_effects(
    lines: list[dict],
    prior_heroes: list[str] | None = None,
    prior_scatter_used: bool = False,
) -> list[dict]:
    """Write each line's effects record (and demote repeated heroes).

    BO's effects budget (locked 2026-11-01, after rough cut v2 read as
    overdone): the scatter treatment -- hero letters scatter in,
    assemble on the vocal, break apart on exit -- belongs ONLY to the
    block's first motif-claiming line; every other hero lands plain
    in red and cuts out hard. A line whose hero_word repeats an earlier
    hero in the same block is DEMOTED (see derive_records). Records are
    derived here in code from hero_word + motif, never from model
    prose; hero_color is re-derived in the same pass so demotion and
    color stay one source of truth, and effects is written right after
    hero_color. prior_* carry block context for runs that direct only
    part of a block (cue4_director passes block 3's first-half state).
    """
    seen: list[str] = [normalize(h) for h in (prior_heroes or [])]
    scatter_used = bool(prior_scatter_used)
    out: list[dict] = []
    for line in lines:
        record, effects = derive_records(line, seen, scatter_used)
        if line.get("motif") is True:
            scatter_used = True
        hero = line.get("hero_word")
        if isinstance(hero, str) and hero.strip():
            seen.append(normalize(hero))
        new_line: dict = {}
        for key, value in line.items():
            if key in ("hero_color", "effects"):
                continue
            new_line[key] = value
            if key == "hero_word":
                new_line["hero_color"] = record
                new_line["effects"] = effects
        if "hero_color" not in new_line:
            new_line["hero_color"] = record
            new_line["effects"] = effects
        out.append(new_line)
    return out


# ---------------------------------------------------------------------- main
async def direct(target: dict, step: str) -> tuple[dict, list[dict], list[str]]:
    receipts: list[dict] = []
    errors: list[str] | None = None
    bad_text: str | None = None
    routes: list[str] = []
    for attempt in range(MAX_REPAIRS + 1):
        prompt = build_prompt(target, errors, bad_text)
        text, resp, route = await call_wonder(prompt)
        routes.append(route)
        kind = "wonder_director_call" if attempt == 0 else "wonder_director_repair"
        note = f"route={route}; attempt={attempt}"
        if errors:
            note += "; fixing: " + "; ".join(errors)[:300]
        receipts.append(log_call(step, kind, resp, note=note))
        try:
            candidate = parse_candidate(text)
            errors = validate(candidate, target)
        except (ValueError, json.JSONDecodeError) as exc:
            candidate = {}
            errors = [f"unparseable JSON output: {exc}"]
        if not errors:
            return candidate, receipts, routes
        bad_text = text
        print(f"attempt {attempt}: {len(errors)} validation error(s)", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
    raise RuntimeError(f"director output still invalid after {MAX_REPAIRS} repairs: {errors}")


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", default="block3", choices=sorted(TARGETS))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    target = TARGETS[args.block]
    out_path = Path(args.out) if args.out else HERE / "director" / f"{args.block}-director.json"
    step = f"2-director-{args.block}"
    candidate, receipts, routes = await direct(target, step)
    lines = add_landings(candidate["lines"], target)
    lines = add_hero_color(lines)
    lines = add_effects(lines)
    doc = {
        "block": target["block_id"],
        "track": "108 VOX1_01",
        "source_lyric": target["lyric"],
        "board_window_srt_s": target["board_window_srt_s"],
        "timing_source": (
            "house whisper-large-v3 on the bounce (two overlapping segments, "
            "onsets cross-checked, +-~0.15s); bounce sings ahead of the SRT grid"
        ),
        "landing_rule": f"landing = onset - {LEAD_FRAMES} frames @ {FPS}fps",
        "model": MODEL,
        "generated_ct": now_ct(),
        "api_routes": routes,
        "receipt_request_ids": [r["request_id"] for r in receipts],
        "lines": lines,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    print(json.dumps({"lines": len(lines), "receipts": receipts}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
