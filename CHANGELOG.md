# CHANGELOG — provenance

This submission copy is **squashed to a single commit**. The tables below
preserve the original commits of the source repo
(`BrickHouse/video-studio-meta`) that this copy was built from, so the
event-period provenance survives the squash. Full history lives in the
source repo.

Date is each original commit's git author date; Period marks when the
*work* was built — the building period ran Oct 27 – Nov 4, 2026, and
anything built on Oct 26 or earlier is **pre-event** (the
`event/pipeline-drop` branch was committed into the source repo on
2026-11-01 during push-all; its subjects carry the original build
dates, and its Oct 26 harness commit is labeled pre-event).

## Main chain (squashed into this copy)

| Date | Commit | Subject | Period |
|---|---|---|---|
| 2026-11-01 | 6b948da | chore: initial import | event |
| 2026-11-01 | 4ff1333 | feat: Muse Wonder director (step 2) — director.py + block-3 design JSON (event-built, Nov 1) | event |
| 2026-11-01 | 409230a | feat: SAM composites — text-behind-rain + redlight halo incl. wide bloom (SUB A) (event-built, Nov 1) | event |
| 2026-11-01 | 66f675f | feat: director JSON -> EffectCraft template builder (SUB C) (event-built, Nov 1) | event |
| 2026-11-01 | 12b1bdc | chore: add scipy to requirements (sam-wide preset dependency) (event-built, Nov 1) | event |
| 2026-11-01 | f3eda9d | fix: builder reproducibility (repo-relative director JSON) + repeated-word landings keyed by index (code review) (event-built, Nov 1) | event |
| 2026-11-01 | 745f806 | director: block-3 cue-4 Wonder plan + block-3 build scripts and receipts (event-period, Nov 1) | event |
| 2026-11-01 | 8407ab6 | block3 fix: NO WAY one-line title punch at 618px — stack cuts clean at NO landing, unit inside 90% box (event-period, Nov 1) | event |
| 2026-11-01 | c2d72e1 | concept test: line-1 alt — key-word color (off-white #F2EDE4, LIGHT stays red), per-char LIGHT assemble/snap/break animators, header strip; build + render + measure scripts (event-period, Nov 1) | event |
| 2026-11-01 | 2b6c343 | block3 v3: giant WAY punch restored (1140px, 94% width, inside frame) with v2 cleanup — NO clears at WAY landing (event-period, Nov 1) | event |
| 2026-11-01 | 0786a83 | chore: recover ec_driver.py — the EC ops executor lives in the M2 lyric-type workdir (event-period tooling, Oct 31) | event |
| 2026-11-01 | ca13e71 | chore: final push-all sweep — lyric-type workshop scripts + configs from the M2 workdir (event-period, Oct 31-Nov 1) | event |
| 2026-11-01 | 3b11eb9 | chore: push-all micro-sweep — lyric-type work-r2 round-2 scratch (event-period, Oct 31) | event |
| 2026-11-01 | dde7069 | feat: director hero_color rule — hero red #FF3B1F, others off-white #F2EDE4 (concept template locked, Nov 1) | event |
| 2026-11-01 | c1bad76 | rollout phase 1: white-word contrast fix — stacked drop shadow wins grid, TEMPLATE-V2 saved (event-period, Nov 1) | event |
| 2026-11-01 | f630b07 | rollout phase 2: concept-template re-render builders for blocks 2+3 (event-period, Nov 1) | event |
| 2026-11-01 | a2fc0e9 | rollout phase 3: rough cut v2 assembly + checkers (event-period, Nov 1) | event |
| 2026-11-01 | 4b80606 | feat: director effects budget — scatter motif-only max 1/block, no repeated hero word (BO note on v2, Nov 1) | event |
| 2026-11-01 | b74a60d | rollout phase 4: rough cut v3 (effects budget) builders + assembler + checkers (event-period, Nov 1) | event |
| 2026-11-01 | 0d74812 | feat: director validate — motif scatter only on a redlight line (Nov 1) | event |
| 2026-11-01 | 02bcb1d | feat: punch holds - full-frame punches hold their sung word + 108->100 push (director rule + rough-cut v4 build scripts) (event-period, Nov 1) | event |
| 2026-11-01 | 8bd398e | docs: director — drop stale 4-6 frame punch phrase, superseded by punch-hold rule (Nov 1) | event |
| 2026-11-01 | 62929ac | fix: director backstop — scatter requires motif AND redlight; tag-prefixed validate error (Nov 1) | event |
| 2026-11-01 | e71c746 | refactor: builder punch_hold_keys() — punch holds computed from measured word-ends; v4 ops byte-identical (Nov 1) | event |
| 2026-11-02 | 74cc42d | fix: repo portability — pin/vendor meta_sam_parser, lazy sam_api import in director.py, python>=3.11 noted (Nov 1) | event |

## event/pipeline-drop branch (provenance)

Harness/pipeline commits from the same source repo. Their code is not
part of this copy's tree; they are listed because they are part of the
build's provenance.

| Date | Commit | Subject | Period |
|---|---|---|---|
| 2026-11-01 | 571ce80 | pipeline: Storyboard to FilmCraft bridge — shot cards to timeline (event-period, Oct 27) | event |
| 2026-11-01 | 62a81fd | pipeline: Storyboard to EffectCraft bridge + EC runner/probes (event-period, Oct 27) | event |
| 2026-11-01 | aac3767 | pipeline: Storyboard Studio bytes-rule changes, Stage 2A (event-period, Oct 27) | event |
| 2026-11-01 | f127054 | pipeline: context meter + agent-surface audit (event-period, Oct 27) | event |
| 2026-11-01 | 03822b7 | panel: WKWebView spike source + panel smoke drivers (event-period, Oct 27) | event |
| 2026-11-01 | ed5fe50 | pipeline: Oct 26 proof harness + sample-108 drivers (pre-event, Oct 26) | pre-event |
