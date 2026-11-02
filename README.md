# BrickHouse Video Studio — video-studio-submission

A clean, squashed submission copy of the BrickHouse Video Studio event build
(Meta Hackathon, Oct 27 – Nov 4, 2026). Source of record:
`BrickHouse/video-studio-meta` @ `74cc42d` — this copy carries an allowlisted
subset of that tree under one squashed commit; the full history lives in the
source repo and is preserved as a table in [CHANGELOG.md](CHANGELOG.md).

## What this is

An agent-directed lyric-video pipeline. A song goes in; a designed,
frame-accurate lyric video comes out:

1. **Director** — `director.py` asks Muse Wonder for a per-line design plan
   (word groupings, hero word, placements, motions) as validated JSON.
   `director/cue4_director.py` is the second-half driver for the block-3
   cue-4 lines. The validated plans are in `director/*.json`, with the clean
   builder input at `director_out/block3.json`.
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
   FilmCraft over the bounced track.

## Meta APIs used, and where in code

| API / model | Where |
|---|---|
| Meta Model API — `sam-3.1` (segmentation) | `sam_api.py` — client adapted from Meta's official SAM cookbook (`07_sam/01_api_basics`); responses parsed with the `meta-sam-parser` package (see `requirements.txt`) |
| Meta Model API — `muse-wonder-1.0` (Responses API) | `director.py`, inside `call_wonder()` — the only function that calls the API; `sam_api` is imported lazily there so the offline tools/tests never touch the client |

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

Expected results: `ALL EFFECTS-BUDGET TESTS PASS` (29 checks),
`ALL TESTS PASS` (gen_config), `ALL PUNCH-HOLD TESTS PASS` (7 checks).
No API key is needed — the tests never call the Meta APIs.

## Configuration

| Variable | Used by | Meaning |
|---|---|---|
| `MODEL_API_KEY` | `sam_api.py` (`client()`) | Meta Model API key for live SAM/Wonder calls. Read from the environment at runtime; on macOS it falls back to the keychain entry the client was developed against. Never stored in this repo. |
| `BRICKHOUSE_WORKDIR` | `builder/gen_config.py`, `builder/rollout/*.py` | Directory holding the EffectCraft lyric-type projects (`.ecproj`). Defaults to the original build machine's workdir. |
| `EFFECTCRAFT_CLI` | `builder/ec_driver.py` | Path to the `effectcraft-cli` binary. Defaults to the original build machine's package path. |

## Contributors

- **BO / BrickHouse Studios** — direction, verdicts, and the build.
- AI agents (Brick, Claude) and models (Muse Wonder, SAM 3.1) participated
  as **tools** under that direction; they are not authors.

## License

Original code in this repo is MIT — see [LICENSE](LICENSE).

Attribution and upstream notes:

- This code *drives* the FilmCraft and EffectCraft applications through
  their CLIs; it does not include their code. FilmCraft and EffectCraft
  (ArtCraft) are dual-licensed MIT / Apache-2.0.
- `meta-sam-parser` is a Meta package under the SAM License.
- `sam_api.py` is adapted from Meta's official SAM API cookbook examples.
