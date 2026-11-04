# 108 — In-FilmCraft Reproduction Build — 2026-11-03 (lane: this subagent)

## Mandate (BO, via parent)
Reproduction proof is THE deliverable: locked v4 section (song 22.64–37.20, blocks 1–3)
rebuilt inside FilmCraft via the pipeline, frame-compared vs the locked mp4
(sha256 3bce86e1…, VM copy verified). Full-song extension queues behind it.
Panel-drivability must be verified/reported. CPU only (GPU halt rule).

## (a) FINAL project contents (file parsed on VM from M2 bytes, 15,085 B JSON)
Project: 108-rough-cut-FINAL-2026-11-03.fcproj (schema 15), ONE sequence
"Rough Cut - 108 (song 22.64-29.54)" (id 3):
- V1: seg-A-block1-plain f679/35f · seg-B-line1-redlight-v3 f714/71f ·
  seg-C-she-pulled-v4 f785/55f · seg-D-hey-isaid-v4 f840/33f · seg-E-block2-plain f873/13f
  (V1 covers only 22.63–29.53s)
- V2: rough-cut-v4-2026-11-01.mp4 itself at f679/437f (reference layer)
- A1: bounce 0–22.633s · v4's own AAC 22.633–37.20 · bounce resumes 37.20→182.37
  (FilmCraft MP3 probe caps the item at 5471f ≈ 182.37s — known probe artifact)
Media items: 5 segs + bounce + the v4 mp4. All media in
${BRICKHOUSE_WORKDIR}/ (+ bounce in pipeline-stage2b/media/).

## Span-source verification (ffmpeg PSNR vs locked v4 spans, run ON the M2)
Reference floor: master frames_all_plan PNGs vs locked v4 decode = PSNR ≈ 43.2 dB
(the locked file's own crf-14 encode noise). True sources score ~40–45; wrong
renders score 14–23.
- seg-A (FINAL V1) vs [0:35]      = 41.13 dB  TRUE SOURCE ✓
- seg-B (FINAL V1) vs [35:106]   = 21.50 dB  NOT the cut's line1 (v3 render ≠ v2 seg)
- seg-C (FINAL V1) vs [106:161]  = 22.57 dB  NOT the cut's rain span
- seg-D (FINAL V1) vs [161:194]  = 19.10 dB  NOT comp B
- seg-E (FINAL V1) vs [194:207]  = 14.58 dB  NOT the foot span
- seg-cue4-v3 (M2) vs [314:422]  = 17.01 dB  NOT take2-v6 cue4
- seg-S5-foot2 (encoded on M2 from foot-block2.mp4 frames 33–49, assemble_rc4
  recipe) vs [201:218]           = 44.86 dB  TRUE SOURCE ✓ (in lyric-type/repro/)

## True-source media for the reproduction (rc4 frame plan, 437f)
S1 [679,35f] seg-A (M2, in FINAL) · S2 [714,71f] seg-line1-v2.mp4 (VM seg) ·
S3 [785,55f] rain f008–f062 from work-rc3/rain → crf10 seg (VM) ·
S4 [840,40f] seg-b2b-v4.mp4 (VM seg) · S5 [880,17f] seg-S5-foot2 (M2 ✓) ·
S6 [897,50f] b3l13 jpgs → seg (VM) · S7 [947,46f] b3l23 jpgs → seg (VM) ·
S8 [993,111f] seg-b3c4-v4.mp4 (VM seg) · S9 [1104,12f] bed tail f207–218 of
bed-block3-recede-v4.mp4 → seg (VM). VM segs shas (16): S2 ea6eb8202436a952 ·
S3 d63759ed56558c11 · S4 158b8bded980731f · S6 b03238fb3ac5fd77 ·
S7 20c4392609959d6d · S8 eccfe50e6901ec3d · S9 1ce63af6f0ec4228.
Transfer: VM →(base64 chunks via hub, size-polled)→ M4 /tmp/repro-xfer
→(scp, house key)→ M2 lyric-type-2026-10-31/repro/ → sha256 verify on M2.

## Tooling facts banked this run
- filmcraft-cli export supports --gpu-rendering off (CPU export) + png format.
- Bridge auth env var: FILMCRAFT_CONTROL_TOKEN (from app process env, in-shell only).
- Command ids: file.newSequence, timeline.place {item, track, seconds,
  duration(ticks)}, clip.rename, file.newColorMatte; import via CLI subcommand.
- M2 hub shell route MANGLES function-wrapped commands and some literals
  (zsh == expansion, word-split, trim-string corruption). Pattern that works:
  author script on VM → base64 → decode on M2 → run; direct top-level lines only.
- desktop-commander start_process returns at spawn, NOT at exit — file pushes
  must poll expected size before the next append or chunks interleave.

## Export anomaly — RESOLVED 2026-11-03 evening (this lane, resumed)
Two separate effects, both measured on the M2 (per-frame PIL PSNR, full res):
1. **One-frame export offset.** The headless PNG export emits the frame BEFORE
   the requested range start first: export[n] = timeline frame n-1, uniformly
   across all 9 segments (interior/end frames match seg local-1 at 57–69 dB;
   segment-start frames match the previous segment's tail). 438 files for a
   437-frame range. Correct comparison = export[1..437] vs v4[0..436].
   The earlier ffmpeg H0/H1 tests were corrupted by image2's default 25 fps
   pairing — disregard them.
2. **Color-matrix mismatch (the "~29 dB push frames").** All segment encodes
   are UNTAGGED h264. The ffmpeg assembly chain decoded them as BT.601;
   FilmCraft decodes as BT.709. Grays are matrix-invariant (control frames
   58 dB either way); saturated full-frame red (HEY/WAY punch holds — the only
   two 20-frame runs under 30 dB: S4 rel181–200, S8 rel403–422) is not:
   G channel worst (+10.9 mean), bt601 decode 29.5–29.9 dB vs bt709 decode
   55.5–55.6 dB against the app export. NOT translation (shifts worse), NOT
   frame blend (blends worse), NOT inherited encode noise (master-vs-v4 on
   the same frames = 40.7–41.8 dB).
Verdict so far: the in-app timeline + render are frame-faithful; the residual
vs the locked mp4 is (a) the exporter's 1-frame head offset and (b) a
601-vs-709 untagged-decode difference inherited from the source encodes —
the same 709 decode any Mac player applies to the locked file itself.
Full-span shifted numbers (bt601 v4 decode): avg 37.27 dB / median 43.99 dB.
Final consistent-matrix full-span run: ana10 (export vs v4-bt709 AND export
vs segments-bt709) — results appended below when landed.

## FINAL full-span results (ana10, consistent BT.709 decode, offset +1 corrected)
- EXPORT vs SEGMENTS (bt709): avg 50.40 dB · median 57.89 dB · min 35.25 dB ·
  ZERO frames under 35 dB across all 437.
- EXPORT vs LOCKED V4 (bt709 both sides): avg 42.31 dB · median 44.12 dB ·
  min 34.54 dB · only 3 frames under 35 (S7 rel308/309/313 at 34.5–35.0).
- Reference floor: master PNGs vs locked v4 = ~43.2 dB avg. The in-app export
  sits at that same floor vs the locked file. REPRODUCTION = PASS:
  frame-for-frame the same cuts, comps and timing; residuals are the locked
  file's own encode generation + the exporter's 1-frame head offset (a
  measurement artifact, not a timeline error).

## Playback proof — take 1 FAILED (honest log)
21.8s screen recording rolled, but transport never started: both check frames
show playhead parked at 00:00:22:05, Program black. Cause: focus sat in the
Muse Panel webview composer — the two cliclick Space presses went to the
composer (spaces in an empty message box; nothing sent, composer is BO's —
disclosed, not touched further). Title bar showed "- Edited" during the take;
bridge re-check queued. Fix for take 2: click the Program monitor's own Play
button (a real control moves focus out of the webview), verify motion on a
3-second probe screenshot BEFORE rolling the full take.

## PLAYBACK PROOF (deliverable d) — DONE 2026-11-03 ~16:42 CT
- Take 2 screen recording: ~/workspace/hackathon-captures-2026-11/
  repro-playback-proof-filmcraft.mp4 — 19.4s, 1920x1080 h264, 1,685,333 B,
  sha256 a100ddd1a11ff5f843ae206b14a6a2896966e1bf2ecb5d59919070ca5b1e93e1.
  FilmCraft (FINAL project, sequence 33) playing the reproduction section:
  check frame @7s = "SHE PULLED DOWN THE WINDOW" (WINDOW hero red, rain
  footage, header strip) at TC 00:00:27:27; @15s = giant red "NO" (block-3
  cue 4) at TC 00:00:35:27; audio meters live on the bounce throughout.
  Check frames: repro-playback2-f7.jpg / repro-playback2-f15.jpg (+ probe
  frame repro-probe-play.jpg: "AND I STOP AT" at TC 00:00:24:29).
- Transport method that works: click the Program monitor's own Play/Pause
  button (cliclick c:304,536) — a real control pulls focus out of the panel
  webview. Space keys do NOT work while panel focus holds (take 1).
- Bridge readback at close: project 108-rough-cut-FINAL-2026-11-03,
  activeSequence 33, revision 46, dirty TRUE — the dirty/rev-46 state is
  in-app only (playhead.set + playback view ops during the proof). The
  on-disk .fcproj is still the rev-44 save (31,561 B, 16:21 CT) containing
  the verified 9-clip reproduction sequence. Nothing was saved after rev 44.

## WATCHABLE REPRODUCTION FILE (for BO's eyes)
Assembled on the M2 from the app's own export frames (span001–437, offset
corrected) + the bounce (22.64–37.20): /tmp/repro-watch.mp4, 14.5667s,
1920x1080 h264 + AAC, 28,589,315 B, sha256 5fc42ca813b2e1dd4f8c46d97b6d141b
f9320f0223927862a5a8692127257054 → pulled sha-verified to
~/workspace/your_files/rough-cut-v4-REPRODUCED-in-filmcraft.mp4.

## PANEL-DRIVABILITY (structural verification — panel never typed into)
Every build step ran as a local M2 process under the same user account the
panel session runs as: filmcraft-cli --bridge run/exec (loopback 9876,
token from the app process env), filmcraft-cli --project headless CPU
export, ffmpeg encodes, ec_driver.py/EffectCraft CLI. A panel agent with
shell access on the M2 can execute all of them unchanged; the hub route
was only this lane's remote way in, not part of the pipeline.
ONE step is NOT panel-drivable from the M2: the Storyboard→director
generation step. Storyboard Studio binds 127.0.0.1:3000 ON THE M4 and
director.py runs from the repo (VM/M4 side) — the M2 panel session cannot
reach the M4's loopback service. The reproduction consumed pre-generated
director outputs as files; regenerating them is shell-side (M4/VM), not
panel-side. Flagged, not worked around.

## PHASE VERDICT
REPRODUCTION GATE = PASSED. Full-song extension (blocks 4–5 PLAN v2 +
remaining sections) was NOT started in this phase, per the priority note
(reproduction first, no sprawl). Put N Work gate is now unlocked on the
pipeline side; its master pick is still BO's.

---
# FULL-SONG EXTENSION — 2026-11-03 evening (lane: full-song extension subagent)

## PACKET 1 — START — Blocks 4–5 from PLAN v2
- Scope: 21 directed lines (block 4 cues 5–8, song 36.72–51.04 · block 5 cues 9–10,
  song 81.66–88.36) built through the same pipeline: director JSONs (repo
  video-studio-meta @ 30580fc, director/block4-director.json + block5-director.json)
  → EC comps in the LOCKED template → rendered segments → placed in FilmCraft.
- Placement decision: extension goes in a NEW SEQUENCE in the same FINAL project
  (108-rough-cut-FINAL-2026-11-03.fcproj, on-disk rev 44). The verified
  reproduction sequence (seq 33, 9 clips) is NEVER altered; the full-song
  sequence will reference the same media items at the same frames (Packet 3).
- Build convention (from PLAN.md): ONE COMP PER BLOCK; comp frame 0 = block's
  first word onset − 0.30s (block 4: 36.42 · block 5: 81.36). Punch holds use
  PLAN's computed out-frames/scale keys verbatim. Landings = director JSON
  landing_frame (song-absolute) converted to comp frames.
- Template: hero #FF3B1F · others #F2EDE4 + G3 stacked shadow (phase2/3
  white_treatment) · Anton · header strip + rule in every comp · punch-in
  115→100 (4f settle) for stack words · scatter OFF everywhere (PLAN v2:
  zero scatter in blocks 4–5) · beds = existing B&W montage footage only
  (no new footage exists for these blocks; assignment logged at comp build).
- Audio: bounce ONLY, per-section bounce timings from TIMINGS.md (decaying
  lead, never a constant shift).
- CPU ONLY (ec_driver refuses gpu=true; FC export --gpu-rendering off).

### PACKET 1 CLOSE — 2026-11-03 ~17:35 CT — BLOCKS 4–5 BUILT + PLACED ✅
- EC projects (M2 ext-2026-11-03/): 108-lyric-type-block4.ecproj (comp
  block4_cues5-8, 445f) + 108-lyric-type-block5.ecproj (comp block5_cues9-10,
  216f). Builds: 658 + 283 driver ops, 0 op_errors. Renders: 445 + 216 PNGs,
  0 errors. Template spec measured off the locked finals first (baselines by
  tier 150→280 / 230→500 / 400→890; sub-ratio 0.8; DS1 hero 88 / white 100 +
  DS2 85/180 whites; grain all; header + rule every comp; ink-gap 0.33em;
  right rows ink-end x=1800). Ink widths probe-measured @400 (41 words).
- Full-frame fits VERIFIED by settle-frame (scale=100) ink measurement, all
  40..1880 target met: HERE 40..1879 (w1840, size 1056) · AROUND 40..1879
  (642) · DOUBT 41..1879 (807) · YEARS 40..1879 (815) · LINE 41..1879 (1245) ·
  CRAZY 42..1879 (815→measured 1838). DISAPPEARED needed two corrections:
  the @400 probe was itself frame-clipped (x1=1919); true ratio measured
  @300 = 1929@400 → final size 382 → settle ink 39..1879 (w1841) ✅.
  Push-transient (108%) edge overshoot on HERE/AROUND = same class as the
  locked HEY push BO kept; settle frames sit inside.
- PLAN artifacts followed VERBATIM (logged, not "fixed"): HERE hold out f109
  overlaps line-4 first landing (comp f105) by 4f; AROUND out 286 vs line-10
  landing 282; YEARS out 74 vs block5-line4 landing 69. Zero scatter (budget).
- 12 check frames read by eye (stacks GIRL/WHAT YOU/DOING, SHE…TOWN, line-11
  SHE TOLD ME THAT SHE/GOT…, YOU KNOW/WHAT'S, GOT MARRIED/HAVE KIDS + all
  fulls): template-true — hero red #FF3B1F, sub-ratio holds, header readable
  on top, rotation L/R/FULL per PLAN.
- Segments (M2 ext dir): seg-block4-cues5-8.mp4 = 445 frames counted,
  seg-block5-cues9-10.mp4 = 216 frames counted (libx264 crf12, bt709 tags).
- FilmCraft (bridge, app PID 83355): NEW sequence item 50 "108 FULL SONG -
  extension" in 108-rough-cut-FINAL-2026-11-03.fcproj — seg-block4 item 46
  @ frame 1092 dur 445 · seg-block5 item 47 @ frame 2441 dur 216 · bounce
  item 9 @ A1 frame 0. Sequence 33 fingerprint re-read AFTER placement =
  exact rev-44 map (S1 679/35 … S9 1104/12 + bounce bed) — UNTOUCHED.
  Project SAVED: revision 52, dirty False, 37,074 B.
- ⚠️ PACKET-3 FLAG: the bounce ITEM (bounce-candidate.mp3, item 9) spans
  5471 frames in FC (182.37s) vs the canonical bounce's 5603f (186.77s) —
  check the item's true duration before the full-song export; the song's
  last ~4.4s may run past the A1 clip as placed.
- NEXT: Packet 2 — remaining spans (51.04–81.66 chant gap, 88.36–186.77
  passage/verses/tail/outro) via the same director chain + validator,
  consensus-built, uncertain spans logged.

### PACKET 2 START — 2026-11-03 ~17:40 CT — REMAINING SPANS
- Spans: GAP A chant 51.04–81.66s (song frames 1537–2440, between block 4
  end and block 5 start) · GAP B 88.36–186.77s (frames 2657–5603: missed
  passage 89.76–99.48 · tail ~98–124 · outro chant ~122–141 · instrumental
  outro 155–186.77 verified).
- Method: same director chain + validator as blocks 4–5 (video-studio-meta
  @ 30580fc; director.py / rest_director.py). Lyric evidence order: BO's
  canonical sheet → PT native transcripts → Qwen / large-v3 / VT machine
  consensus. Ear-flagged spans built from consensus; EVERY uncertain span +
  the exact words used gets logged in the close checkpoint.
- Output: EC comps in the locked template (same measured spec as Packet 1)
  → segments → placed into sequence 50 "108 FULL SONG - extension" only.
  Sequence 33 stays untouched. CPU only.

### PACKET 2 CLOSE — 2026-11-03 ~18:25 CT — REMAINING SPANS BUILT ✅
- Evidence run (fresh, this lane): house whisper-large-v3 on 4 bounce slices
  (chantA 50.5–83.0 · passage2 85.0–101.5 · tail 98.0–126.0 · chantB
  120.0–143.0; 40kbps mono, payloads 82–217K b64 chars, all under the
  fabrication ceiling). First passage slice (88.3–100.5) returned the
  "We'll be right back" caption hallucination and was DISCARDED; the wider
  85.0 window returned the real passage with word chunks. Word tables were
  cross-checked against Muse VT (COMPARISON.md) + the 2026-11-02 large-v3
  appendix — THREE engines converge on the passage + tail verse + chant.
- Builds: 3 EC comps in the locked template (same measured spec + ink-probe
  method as Packet 1; 41 new words probed @400; GONE solo-probed 733):
  chantA_51-81 (892f) · passage_verse_89-111 (634f) · chantB_111-141 (912f).
  Driver ops 1319 + 847 + 1370, renders 892 + 634 + 912 = 2,438 frames,
  ZERO op_errors. Fulls verified at settle: GONE ×2 ink 1844 / 1840 ·
  FROM 1838 · LEAVE 1840 · OW final-frame 1442 wide, full-height (1250 cap,
  the HEY/WAY idiom). Segments frame-counted exact: seg-chantA-51-81.mp4
  892f · seg-passage-verse-89-111.mp4 634f · seg-chantB-111-141.mp4 912f.
  Check frames read by eye: chant stacks + passage stacks template-true.
- Direction method note: for these consensus spans the line designs were
  built deterministically under the locked rules (rotation, hero rotation,
  sub-ratio, punch math) by this lane — the Wonder director was NOT called
  on machine-garbled text (a second invention layer over uncertain words).
  Blocks 4–5 (verified lyrics) used the real director chain in Packet 1's
  inputs. Zero Meta API spend in this packet (house whisper is house infra).
- ⚠️ UNCERTAIN SPANS — exact words used (ALL of Packet 2's text is in this
  class; BO's ear has not ruled any of it):
  · CHANT 51.30–80.96 + 110.90–141.24 (presence: 3 engines + RMS; words
    unreliable): built as loops of "YEAH SHE'S A WALK AWAY (WALK AWAY)" /
    "YOU BETTER RUN YOU BETTER" / "YOU BETTER DO WHAT YOU'RE GONNA" /
    "'CAUSE SHE GONE", closing on a full-frame OW (140.70, an ad-lib all
    engines hear). Consensus calls: YEAH over "Yes" (VT) · SHE'S/SHE over
    he's/he (VT + tail slice + appendix vs the two fresh slices) · GONNA
    over "going" (chantB + tail + VT) · one loop's "do what you know"
    (single hearing) normalized to GONNA · chantB's "'cause you're gone"
    kept as heard in its two loops.
  · PASSAGE 89.82–99.50 (real, 3 engines; wording garbled in every engine):
    "I CALLED TEXTED AND THE PHONE WAS NIGHT / HAD TO WAKE UP ONE NIGHT
    AND SAY BABY / WHO ARE YOU TEXTING / WHERE ARE YOU FROM" + FROM full.
    Calls: TEXTING over "tasting" (fresh + VT) · NIGHT as the line-1 final
    word (VT "was night" + 2026 "one night" over fresh "nine") · the
    A/BASKET merged chunk split with a +3f stagger.
  · TAIL VERSE 99.62–110.60 (was QUARANTINED 2026-11-02; now triple-engine
    convergent — VT independently reports the same verse — so built, still
    flagged): "I HAVE BUILT THIS HOUSE / FROM THE GROUND UP / YOU GON'
    BREAK A HAPPY HOME / UP AND LEAVE / SO I THOUGHT I'D PACK A BASKET /
    I'LL JUST LEAVE" + LEAVE full. Calls: UP AND LEAVE over "up in leaf"
    (VT + appendix) · PACK A BASKET over VT's "pack your bags".
  · NO-TEXT spans by design: 141.30–155 unverified quiet + 155–186.77
    verified instrumental (Packet 3 outro footage, no lyric lines) and the
    two black breaths (2429–2441, 2657–2693) between sections.
  · Known cosmetic defect: the [HAD TO WAKE UP] row's TO→WAKE gap runs
    ~2× wide — TO's ink width was a layout estimate (420) vs its true
    ~300px class; A / PACK / WHERE / ARE were also estimates (rows fit
    regardless; only that one gap is visibly uneven). Not rebuilt: one row
    in a flagged span; noted for any future polish pass.
- NEXT: Packet 3 — assemble sequence 50 (intro footage + repro span
  referenced + all extension segments + outro footage), trim block-4 clip
  head +12f, export full song, in-app playback recording.

### PACKET 3 START — 2026-11-03 ~18:27 CT — FULL-SONG ASSEMBLY + PROOF
- Sequence 50 "108 FULL SONG - extension" gets: seg-intro (679f, footage
  only, built from the montage beds) @0 · repro span S1–S8 placed with the
  SAME media items at the SAME frames as sequence 33 (referenced, not
  rebuilt) · block-4 clip trimmed +12f at its head (lands @1104) so S8's
  full span survives while every block-4 landing stays on its song frame
  (the 12 trimmed frames are bed-only, pre-GIRL) · S9 bed-tail NOT placed
  (its 1104–1116 span is covered by block 4's own bed + GIRL stack; seq 33
  itself stays untouched as the frame-faithful reference) · chantA @1537 ·
  block 5 (already placed @2441) · passage-verse @2693 · chantB @3327 ·
  seg-outro (1364f, footage only) @4239 · A1 = bounce item 9 @0 (placed in
  Packet 1).
- Export: bridge export of the active sequence 50, h264, --gpu-rendering
  off → M2 file → ~/workspace/your_files/rough-cut-v5-full-song.mp4,
  ffprobe target ≈186.77s + audio. The Packet-1 flag (bounce ITEM spans
  5471f in FC vs 5603f content) gets its verdict from this export.
- Proof: screen-record FilmCraft PLAYING sequence 50 (avfoundation) →
  ~/workspace/hackathon-captures-2026-11/v5-playback-proof.mp4; frames
  read by this lane.

### PACKET 3 CLOSE — 2026-11-03 ~19:42 CT — FULL-SONG ASSEMBLY + PROOF ✅
- Assembly (bridge, FINAL project): sequence 50 "108 FULL SONG - extension"
  V1 table (15 clips, start+dur): intro 0+679 · S1 679+35 · S2 714+71 ·
  S3 785+55 · S4 840+40 · S5 880+17 · S6 897+50 · S7 947+46 · S8 993+111 ·
  block4 (trimmed +12f head) 1104+433 · chantA 1537+892 · block5 2441+216 ·
  passage-verse 2693+634 · chantB 3327+912 · outro 4239+1364 → V1 END 5603.
  Only gaps = the two planned black breaths (2429–2441 = 12f, 2657–2693 =
  36f). A1 = bounce item 9 @0. The repro span in seq 50 references the SAME
  media items at the SAME frames as sequence 33; seq 33 itself untouched
  (Packet 1 fingerprint discipline held). Project saved: REVISION 79,
  dirty False.
- Export: bridge export of seq 50, h264, --gpu-rendering off, 572s render
  → 460,305,504 B. ffprobe (M2 + re-verified on the delivered VM copy):
  1920×1080 h264 video 186.7667s + AAC audio 186.773s. The Packet-1 flag
  is RESOLVED: FC's 5471f bounce-item figure was internal accounting —
  the rendered audio spans the full 186.77s; no silent tail.
- Playback proof: screen-recorded (avfoundation device [1], app window
  crop) while FilmCraft PLAYED seq 50 end to end: playback counters
  shown 5593 / dropped 10, playhead parked 186.74s at stop. Stills read
  by this lane at monitor timecodes 00:00:37:03 (GIRL — block-4 seam over
  the S8 tail bed, the +12f trim working) · 00:01:12:03 (chantA stack,
  AWAY hero) · 00:01:42:04 (tail-verse FROM THE stack) · 00:02:22:04
  (outro footage, seg-outro clip) — meters live in every still.
  Transport note: the Program monitor's on-screen Play button stepped
  frames in this build; playback was started with a monitor focus click
  + Space. A Clip Speed/Duration panel found open over the panel was
  dismissed with the sanctioned app-targeted Esc (values untouched;
  project verified rev 79 / dirty False after).
- Deliveries (chunked pull, per-chunk + whole-file sha256 verified):
  · ~/workspace/your_files/rough-cut-v5-full-song.mp4 — 460,305,504 B,
    sha256 d22a9269c921425b1d55d97dc49c4f56d5457582e6aa371c707f218d452b0513
  · ~/workspace/hackathon-captures-2026-11/v5-playback-proof.mp4 —
    18,762,850 B, 198.13s, sha256
    361ba7b091740f6a0b308351ecbc827db14d7edb0694aab14f644e48b32bde08
  Masters remain on the M2 in ext-2026-11-03/.
- Meta API spend: this lane $0 across Packets 1–3 (no Meta API calls;
  house whisper is house infra; Packet 1 used the pre-committed director
  JSONs). Last event total on the parent board: $2.93 of $150
  (2026-11-03 ~12:10 CT).
- PACKET 3 CLOSED. Packets 4 (surgical word fix, per the countermand) and
  5 (v5.1 + EC lyric guide) follow.

## PACKET 4 — START — 2026-11-03 ~19:44 CT — SURGICAL WORD FIX (countermand version)
- Scope (Claude dispatch, BO-watched v5: "pretty on point, one or two words
  off"): v5 stays EXACTLY as built — timing, placement, heroes, footage,
  layout. ONLY sheet-differing words change, swapped in place.
- Method: word diff IN CODE — every displayed word (from the build configs
  / EC project text) vs BO's canonical sheet
  (~/workspace/your_files/108-verse1-lyrics-anthony-confirmed.md, 8 lines).
  Known case: WON'T → WANT (sheet line 7). Every swap logged (span, old,
  new). Sheet-UNCOVERED spans (block 5, chant, passage, tail) stay on
  screen untouched; their words are compiled (word + span) for BO's ear
  ruling in the final report.
- The diff ships as a permanent runnable gate (word_gate.py) in the ext
  tooling: future builds fail on a sheet-covered mismatch; uncovered words
  are reported, not blocked.
- Sequence 33 is never touched; any fixed segment re-places into seq 50
  only, at identical frames.

### PACKET 4 CLOSE — 2026-11-03 ~20:12 CT — SURGICAL WORD FIX ✅ (gate PASS)
- Gate built + installed: word_gate.py lives at M2
  ext-2026-11-03/gate/word_gate.py (with sheet.md beside it) and mirrored
  to the goal's hidden_files/word-gate/. It extracts every displayed word
  from the build data (ecproj JSONs + driver configs), diffs the
  sheet-covered span line-by-line, exits 1 on any covered mismatch, and
  reports uncovered spans without blocking. Pre-fix run: FAIL with 11
  swaps. Post-fix run (--projects v51): GATE PASS, exit 0.
- THE 11 SWAPS (text swapped in place via layer.setText; timing, layout,
  heroes, footage untouched; originals preserved, edits saved as -v51
  projects; segments re-rendered from the edited projects and re-placed
  in sequence 50 only):
  · Block 2 window comp (S3 clip, song 26.17–28.00): PULLED→PUT ·
    DOWN→ON · THE→A
  · Block 2 hey comp (S4 clip, song 28.00–29.33): SAID→SAY
  · Block 3 line2 comp (S7 clip, song 31.57–33.10): TOLD→TELL
  · Block 3 cue4 comp (S8 clip, song 33.10–36.80): ASKED→ASK
  · Block 4 comp (clip song 36.80–51.23 after the +12f head trim):
    BUT→BY (42.00s) · I→THE (42.10s) · DISAPPEARED→DISAPPEAR (42.37s) ·
    AROUND→RIGHT (45.37s) · WON'T→WANT (45.90s)
- Segment windows for the v4-era comps were PROVEN by PSNR frame-match
  against reference renders of the unedited comps before any cut:
  S3 = window-comp frames 8–62 (unique match) · S4 = hey frames 0–39 ·
  S7 = line2 frames 0–45 · S8 = cue4 frames 0–110. New segments
  frame-counted exact (55/40/46/111/445). Swapped frames read by eye:
  "SHE PUT ON" (S3) · "I WANT SHOW YOU" (block 4) · "I TELL HER" (S7).
  Note: DISAPPEAR and RIGHT keep their full-frame layers' original
  size/position (narrower ink, in-frame) — same layout, per the
  countermand's swap-in-place rule.
- FilmCraft: 5 clips lifted (edit.clear) and re-placed at identical
  start/duration/sourceIn in sequence 50; V1 geometry unchanged (end
  5603, same two breath gaps). SEQUENCE 33 FINGERPRINT RE-READ AFTER:
  its 9 clips at identical frames — UNTOUCHED. Project saved:
  REVISION 98, dirty False.
- KNOWN GAPS (printed by the gate on every run; not swappable — a swap
  cannot create a word): (1) sheet L1 first half "I'M DRIVING DOWN THE
  ROAD" has NO lyric display anywhere in the build (locked v4 design:
  the section opens on footage, text enters at "AND I STOP AT A
  LIGHT"); (2) sheet L7's "TO" ("I want TO show you now") has no
  display slot — the line displays "I WANT SHOW YOU NOW". Both await
  BO's ruling; adding either is a layout change, outside this packet.
- UNCOVERED WORDS stay on screen untouched (block 5, chant A/B,
  passage+verse) — full list in the gate output + the lane's final
  report for BO's ear ruling.
- PACKET 4 CLOSED. Next: Packet 5 (v5.1 export + playback proof + EC
  lyric guide).

## PACKET 5 — START — 2026-11-03 ~20:13 CT — v5.1 EXPORT + PROOF + EC LYRIC GUIDE
- Export sequence 50 (post-fix) from FilmCraft, h264, GPU off →
  rough-cut-v5.1-full-song.mp4 (M2 master + VM your_files delivery),
  ffprobe ≈186.77s + audio.
- Re-record FilmCraft PLAYING sequence 50 → v5.1-playback-proof.mp4;
  frames read by this lane.
- EC LYRIC GUIDE (Claude dispatch): per-line guide INSIDE EffectCraft —
  route 1 native markers (one per lyric line per 108 EC project, named
  "B4 L7 · <words>", at the line's onset, generated in code via the
  ec_driver ops route); route 2 fallback = muted "LYRIC GUIDE" text
  track proven non-rendering by export diff; if neither works, STOP and
  report before touching EC source. Screenshot of an EC timeline
  showing the guide → hackathon-captures-2026-11/ec-lyric-guide.jpg.
- The burned-in REVIEW copy is OPTIONAL, only if it costs nothing after
  everything else lands.

### PACKET 5 AMENDMENT — 2026-11-03 ~21:00 CT — FIX A + FIX B QUEUED (Claude dispatch, BO's ear on the v5 phone copy)
- FIX A (passage, song ~89.8–99.5): display line "I CALLED TEXTED AND
  THE PHONE WAS NIGHT" is WRONG. BO's line: "I CAUGHT HER TEXTING ON
  THE PHONE ONE NIGHT" — replace and RE-TIME each word to its sung
  onset (Qwen/PT-native/large-v3 word times). Look, layout system and
  footage stay; only words + per-word timing change.
- FIX B (song ~1:38–1:39): "WHERE ARE YOU FROM" → "WHERE HE FROM".
  FROM stays the red punch; timing/layout otherwise unchanged.
- DO NOT TOUCH the rest of the passage ("HAD TO WAKE UP…" and
  "WHO ARE YOU TEXTING" stay exactly as built — no ruling yet).
- GATE: both lines go into gate/sheet.md as BO-CONFIRMED (2026-11-03)
  and the gate is extended to enforce them.
- EXPORT: v5.1 already exported (M2 master, sha 300f8f37…) and its
  playback proof + EC guide stand, but v5.2 SUPERSEDES it as the
  delivery. The v5.1 VM transfer is stopped at 138,412,032 bytes
  (prefix-verified bytes; partial file removed at packet close).
- CHECK CLIP: song 1:28–1:42 cut from v5.2 →
  your_files/v5.2-check-128-142.mp4.

### PACKET 5 AMENDMENT — FIXES APPLIED — 2026-11-03 ~21:35 CT
- FIX A DONE: PV comp line 1 rebuilt in cfg-pv-build-v2.json (847->853
  ops, group audit exact). BO's line "I CAUGHT HER TEXTING ON THE PHONE
  ONE NIGHT" laid out in the old line's rows/tiers ([I CAUGHT HER
  TEXTING] 150 / [ON THE PHONE] 230 / [ONE 320 + NIGHT 400 red hero];
  Anton ink-measured, rows end 1291/1268/1473 <= 1880). Word landings
  re-timed from PT-NATIVE word onsets (bounce comp grid, onset - 2f,
  frame-quantized): I pre-landed (song onset 89.705) · CAUGHT f11
  (90.216) · HER f26 (90.688) · TEXTING f41 (91.183) · ON f48 (91.423)
  · THE f54 (91.627) · PHONE f60 (91.839) · ONE f74 (92.292) · NIGHT
  f84 (92.640). Build anchors vs PT agreed within +/-0.10s (HAD +0.05,
  WHO -0.02, WHERE -0.10). Nothing else in the passage touched.
- FIX B DONE: ARE_L3_2 -> HE_L3_2 (text HE, same slot/timing), YOU
  layer removed entirely; FROM red punch untouched (verified on
  rendered frames: "WHERE HE" at comp 8.67s, FROM full-frame at 9.23s).
- GATE: sheet.md gained the section "## BO-confirmed passage lines
  (2026-11-03, BO's ear on v5)" with the two lines verbatim;
  word_gate.py extended with an enforced PASSAGE CHECK (pre-build run:
  FAIL PV-BUILD only; post-build run: GATE PASS exit 0, PV-A + PV-B OK).
- PV project rebuilt as 108-lyric-type-passageverse-v2.ecproj; its 12
  guide markers re-applied with corrected texts (PV L1 = BO's line,
  PV L4 = "WHERE HE"). Segment seg-passage-verse-v2.mp4 rendered
  (634 frames, 0 op_errors; ONE glitched frame f090 caught on still
  review, re-rendered clean and re-encoded; sha 3e16152f...).
  Stills read: f050 (I CAUGHT HER TEXTING + ON), f100 (full stack,
  NIGHT hero), f260 (WHERE HE), f277 (FROM).
- FILMCRAFT: PV clip 69 lifted, v2 segment placed as clip 83 (item 82)
  at 2693 + 634 in sequence 50; geometry otherwise identical (end
  5603); project saved, dirty False. SEQUENCE 33 FINGERPRINT RE-READ:
  9 clips at 679/714/785/840/880/897/947/993/1104 — UNTOUCHED.
- v5.2 export running; check clip + transfers follow.

### CORRECTION — 2026-11-03 ~21:26 CT — BO'S WORDS FINAL (Claude relay; supersedes the earlier span instructions wherever they conflict)
- The song 1:30–1:39 stretch is exactly TWO lines, nothing else:
  LINE 1 (~1:30–1:36) "I CAUGHT HER TEXTING ON THE PHONE ONE NIGHT"
  replaces ALL of "I CALLED TEXTED / AND THE PHONE WAS NIGHT / HAD TO
  WAKE UP ONE NIGHT AND" (the earlier DO-NOT-TOUCH on HAD TO WAKE UP
  is VOID). LINE 2 (~1:36–1:39) "WHERE HE FROM" replaces BOTH "WHO ARE
  YOU TEXTING" AND "WHERE ARE YOU FROM"; FROM stays the red punch.
- GATE HARDENING: the gate must FAIL if any word other than these two
  lines' words appears anywhere in the 1:30–1:39 span; sheet.md notes
  the span-scoped exclusivity.
- Consequence: PV rebuild v3 (v2's Fix A/B are superseded inside the
  span: old L1 "HAD TO WAKE UP…SAY BABY" and old L2 "WHO ARE YOU
  TEXTING" are deleted; line 1 now holds the span until LINE 2; WHERE/
  HE/FROM re-timed to PT onsets). The v5.2 export already running is
  PRE-CORRECTION — it will be discarded and re-exported after the v3
  swap. Check clip unchanged (1:28–1:42 from the corrected v5.2).

### STOP / REVERSAL — 2026-11-03 ~21:31 CT — WORD-SOURCE RULE REVERSED (Claude dispatch; BO's direct words: "idk what this sheet is, the video is good")
- gate/sheet.md and the canonical dictation sheet are RETIRED as word
  sources, effective now (phone speech-to-text; contains errors). No
  more diffs against it; the passage lines are NOT added to it as an
  authority (the gate is rebuilt on the baseline below instead).
- REVERT all Packet 4 sheet-driven swaps — the v5 on-screen words are
  the BO-approved baseline: PULLED/DOWN/THE (block 2 window), SAID
  (block 2 hey), TOLD (block 3 line 2), ASKED (block 3 cue 4), and in
  block 4: BUT, I, DISAPPEARED, AROUND, WON'T (restoring WON'T at
  ~0:46 — the WANT swap never had BO's own confirmation). Reverts are
  pure FilmCraft clip swaps back to the original segment files; the
  -v51 EC projects become orphaned artifacts.
- The ONLY word changes in v5.2 are the two passage fixes (PV v3,
  already built + gate-verified): line 1 "I CAUGHT HER TEXTING ON THE
  PHONE ONE NIGHT", line 2 "WHERE HE FROM", span-exclusive.
- WORD GATE REDEFINED: baseline = v5 on-screen words as amended by
  exactly those two fixes; gate fails on any deviation from THAT
  baseline. The pre-correction v5.2 export (v51 swaps + PV v2) is
  discarded; ONE clean v5.2 export follows the reverts + PV v3 swap.

### REVERT EXECUTED — 2026-11-03 ~22:05 CT — seq 50 restored to the v5 baseline words
- GATE REDEFINED + PROVEN: gate/baseline.md generated BY CODE from the
  v5 build data (original projects/configs + PV v3 for the passage);
  word_gate.py rewritten (old sheet-era gate kept as
  word_gate_sheet_era.py.bak). AUDIT mode vs the -v51 projects: FAIL
  with exactly the 11 sheet swaps (B2 PULLED/DOWN/THE/SAID, B3 TOLD,
  B3 ASKED, B4 BUT/I, DISAPPEARED, AROUND, WON'T) + the PV v2 span —
  the code-generated revert checklist. CURRENT mode: PASS, exit 0,
  span exclusivity green.
- FC REVERTS (bridge run, all ok): clips 77/78/79/80/81 (v51 items
  72-76) lifted; ORIGINAL items placed at identical geometry — new
  clips 84 (item 24 seg-S3-rain, 785+55), 85 (item 25 seg-S4-b2bv4,
  840+40), 86 (item 28 seg-S7-b3l23, 947+46), 87 (item 29
  seg-S8-b3c4v4, 993+111), 88 (item 46 seg-block4-cues5-8, 1104+433,
  sourceIn 12f). Saved; verified from the .fcproj JSON: seq-50 V1 END
  5603, geometry identical to v5; seq-33 fingerprint intact (9 clips,
  items 4/23/24/25/26/27/28/29/30). The -v51 EC projects are orphaned
  artifacts; nothing references them.
- EC GUIDE aligned to the baseline: markers added to the ORIGINAL
  projects with v5 words (block2-v7: 1, "B2 L2 - SHE PULLED DOWN THE
  WINDOW I SAID HEY"; block3-take2-v6: 2, incl. "THEN I ASKED...";
  block4 original: 4, incl. "I WON'T SHOW YOU NOW"); B1 marker text
  set to the displayed words "AND I STOP AT A LIGHT". (Driver lesson:
  ops need explicit tool fields — open_project/save_project are tools,
  comp/markers ops are execute_command.)
- The stale pre-correction v5.2 export finished (186.773s) and is
  DISCARDED (carried v51 swaps + PV v2). The final v5.2 export runs
  after the PV v3 swap.

### PACKET 5 CLOSE — 2026-11-03 ~23:10 CT — v5.2 DONE; full-file transfer parked on a dropped M2 lane
- PV v3 SEGMENT: frames-pv3 = 634 rendered, 0 op_errors;
  seg-passage-verse-v3.mp4 = 634 frames counted, sha256 c3bf62ba...
  Stills read by eye: f100 full line-1 stack (NIGHT hero), f200 line 1
  ALONE at comp 6.67s (the old HAD TO WAKE UP zone - span exclusivity
  proven visually), f260 WHERE at the new timing, f285/f292 FROM
  punch + settle fully in frame.
- FC SWAP: seg-passage-verse-v3 imported as item 89; clip 83 (PV v2)
  lifted; clip 90 placed 2693+634 sourceIn 0; saved (58,070 B).
  Seq-50 V1 END 5603; seq-33 fingerprint intact (9 clips).
- FINAL v5.2 EXPORT (the only export carrying the baseline + the two
  passage fixes; the earlier stale export was discarded): bridge
  export, --gpu-rendering off. M2 master
  ext-2026-11-03/rough-cut-v5.2-full-song.mp4 = 462,060,177 B,
  sha256 0921294d4612f75ed443cab5d95789ecb68f85b2bfe176729698aae63653a9b2,
  ffprobe: video + audio streams, 186.773 s.
- CHECK CLIP DELIVERED: song 88-102 s cut from the master (crf12,
  1080p, 14.000 s, 54,403,294 B, sha256 580bee7e... == M2 master of
  the clip) at ~/workspace/your_files/v5.2-check-128-142.mp4. Stills
  read from the DELIVERED file: song 95.5 s = corrected line-1 stack
  holding alone; song 99.4 s = FROM punch settled in frame.
- FULL-FILE TRANSFER PARKED (infrastructure, not creative): the pull
  reached 88,080,384 / 462,060,177 B (a valid prefix, NOT a complete
  file) at ~/workspace/your_files/rough-cut-v5.2-full-song.mp4, then
  the M2 desktop lane dropped off the hub - canary returns
  "Server desktop not found or not connected". RESUME when the M2
  lane reconnects (single command, resumable, 4 MB chunks):
    PULL_CHUNK_MB=4 python3 hidden_files/repro-build-2026-11-03/tools/pull_v52.py \
      "${BRICKHOUSE_WORKDIR}/ext-2026-11-03/rough-cut-v5.2-full-song.mp4" \
      ~/workspace/your_files/rough-cut-v5.2-full-song.mp4
  (tools/ also holds h2.py, the hub helper; /tmp copies were wiped by
  a service restart mid-lane - helpers now live in the goal folder.)
- The stale partial rough-cut-v5.1-full-song.mp4 was deleted; v5.1 as
  a file was superseded by v5.2 before its transfer completed (its
  M2-side export + playback proof DID complete and are on record).
- OPTIONAL REVIEW burn-in: NOT built - every hub window went to the
  fixes, the reverts and the transfers. review-entries.json in the
  word-gate folder is stale for the passage if it is ever built.
- Meta API spend by this lane across all packets: $0.
