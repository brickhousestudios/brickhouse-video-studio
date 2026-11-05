# PUT N WORK — Plan-Pipeline Readiness

**Status: PREP ONLY. Nothing has been transcribed or directed. The single
blocking input is BO's master pick.**

Prepared 2026-11-02. Everything below is census (read-only) + harness code.
No PUT N WORK audio has been run through whisper or director.py, and
nothing here leaves BrickHouse.

## Candidate census — claimed vs measured (ffprobe)

| Candidate (Claude's list) | Claimed | Found at | Size (bytes) | Measured | Verdict |
|---|---|---|---|---|---|
| V3 | 3:44 | `/Volumes/STICK/108 N DRIZZZ/PUT N WORK MASTER V3/Bounced Files/PUT N WORK MASTER V3.wav` | 64,845,922 | 223.968 s (3:44.0) | ✅ VERIFIED |
| V3 (dupe bounce) | — | `…/Bounced Files/PUT N WORK MASTER V3_1.wav` | 64,845,922 | 223.968 s | duplicate of V3 |
| FM | 2:44 | `…/PUT N WORK MASTER V3/Audio Files/PUT N WORK MASTER FM.L.wav` + `FM.R.wav` (stereo split pair) | 23,737,892 ea | 163.968 s ea (2:44.0) | ✅ VERIFIED |
| rescue | 2:47 | `/Volumes/STICK/M4_MAC_RESCUE_2026/Downloads/PUT N WORK MASTER.wav` | 32,410,658 | 167.467 s (2:47.5) | ✅ VERIFIED |
| rescue (mirror) | — | `/Volumes/STICK/M4_MAC_RESCUE_2026/Downloads_KEEP/PUT N WORK MASTER.wav` | 32,410,658 | 167.467 s, md5 identical | byte-for-byte mirror |
| vocals stem | 3:56 | — | — | — | ❌ NOT FOUND anywhere searched |
| *(extra, unlisted)* V1 mix | — | `/Volumes/STICK/108 N DRIZZZ/PUT N WORK DRIXX 208_V1.wav` | 34,053,802 | 175.957 s (2:56.0) | extra candidate, not in Claude's list |

The V3 session (Pro Tools, `PUT N WORK MASTER V3.ptx`) lives at
`/Volumes/STICK/108 N DRIZZZ/PUT N WORK MASTER V3/`; its Audio Files folder
holds only the FM pair. `/Volumes/STICK/PUTNWORK COVER IDEAS/` is artwork
only (jpg/mp4), no audio, no lyrics.

**Where searched:** VM home (full pruned find); M4 home
(Desktop/Documents/Music/Downloads/BrickHouse/Projects + full-home audio
sweep) and the full M4-BOOT volume (name sweep ran to completion, 343 s);
M2 home folders + `/Volumes/STICK/BrickHouse`; then STICK-wide sweeps to
depth 4 and depth 6 — which is where every hit above came from. Name
patterns: `put n work / putnwork / put_in_work / pnw / rescue / stem /
lyric` (+ a `*put*` file sweep). Only false positives elsewhere
(`output_vox2_tunechi.wav`, node_modules noise, NBA reference stems).

## Lyric sheet status

❌ **The timed lyric sheet (claimed grid 3:14) was NOT found** on any
searched machine. Closest artifact:
`/Volumes/STICK/M4_MAC_RESCUE_2026/Downloads/PUT N WORK MASTER_transcription.txt`
(+ a mirror in Downloads_KEEP) — 510 words, a single untimed paragraph of
noisy ASR sitting beside the rescue master. It carries the lyrics
(hook: "put in work" recurring) but **no timestamps and no line grid** —
it is not the 3:14 sheet. The timed sheet may live in Notion/Docs rather
than fleet files; BO/Claude to point at it.

**Flag for the stress test:** no verified candidate is 3:14 long
(3:44 / 2:56 / 2:47 / 2:44). If the sheet's grid really spans 3:14, it
matches none of these masters end-to-end — grid drift is not a
hypothetical here, it's the first thing the run will measure.

## Harness — `plan_harness.py` (this folder)

Parameterized: `--audio <file> --lyrics <file> --out <dir>
[--director-dir <video-studio-meta/director>] [--dry-run]`.
Full runs are **gated**: they refuse unless `PNW_MASTER_CONFIRMED=1` is in
the environment, so the harness can never transcribe a guessed master by
accident.

Stages (a–e as specced):
- (a) ffprobe duration — done at runtime.
- (b) slice plan: 120 s slices, 10 s overlap, 40 kbps mono mp3; every
  slice's estimated base64 payload asserted < 950,000 chars (the
  house-whisper fabrication ceiling; ~142 s is the hard max at 40 kbps).
- (c) house-whisper per slice via the hub client pattern from
  `~/workspace/transcription-test/call_house.py` (hub__call_tool_v2 →
  brickhouse-whisper/transcribe_audio_mcp), with the payload guard and
  the canned-fake-transcript refusal. **Code-complete, UNRUN.**
- (d) stitch: per-slice timed lines re-based onto the song grid,
  first-coverage-wins in overlap zones. **Code-complete, UNRUN** (written
  against the response shape the 108 lane received; first real run must
  eyeball the raw response before trusting the grid).
- (e) stress report (JSON): timing drift (sheet vs whisper offsets at
  start/middle/end), repeated hooks (normalized duplicate sheet lines →
  hero-repeat exposure), hero repeats per block (blocks split on >4 s
  grid gaps), validator rejects (from the director stage), payload-safety
  stats (slice count, max payload vs ceiling).

Director stage imports director.py **in place** from video-studio-meta
(path parameterized, never copied). Its per-line wiring is stubbed to the
module's public surface (validate / hero-color / effects derivation) and
gets finalized against the real call shape on the first sanctioned run —
recording exactly where it rejects is the stress test's job.

**Validation so far — `--selftest` on synthetic silence ONLY (PASS):**
a generated 4-minute silent wav → 3 slices, gapless overlap coverage,
slice-0 estimate 800,000 b64 chars vs 800,520 actual encoded, all slices
under the 950,000 ceiling. No real audio was sliced; `--dry-run` was not
pointed at any candidate.

## What runs the minute BO picks

1. BO names the master (V3 / FM / rescue / the V1 extra / the stem if it
   surfaces) **and** the lyric sheet's location (or confirms the rescue
   transcription is the sheet of record despite having no grid).
2. `PNW_MASTER_CONFIRMED=1 python3 plan_harness.py --audio <pick>
   --lyrics <sheet> --out runs/<pick>/ --director-dir <…/director>`
3. Stress report answers: Does the whisper grid drift against the sheet
   grid across 3+ minutes, and by how much at start/middle/end? Which
   lines repeat (hooks) and do their natural heroes collide inside a
   block under the no-repeat-hero budget? How many lines does
   director.py's validator reject, and why? Were all payloads safely
   under the fabrication ceiling?
4. Report lands here for BO/Claude before any footage or build talk —
   planning only, per the agreed order: timing → director plan →
   BO's verdict → only then footage.

## DECISION — master picked (2026-11-04, BO delegated the pick to Brick)

BO (2026-11-04 08:03 CT): "put n work is next and u can pick any mp3/wav as the master." The earlier struck V3 attribution stays struck as history; this pick is Brick's, on receipts:

- **PICK: V3** — `/Volumes/STICK/108 N DRIZZZ/PUT N WORK MASTER V3/Bounced Files/PUT N WORK MASTER V3.wav`, 223.968 s, 64,845,922 B (afinfo + stat re-verified 2026-11-04 via M4→M2 SSH side door).
- Decisive receipt: BO's lyric sheet (SRT, same folder as before) grids the song HOOK/VERSE1/BRIDGE/HOOK/VERSE2/FINAL HOOK with **"Song ends at 3:14" (194 s)**. V1 (175.957 s), Rescue (167.467 s) and the FM pair (163.968 s) all END before the sheet's final hook finishes — they physically cannot contain the sheet's arrangement. The vocals stem (235.653 s) is vocals-only, not a mix. V3 is the only full mix that contains the whole sheet, and it is the session's own named MASTER bounce.
- Open measurement: V3 runs 223.968 s vs the sheet grid ending 194 s — a ~30 s delta (intro/outro/count-in class). The stress run's first job is to locate the sections inside V3 and measure the drift; the pick is structural, not ear-verified.
- Gate state: PNW_MASTER_CONFIRMED is now satisfied by BO's delegation + this pick. Sequence: pull V3 local after the v5.2 pull clears the hub channel, then fire the harness stress run (timing only — no footage, no build) per the agreed order.
