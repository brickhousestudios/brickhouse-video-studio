# BrickHouse Video Studio — video-studio-submission

A clean, squashed submission copy of the BrickHouse Video Studio event build
(Meta Hackathon, Oct 27 – Nov 4, 2026). Source of record:
`BrickHouse/video-studio-meta` @ `e4c4987` — this copy carries an allowlisted
subset of that tree, first squashed to a single commit on Nov 2 and re-synced
with one additional commit on Nov 4; the full history lives in the
source repo and is preserved as a table in [CHANGELOG.md](CHANGELOG.md).

## What this is

An agent-directed lyric-video pipeline. A song goes in; a designed,
frame-accurate lyric video comes out:

1. **Director** — `director.py` asks Muse Wonder for a per-line design plan
   (word groupings, hero word, placements, motions) as validated JSON.
   `director/cue4_director.py` is the second-half driver for the block-3
   cue-4 lines. The validated plans are in `director/*.json`, with the clean
   builder input at `director_out/block3.json`. `director/rest_director.py`
   chains the planning across the rest of the song (blocks 4–5 plans:
   `director/block4-director.json`, `director/block5-director.json`), and
   `validate()` enforces the full-frame rotation rule — no more than 2
   consecutive lines without a full-frame placement.
2. **Masks** — `sam_api.py` calls SAM 3.1 for segmentation masks over the
   footage (e.g. raindrops on glass, headlight bloom), composited so the
   lyric type sits *behind* the rain.
3. **Builder** — `builder/gen_config.py` turns a director JSON into an
   EffectCraft driver config (landings computed in code at onset − 2 frames);
   `builder/ec_driver.py` executes the ops against the EffectCraft CLI;
   `builder/rollout/` holds the phase build/check scripts that assembled the
   locked section, including `punch_hold_keys()` (full-frame punches hold
   their sung word + 2 frames with a 108% → 100% push).
4. **Output** — the locked section of the "108" lyric video
   (song 22.64s–37.20s, rough cut v4) was assembled from these builds in
   FilmCraft over the bounced track. The same chain then reproduced that
   section inside FilmCraft and built the full song (rough cut v5.2): the
   driver configs are in `builder/ext-2026-11-03/` and
   `builder/repro-2026-11-03/`, and `builder/word-gate/word_gate.py` gates
   the on-screen words against the approved baseline in code.
5. **Timing cross-check** — `voice_transcribe.py` runs Muse Voice
   Transcribe on the bounce for section-level line timing, cross-checked
   against the house whisper word grid (section-level only — word timing
   stays with whisper).
6. **Title/end cards** — `image_cards.py` generates the title and end
   cards: Muse Image plates, typeset in PIL in the locked look.

## Meta APIs used, and where in code

| API / model | Where |
|---|---|
| Meta Model API — `sam-3.1` (segmentation) | `sam_api.py` — client adapted from Meta's official SAM cookbook (`07_sam/01_api_basics`); responses parsed with the `meta-sam-parser` package (see `requirements.txt`) |
| Meta Model API — `muse-wonder-1.0` (Responses API) | `director.py`, inside `call_wonder()` — the only function that calls the API; `sam_api` is imported lazily there so the offline tools/tests never touch the client |
| Meta Model API — Muse Voice Transcribe (ASR) | `voice_transcribe.py` — transcribes the bounced track for **section-level** line timing (turn-level timestamps), cross-checked against the whisper word grid; never used for word-level timing |
| Meta Model API — `muse-image-1.0` | `image_cards.py` — generates the title/end card plates; type is set in PIL in the locked look |

Live API use is the only networked path. Everything else in this repo —
validation, annotation, config generation, and all tests — runs offline.

## Run the offline tests

Requires Python ≥ 3.11 (see `.python-version`; developed on 3.12 — the
system Python 3.9 on some machines will not work).

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python director/test_effects_budget.py
.venv/bin/python builder/test_gen_config.py
.venv/bin/python builder/rollout/test_punch_hold.py
```

Expected results: `ALL EFFECTS-BUDGET TESTS PASS` (35 checks),
`ALL TESTS PASS` (gen_config), `ALL PUNCH-HOLD TESTS PASS` (7 checks).
No API key is needed — the tests never call the Meta APIs.

## Configuration

| Variable | Used by | Meaning |
|---|---|---|
| `MODEL_API_KEY` | `sam_api.py` (`client()`) | Meta Model API key for live SAM/Wonder calls. Read from the environment at runtime; on macOS it falls back to the keychain entry the client was developed against. Never stored in this repo. |
| `BRICKHOUSE_WORKDIR` | `builder/gen_config.py`, `builder/rollout/*.py` | Directory holding the EffectCraft lyric-type projects (`.ecproj`). Required, with no default: `builder/paths.py` raises a clear error naming the var when it is unset. The offline tests do not need it. |
| `BRICKHOUSE_WORKDIR` (recorded placeholder) | `builder/ext-2026-11-03/*.json`, `builder/repro-2026-11-03/*.json` driver configs | The recorded build/render configs spell the workdir as the literal placeholder `${BRICKHOUSE_WORKDIR}`; substitute your own workdir path before replaying a config. |
| `EFFECTCRAFT_CLI` | `builder/ec_driver.py` | Path to the `effectcraft-cli` binary. Required, with no default: `builder/paths.py` raises a clear error naming the var when it is unset. The offline tests do not need it. |

## Contributors

- **BO / BrickHouse Studios** — direction, verdicts, and the build.
- AI agents (Brick, Claude) and models (Muse Wonder, SAM 3.1, Muse Voice
Transcribe, Muse Image) participated
  as **tools** under that direction; they are not authors.

## License

Original code in this repo is MIT — see [LICENSE](LICENSE).

Attribution and upstream notes:

- This code *drives* the FilmCraft and EffectCraft applications through
  their CLIs; it does not include their code. FilmCraft and EffectCraft
  (ArtCraft) are dual-licensed MIT / Apache-2.0.
- `meta-sam-parser` is a Meta package under the SAM License.
- `sam_api.py` is adapted from Meta's official SAM API cookbook examples.
