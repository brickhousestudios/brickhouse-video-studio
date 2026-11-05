# PUT N WORK — DIRECTOR PLAN (for BO's verdict)

Step 2 of the standing order (timing → director plan → BO verdict → footage). NO footage, NO build yet — this is the plan to green-light or mark up. Built 2026-11-04 (America/Chicago) by the house director chain: Muse Wonder (muse-wonder-1.0) designs, `director.py`'s real `validate()` gates, hero color + effects derived in code — same chain that directed 108 blocks 4–5.

**Track:** PUT N WORK (DRIXX) — master **V3** (`PUT N WORK MASTER V3.wav`, 223.968s, sha256 `260e5b69c37b64a208aaebb0b20c770e72ffb3697828418737bba8d470ec79eb`), Brick's pick under BO's 2026-11-04 delegation.
**Words:** BO's lyric sheet ONLY — ASR text was used for timing, never displayed.
**Timing:** house whisper-large-v3 grid on V3 (473 timed words) assembled onto the sheet words by anchor matching. The sheet's own clock is NOT used: measured drift runs **+11.2s at HOOK 1 → −31.9s at FINAL HOOK**. Per-line provenance: **ANCHORED** = direct grid anchors · **INTERPOLATED** = filled between anchors in the same section · **ESTIMATED** = the grid's dead/degraded zone, word-rate spread (flagged again at the bottom).
**Cadence:** every display line lands **2 frames before** its first word's onset (30fps) and holds until the next line lands — the lyric-type rule. In/out below are the LANDINGS.
**Effects budget:** PUT N WORK has **no redlight-motif line** (no line brakes or stops; the cops line runs FROM them) — so no scatter/break-apart anywhere in this song; heroes land plain. The wrapper validator rejected any motif claim outright.
**Hero discipline:** one hero per line, never repeated inside a block; hooks 1/2/final are separate blocks, so a hero may return in a later hook. Hero = red **#FF3B1F**, all other words off-white **#F2EDE4**, derived in code from the model's hero pick.
**Rotation:** placement never repeats back-to-back; at most 2 stack lines in a row before a full-frame line (validator-enforced).

## pnw-hook1 — HOOK1 (11 sheet lines → 30 display lines)

Timing source: house whisper-large-v3 timing grid on the V3 master (song_grid.json, 473 timed words; 90s head slice + 45s re-sliced tail); words are BO's lyric sheet ONLY -- ASR text was used for timing, never displayed; per-word timing provenance (ANCHORED / INTERPOLATED / ESTIMATED) is recorded line-by-line in PNW-PLAN.md. Sheet absolute times were NOT used: measured drift vs V3 runs +11.2s at HOOK 1 to -31.9s at FINAL HOOK.
Model: muse-wonder-1.0 · generated 2026-11-04T12:08:15-06:00 · receipts: resp_6aeb748fc0772febad944b6f · Wonder spend this section: $0.4284 (1 call(s))

| Line | In | Out | Display | Placement | Hero | Effects | Timing |
|---|---|---|---|---|---|---|---|
| pnw-hook1-line1 | 10.95 | 11.85 | NIGGA WHERE I'M FROM | left | FROM | — | ESTIMATED (sheet L1) |
| pnw-hook1-line2 | 11.85 | 12.59 | YOU CAN'T GET NO | right | CAN'T | — | ANCHORED (sheet L1) |
| pnw-hook1-line3 | 12.59 | 12.95 | SLEEP | full | SLEEP | — | ANCHORED (sheet L1) |
| pnw-hook1-line4 | 12.95 | 13.61 | YOU CANNOT | left | CANNOT | — | ANCHORED (sheet L2) |
| pnw-hook1-line5 | 13.61 | 14.05 | GET NO | right | NO | — | ANCHORED (sheet L2) |
| pnw-hook1-line6 | 14.05 | 14.45 | PEACE | full | PEACE | — | ANCHORED (sheet L2) |
| pnw-hook1-line7 | 14.45 | 15.39 | NIGGA WHERE I'M FROM | left | WHERE | — | ANCHORED (sheet L3) |
| pnw-hook1-line8 | 15.39 | 16.99 | THE BAY WE DO NOT FUCKING | right | FUCKING | — | ANCHORED (sheet L3) |
| pnw-hook1-line9 | 16.99 | 17.31 | WEEP | full | WEEP | — | ANCHORED (sheet L3) |
| pnw-hook1-line10 | 17.31 | 17.91 | ALL WE KNOW | left | KNOW | — | ANCHORED (sheet L4) |
| pnw-hook1-line11 | 17.91 | 19.51 | IS CRACK CARS WE HAD NO | right | CARS | — | ANCHORED (sheet L4) |
| pnw-hook1-line12 | 19.51 | 20.27 | OG | full | OG | — | ANCHORED (sheet L4) |
| pnw-hook1-line13 | 20.27 | 21.41 | I WENT OUTSIDE WITH THE | left | OUTSIDE | — | ANCHORED (sheet L5) |
| pnw-hook1-line14 | 21.41 | 22.81 | BARS HIT A CAR FOR NO | right | BARS | — | ANCHORED (sheet L5) |
| pnw-hook1-line15 | 22.81 | 23.19 | REASON | full | REASON | — | ANCHORED (sheet L5) |
| pnw-hook1-line16 | 23.19 | 24.02 | WE SMOOTH WITH IT | left | SMOOTH | — | ANCHORED (sheet L6) |
| pnw-hook1-line17 | 24.02 | 25.41 | TRUE WITH IT CREEPIN' THROUGH THE | right | CREEPIN' | — | INTERPOLATED (sheet L6/7) |
| pnw-hook1-line18 | 25.41 | 25.77 | NIGHT | full | NIGHT | — | ANCHORED (sheet L7) |
| pnw-hook1-line19 | 25.77 | 26.75 | THEM NIGGAS ROUND ME | left | NIGGAS | — | ANCHORED (sheet L7) |
| pnw-hook1-line20 | 26.75 | 28.23 | I'M BLOWIN' I BUST MY OWN | right | BLOWIN' | — | ANCHORED (sheet L8) |
| pnw-hook1-line21 | 28.23 | 28.71 | PIPE | full | PIPE | — | ANCHORED (sheet L8) |
| pnw-hook1-line22 | 28.71 | 29.65 | GOT THE MONEY | left | MONEY | — | ANCHORED (sheet L9) |
| pnw-hook1-line23 | 29.65 | 31.05 | THE POWER BITCH IS | right | POWER | — | ANCHORED (sheet L9) |
| pnw-hook1-line24 | 31.05 | 31.37 | ALRIGHT | full | ALRIGHT | — | ANCHORED (sheet L9) |
| pnw-hook1-line25 | 31.37 | 32.37 | BITCH WE PUT IN | left | PUT | — | INTERPOLATED (sheet L10) |
| pnw-hook1-line26 | 32.37 | 33.45 | WORK BITCH WE PUT IN | right | BITCH | — | INTERPOLATED (sheet L10) |
| pnw-hook1-line27 | 33.45 | 33.65 | WORK | full | WORK | — | ANCHORED (sheet L10) |
| pnw-hook1-line28 | 33.65 | 34.25 | WE GRINDING | left | GRINDING | — | INTERPOLATED (sheet L11) |
| pnw-hook1-line29 | 34.25 | 34.74 | HARD AHH | right | HARD | — | INTERPOLATED (sheet L11) |
| pnw-hook1-line30 | 34.74 | 35.19 | YEAH | full | YEAH | — | INTERPOLATED (sheet L11) |

Director's rationale:
- pnw-hook1-line1: The hook opens left and builds to FROM to set the place.
- pnw-hook1-line2: The line shifts right and builds to CAN'T before the lack of sleep.
- pnw-hook1-line3: SLEEP fills the frame as the first payoff.
- pnw-hook1-line4: The next denial returns left and lands on CANNOT.
- pnw-hook1-line5: The line shifts right and builds to NO.
- pnw-hook1-line6: PEACE fills the frame as the second payoff.
- pnw-hook1-line7: The place line returns left and builds to WHERE.
- pnw-hook1-line8: The line shifts right and builds to FUCKING.
- pnw-hook1-line9: WEEP fills the frame to close the bay line.
- pnw-hook1-line10: The knowledge line opens left and lands on KNOW.
- pnw-hook1-line11: The line shifts right and builds to CARS.
- pnw-hook1-line12: OG fills the frame to close the line.
- pnw-hook1-line13: The outside line opens left and builds to OUTSIDE.
- pnw-hook1-line14: The right stack centers on BARS and the hit that follows.
- pnw-hook1-line15: REASON fills the frame to close the run.
- pnw-hook1-line16: The smooth line opens left and builds to SMOOTH.
- pnw-hook1-line17: The line shifts right and builds to CREEPIN' heading into night.
- pnw-hook1-line18: NIGHT fills the frame as the setting lands.
- pnw-hook1-line19: The group line opens left and builds to NIGGAS.
- pnw-hook1-line20: The line shifts right and builds to BLOWIN'.
- pnw-hook1-line21: PIPE fills the frame to close the line.
- pnw-hook1-line22: The money line opens left and lands on MONEY.
- pnw-hook1-line23: The line shifts right and builds to POWER.
- pnw-hook1-line24: ALRIGHT fills the frame as the payoff.
- pnw-hook1-line25: The work chant opens left and builds to PUT.
- pnw-hook1-line26: The chant shifts right and builds to BITCH before the work punch.
- pnw-hook1-line27: WORK fills the frame as the chant payoff.
- pnw-hook1-line28: The closing line opens left and lands on GRINDING.
- pnw-hook1-line29: The line shifts right and lands on HARD.
- pnw-hook1-line30: YEAH fills the frame to close the hook.

## pnw-verse1 — VERSE1 (8 sheet lines → 24 display lines)

Timing source: house whisper-large-v3 timing grid on the V3 master (song_grid.json, 473 timed words; 90s head slice + 45s re-sliced tail); words are BO's lyric sheet ONLY -- ASR text was used for timing, never displayed; per-word timing provenance (ANCHORED / INTERPOLATED / ESTIMATED) is recorded line-by-line in PNW-PLAN.md. Sheet absolute times were NOT used: measured drift vs V3 runs +11.2s at HOOK 1 to -31.9s at FINAL HOOK.
Model: muse-wonder-1.0 · generated 2026-11-04T12:10:12-06:00 · receipts: resp_6aeb7503c8a278068a4c4bbc · Wonder spend this section: $0.3697 (1 call(s))

| Line | In | Out | Display | Placement | Hero | Effects | Timing |
|---|---|---|---|---|---|---|---|
| pnw-verse1-line1 | 35.19 | 36.29 | YOU KNOW I'M GOING HARD | left | HARD | — | ANCHORED (sheet L1) |
| pnw-verse1-line2 | 36.29 | 37.67 | I'M WORKING TILL THE SUN COME | right | WORKING | — | ANCHORED (sheet L1) |
| pnw-verse1-line3 | 37.67 | 38.41 | UP | full | UP | — | ANCHORED (sheet L1) |
| pnw-verse1-line4 | 38.41 | 39.55 | JUST TRYNA GET TO THE RACKS | left | RACKS | — | INTERPOLATED (sheet L2) |
| pnw-verse1-line5 | 39.55 | 40.24 | BUT THIS SHIT THAT AIN'T | right | SHIT | — | INTERPOLATED (sheet L2) |
| pnw-verse1-line6 | 40.24 | 40.28 | ENOUGH | full | ENOUGH | — | INTERPOLATED (sheet L2) |
| pnw-verse1-line7 | 40.28 | 41.65 | AINT ENOUGH AND THEY SAY | left | AINT | — | INTERPOLATED (sheet L2/3) |
| pnw-verse1-line8 | 41.65 | 42.85 | HARD TIME MAKES YOU | right | TIME | — | ANCHORED (sheet L3) |
| pnw-verse1-line9 | 42.85 | 43.87 | TOUGH | full | TOUGH | — | ANCHORED (sheet L3) |
| pnw-verse1-line10 | 43.87 | 45.49 | I'M OUT HERE LOOKING FOR SOME REAL | left | REAL | — | ANCHORED (sheet L4) |
| pnw-verse1-line11 | 45.49 | 46.45 | BUT I AINT FINDING NO | right | FINDING | — | ANCHORED (sheet L4) |
| pnw-verse1-line12 | 46.45 | 46.93 | LOVE | full | LOVE | — | ANCHORED (sheet L4) |
| pnw-verse1-line13 | 46.93 | 48.83 | READY TO KILL I GOT MY | left | KILL | — | ANCHORED (sheet L5) |
| pnw-verse1-line14 | 48.83 | 49.41 | HAND ON THE | right | HAND | — | ANCHORED (sheet L5) |
| pnw-verse1-line15 | 49.41 | 49.93 | GUN | full | GUN | — | ANCHORED (sheet L5) |
| pnw-verse1-line16 | 49.93 | 51.06 | I AIN'T EVEN GON' SAY | left | SAY | — | ANCHORED (sheet L6) |
| pnw-verse1-line17 | 51.06 | 51.67 | NOTHING IT'S MURDER | right | MURDER | — | INTERPOLATED (sheet L6) |
| pnw-verse1-line18 | 51.67 | 52.60 | 101 | full | 101 | — | ANCHORED (sheet L6) |
| pnw-verse1-line19 | 52.60 | 54.45 | HUND AROUND THAT DRUM AND WE | left | HUND | — | INTERPOLATED (sheet L7) |
| pnw-verse1-line20 | 54.45 | 56.87 | GON' LET IT DUMP HUND AROUND THAT | right | AROUND | — | INTERPOLATED (sheet L7/8) |
| pnw-verse1-line21 | 56.87 | 57.09 | DRUM | full | DRUM | — | ANCHORED (sheet L8) |
| pnw-verse1-line22 | 57.09 | 57.65 | AND WE GON' | left | GON' | — | ANCHORED (sheet L8) |
| pnw-verse1-line23 | 57.65 | 57.97 | LET IT | right | LET | — | ANCHORED (sheet L8) |
| pnw-verse1-line24 | 57.97 | 58.49 | DUMP | full | DUMP | — | ANCHORED (sheet L8) |

Director's rationale:
- pnw-verse1-line1: The verse opens left and builds to HARD for the work ahead.
- pnw-verse1-line2: The line shifts right and builds to WORKING till sunrise.
- pnw-verse1-line3: UP fills the frame as the sunrise point.
- pnw-verse1-line4: The money aim opens left and lands on RACKS.
- pnw-verse1-line5: The line shifts right and lands on SHIT as the setback.
- pnw-verse1-line6: ENOUGH fills the frame as the shortfall.
- pnw-verse1-line7: The echoed AINT opens left before what they say.
- pnw-verse1-line8: The line shifts right and builds from HARD to TIME.
- pnw-verse1-line9: TOUGH fills the frame as the result of hard time.
- pnw-verse1-line10: The search opens left and lands on REAL.
- pnw-verse1-line11: The line shifts right and builds to FINDING with no result.
- pnw-verse1-line12: LOVE fills the frame as what is missing.
- pnw-verse1-line13: The threat opens left and lands on KILL.
- pnw-verse1-line14: The line shifts right and puts HAND in front.
- pnw-verse1-line15: GUN fills the frame as the object in hand.
- pnw-verse1-line16: The silence line opens left and builds to SAY.
- pnw-verse1-line17: The line shifts right and lands on MURDER before the number.
- pnw-verse1-line18: 101 fills the frame to close the murder line.
- pnw-verse1-line19: The closing run opens left with HUND around the drum.
- pnw-verse1-line20: The line shifts right, carries the first DUMP, and builds the repeat to AROUND.
- pnw-verse1-line21: The repeated DRUM fills the frame before the last steps.
- pnw-verse1-line22: The final pass returns left and builds to GON'.
- pnw-verse1-line23: The line shifts right and puts LET before the release.
- pnw-verse1-line24: DUMP fills the frame to close the verse.

## pnw-bridge — BRIDGE (4 sheet lines → 12 display lines)

Timing source: house whisper-large-v3 timing grid on the V3 master (song_grid.json, 473 timed words; 90s head slice + 45s re-sliced tail); words are BO's lyric sheet ONLY -- ASR text was used for timing, never displayed; per-word timing provenance (ANCHORED / INTERPOLATED / ESTIMATED) is recorded line-by-line in PNW-PLAN.md. Sheet absolute times were NOT used: measured drift vs V3 runs +11.2s at HOOK 1 to -31.9s at FINAL HOOK.
Model: muse-wonder-1.0 · generated 2026-11-04T12:10:31-06:00 · receipts: resp_6aeb7516fdb0196f33f3450f · Wonder spend this section: $0.1058 (1 call(s))

| Line | In | Out | Display | Placement | Hero | Effects | Timing |
|---|---|---|---|---|---|---|---|
| pnw-bridge-line1 | 58.49 | 59.65 | I'M IN THE LAB BITCH | left | LAB | — | ANCHORED (sheet L1) |
| pnw-bridge-line2 | 59.65 | 60.91 | I'M TRYNA MAKE A WAY WITH | right | WAY | — | INTERPOLATED (sheet L1) |
| pnw-bridge-line3 | 60.91 | 61.47 | RAP | full | RAP | — | INTERPOLATED (sheet L1) |
| pnw-bridge-line4 | 61.47 | 62.29 | I SPEND THAT BREAD | left | BREAD | — | ANCHORED (sheet L2) |
| pnw-bridge-line5 | 62.29 | 63.17 | NOW I'M GON' MAKE IT | right | MAKE | — | INTERPOLATED (sheet L2) |
| pnw-bridge-line6 | 63.17 | 63.89 | BACK | full | BACK | — | ANCHORED (sheet L2) |
| pnw-bridge-line7 | 63.89 | 65.35 | KEEP IT REAL | left | REAL | — | ANCHORED (sheet L3) |
| pnw-bridge-line8 | 65.35 | 66.03 | AIN'T NO FAKING | right | FAKING | — | ANCHORED (sheet L3) |
| pnw-bridge-line9 | 66.03 | 66.55 | THAT | full | THAT | — | ANCHORED (sheet L3) |
| pnw-bridge-line10 | 66.55 | 67.36 | PLAY ONE OF MINE | left | MINE | — | ANCHORED (sheet L4) |
| pnw-bridge-line11 | 67.36 | 68.27 | AND YOU GON' TAKE A | right | TAKE | — | INTERPOLATED (sheet L4) |
| pnw-bridge-line12 | 68.27 | 69.37 | NAP | full | NAP | — | ANCHORED (sheet L4) |

Director's rationale:
- pnw-bridge-line1: The bridge opens left and lands on LAB as the workplace.
- pnw-bridge-line2: The line shifts right and builds to WAY as the path sought.
- pnw-bridge-line3: RAP fills the frame as the means to make a way.
- pnw-bridge-line4: The spending line returns left and lands on BREAD.
- pnw-bridge-line5: The line shifts right and builds to MAKE before the return.
- pnw-bridge-line6: BACK fills the frame as the money returning.
- pnw-bridge-line7: The honesty line opens left and lands on REAL.
- pnw-bridge-line8: The line shifts right and lands on FAKING as what is denied.
- pnw-bridge-line9: THAT fills the frame to close the honesty point.
- pnw-bridge-line10: The final line opens left and lands on MINE as the song played.
- pnw-bridge-line11: The line shifts right and builds to TAKE before the rest.
- pnw-bridge-line12: NAP fills the frame to close the bridge.

## pnw-hook2 — HOOK2 (11 sheet lines → 27 display lines)

Timing source: house whisper-large-v3 timing grid on the V3 master (song_grid.json, 473 timed words; 90s head slice + 45s re-sliced tail); words are BO's lyric sheet ONLY -- ASR text was used for timing, never displayed; per-word timing provenance (ANCHORED / INTERPOLATED / ESTIMATED) is recorded line-by-line in PNW-PLAN.md. Sheet absolute times were NOT used: measured drift vs V3 runs +11.2s at HOOK 1 to -31.9s at FINAL HOOK.
Model: muse-wonder-1.0 · generated 2026-11-04T12:13:53-06:00 · receipts: resp_6aeb75e18a328343c2b341d5 · Wonder spend this section: $0.5749 (1 call(s))

| Line | In | Out | Display | Placement | Hero | Effects | Timing |
|---|---|---|---|---|---|---|---|
| pnw-hook2-line1 | 69.37 | 70.39 | NIGGA WHERE I'M FROM | left | FROM | — | ANCHORED (sheet L1) |
| pnw-hook2-line2 | 70.39 | 71.13 | YOU CAN'T GET NO | right | GET | — | ANCHORED (sheet L1) |
| pnw-hook2-line3 | 71.13 | 71.63 | SLEEP | full | SLEEP | — | ANCHORED (sheet L1) |
| pnw-hook2-line4 | 71.63 | 72.13 | YOU CANNOT | left | CANNOT | — | ANCHORED (sheet L2) |
| pnw-hook2-line5 | 72.13 | 72.59 | GET NO | right | NO | — | ANCHORED (sheet L2) |
| pnw-hook2-line6 | 72.59 | 73.05 | PEACE | full | PEACE | — | ANCHORED (sheet L2) |
| pnw-hook2-line7 | 73.05 | 74.61 | NIGGA WHERE I'M FROM THE BAY | left | BAY | — | ANCHORED (sheet L3) |
| pnw-hook2-line8 | 74.61 | 75.41 | WE DO NOT FUCKING | right | FUCKING | — | ANCHORED (sheet L3) |
| pnw-hook2-line9 | 75.41 | 75.89 | WEEP | full | WEEP | — | ANCHORED (sheet L3) |
| pnw-hook2-line10 | 75.89 | 76.61 | ALL WE KNOW IS | left | KNOW | — | ANCHORED (sheet L4) |
| pnw-hook2-line11 | 76.61 | 78.05 | CRACK CARS WE HAD NO | right | CARS | — | ANCHORED (sheet L4) |
| pnw-hook2-line12 | 78.05 | 78.91 | OG | full | OG | — | ANCHORED (sheet L4) |
| pnw-hook2-line13 | 78.91 | 79.95 | I WENT OUTSIDE WITH THE | left | OUTSIDE | — | ANCHORED (sheet L5) |
| pnw-hook2-line14 | 79.95 | 81.35 | BARS HIT A CAR FOR NO | right | CAR | — | ANCHORED (sheet L5) |
| pnw-hook2-line15 | 81.35 | 81.75 | REASON | full | REASON | — | ANCHORED (sheet L5) |
| pnw-hook2-line16 | 81.75 | 82.79 | WE SMOOTH WITH IT | left | SMOOTH | — | ESTIMATED (sheet L6) |
| pnw-hook2-line17 | 82.79 | 84.34 | TRUE WITH IT CREEPIN' THROUGH THE | right | CREEPIN' | — | ESTIMATED (sheet L6/7) |
| pnw-hook2-line18 | 84.34 | 84.60 | NIGHT | full | NIGHT | — | ESTIMATED (sheet L7) |
| pnw-hook2-line19 | 84.60 | 85.64 | THEM NIGGAS ROUND ME | left | NIGGAS | — | ESTIMATED (sheet L7) |
| pnw-hook2-line20 | 85.64 | 87.20 | I'M BLOWIN' I BUST MY OWN | right | BUST | — | ESTIMATED (sheet L8) |
| pnw-hook2-line21 | 87.20 | 87.46 | PIPE | full | PIPE | — | ESTIMATED (sheet L8) |
| pnw-hook2-line22 | 87.46 | 88.24 | GOT THE MONEY | left | MONEY | — | ESTIMATED (sheet L9) |
| pnw-hook2-line23 | 88.24 | 89.27 | THE POWER BITCH IS | right | POWER | — | ESTIMATED (sheet L9) |
| pnw-hook2-line24 | 89.27 | 89.53 | ALRIGHT | full | ALRIGHT | — | ESTIMATED (sheet L9) |
| pnw-hook2-line25 | 89.53 | 91.35 | BITCH WE PUT IN WORK BITCH WE | left | WORK | — | ESTIMATED (sheet L10) |
| pnw-hook2-line26 | 91.35 | 93.16 | PUT IN WORK WE GRINDING HARD AHH | right | HARD | — | ESTIMATED (sheet L10/11) |
| pnw-hook2-line27 | 93.16 | 93.42 | YEAH | full | YEAH | — | ESTIMATED (sheet L11) |

Director's rationale:
- pnw-hook2-line1: The hook opens left and lands on FROM as the origin.
- pnw-hook2-line2: The line shifts right and builds to GET as the effort to rest.
- pnw-hook2-line3: SLEEP fills the frame as the rest that is denied.
- pnw-hook2-line4: The next line opens left and lands on CANNOT as the block.
- pnw-hook2-line5: The line shifts right and lands on NO as the denial.
- pnw-hook2-line6: PEACE fills the frame as the calm that is denied.
- pnw-hook2-line7: The line returns left and lands on BAY as the home place.
- pnw-hook2-line8: The line shifts right and lands on FUCKING as the hard edge of the denial.
- pnw-hook2-line9: WEEP fills the frame as the grief that is refused.
- pnw-hook2-line10: The line opens left and lands on KNOW as the shared knowledge.
- pnw-hook2-line11: The line shifts right and lands on CARS as the street work named.
- pnw-hook2-line12: OG fills the frame as the missing elder.
- pnw-hook2-line13: The next line opens left and lands on OUTSIDE as the move out.
- pnw-hook2-line14: The line shifts right and lands on CAR as the object hit.
- pnw-hook2-line15: REASON fills the frame as the missing motive.
- pnw-hook2-line16: The smoother line opens left and lands on SMOOTH as the manner.
- pnw-hook2-line17: The line shifts right and lands on CREEPIN' as the movement into night.
- pnw-hook2-line18: NIGHT fills the frame as the setting for the movement.
- pnw-hook2-line19: The line opens left and lands on NIGGAS as the people nearby.
- pnw-hook2-line20: The line shifts right and lands on BUST as the action taken.
- pnw-hook2-line21: PIPE fills the frame as the object in that action.
- pnw-hook2-line22: The reward line opens left and lands on MONEY as the gain.
- pnw-hook2-line23: The line shifts right and lands on POWER as the second gain.
- pnw-hook2-line24: ALRIGHT fills the frame as the verdict on that gain.
- pnw-hook2-line25: The chant returns left and lands on WORK as the labor repeated.
- pnw-hook2-line26: The line shifts right and lands on HARD as the effort in the grind.
- pnw-hook2-line27: YEAH fills the frame to close the hook.

## pnw-verse2 — VERSE2 (13 sheet lines → 33 display lines)

Timing source: house whisper-large-v3 timing grid on the V3 master (song_grid.json, 473 timed words; 90s head slice + 45s re-sliced tail); words are BO's lyric sheet ONLY -- ASR text was used for timing, never displayed; per-word timing provenance (ANCHORED / INTERPOLATED / ESTIMATED) is recorded line-by-line in PNW-PLAN.md. Sheet absolute times were NOT used: measured drift vs V3 runs +11.2s at HOOK 1 to -31.9s at FINAL HOOK.
Model: muse-wonder-1.0 · generated 2026-11-04T12:17:38-06:00 · receipts: resp_6aeb76c22254287dbdfa4785 · Wonder spend this section: $0.7896 (1 call(s))

| Line | In | Out | Display | Placement | Hero | Effects | Timing |
|---|---|---|---|---|---|---|---|
| pnw-verse2-line1 | 93.42 | 95.24 | BITCH I PUT IN WORK OKAY NEVER | left | WORK | — | ESTIMATED (sheet L1) |
| pnw-verse2-line2 | 95.24 | 97.05 | TAKE NO DAYS OFF I'MA GET THIS | right | GET | — | ESTIMATED (sheet L1/2) |
| pnw-verse2-line3 | 97.05 | 97.31 | CAKE | full | CAKE | — | ESTIMATED (sheet L2) |
| pnw-verse2-line4 | 97.31 | 98.61 | OKAY I'MA MAKE SURE WE | left | SURE | — | ESTIMATED (sheet L2) |
| pnw-verse2-line5 | 98.61 | 100.07 | GON' BALL WHEN WE GET THE | right | BALL | — | ESTIMATED (sheet L2/3) |
| pnw-verse2-line6 | 100.07 | 100.37 | PACKAGE | full | PACKAGE | — | ANCHORED (sheet L3) |
| pnw-verse2-line7 | 100.37 | 101.96 | NIGGA THEN WE GON' SET IT | left | SET | — | ANCHORED (sheet L3) |
| pnw-verse2-line8 | 101.96 | 103.17 | OFF WHEN THEY COMING OUR | right | COMING | — | INTERPOLATED (sheet L3/4) |
| pnw-verse2-line9 | 103.17 | 103.35 | WAY | full | WAY | — | ANCHORED (sheet L4) |
| pnw-verse2-line10 | 103.35 | 104.72 | NIGGA THEN WE GONNA PLAY IT | left | PLAY | — | INTERPOLATED (sheet L4) |
| pnw-verse2-line11 | 104.72 | 105.11 | RAW I BE TURNIN' FOR | right | TURNIN' | — | INTERPOLATED (sheet L4/5) |
| pnw-verse2-line12 | 105.11 | 105.19 | REAL | full | REAL | — | INTERPOLATED (sheet L5) |
| pnw-verse2-line13 | 105.19 | 107.07 | NIGGA TURNT UP OFF THESE PILLS | left | PILLS | — | ANCHORED (sheet L5) |
| pnw-verse2-line14 | 107.07 | 108.05 | GIVE A DAMN I GOT NO | right | DAMN | — | INTERPOLATED (sheet L6) |
| pnw-verse2-line15 | 108.05 | 108.45 | CHILL | full | CHILL | — | ANCHORED (sheet L6) |
| pnw-verse2-line16 | 108.45 | 109.27 | LITTLE BITCHES I GOT | left | BITCHES | — | ANCHORED (sheet L6) |
| pnw-verse2-line17 | 109.27 | 110.65 | NO FEEL AYE FREE LIH | right | FEEL | — | INTERPOLATED (sheet L6/7) |
| pnw-verse2-line18 | 110.65 | 110.77 | BLAST | full | BLAST | — | ANCHORED (sheet L7) |
| pnw-verse2-line19 | 110.77 | 112.35 | FOR REAL WHEN HE GET OUT BITCHES | left | OUT | — | ANCHORED (sheet L7) |
| pnw-verse2-line20 | 112.35 | 113.91 | IT DRILLED WE BE GETTIN' TO THAT | right | DRILLED | — | ANCHORED (sheet L7/8) |
| pnw-verse2-line21 | 113.91 | 114.31 | MONEY | full | MONEY | — | ANCHORED (sheet L8) |
| pnw-verse2-line22 | 114.31 | 115.25 | NO CAP REAL | left | CAP | — | ANCHORED (sheet L8) |
| pnw-verse2-line23 | 115.25 | 116.75 | SPILL NO CAP REAL | right | NO | — | ANCHORED (sheet L8/9) |
| pnw-verse2-line24 | 116.75 | 118.05 | SPILLLLLLLLLL | full | SPILLLLLLLLLL | — | ANCHORED (sheet L9) |
| pnw-verse2-line25 | 118.05 | 120.49 | NORTHWOOD DRIVE YOU COME AROUND THIS | left | DRIVE | — | INTERPOLATED (sheet L10) |
| pnw-verse2-line26 | 120.49 | 121.89 | BITCH YOU WILL GET YOUR ASS | right | ASS | — | INTERPOLATED (sheet L10/11) |
| pnw-verse2-line27 | 121.89 | 122.41 | SHOT | full | SHOT | — | ANCHORED (sheet L11) |
| pnw-verse2-line28 | 122.41 | 123.74 | YOU LOOK AROUND THE WAY | left | LOOK | — | ANCHORED (sheet L12) |
| pnw-verse2-line29 | 123.74 | 124.84 | YOU MIGHT SEE YO | right | SEE | — | INTERPOLATED (sheet L12) |
| pnw-verse2-line30 | 124.84 | 125.37 | OPPS | full | OPPS | — | INTERPOLATED (sheet L12) |
| pnw-verse2-line31 | 125.37 | 126.65 | BUT YOU SEE THEM COPS | left | COPS | — | INTERPOLATED (sheet L13) |
| pnw-verse2-line32 | 126.65 | 127.91 | YOU BETTER RUN AND HIDE IT AND | right | RUN | — | INTERPOLATED (sheet L13) |
| pnw-verse2-line33 | 127.91 | 127.99 | HOP | full | HOP | — | INTERPOLATED (sheet L13) |

Director's rationale:
- pnw-verse2-line1: The opening stack lands on WORK as the labor.
- pnw-verse2-line2: The line shifts right and lands on GET as the drive.
- pnw-verse2-line3: CAKE fills the frame as the prize.
- pnw-verse2-line4: The line opens left and lands on SURE as the certainty.
- pnw-verse2-line5: The line shifts right and lands on BALL as the play ahead.
- pnw-verse2-line6: PACKAGE fills the frame as the thing awaited.
- pnw-verse2-line7: The line opens left and lands on SET as the trigger.
- pnw-verse2-line8: The line shifts right and lands on COMING as the approach.
- pnw-verse2-line9: WAY fills the frame as the route they take.
- pnw-verse2-line10: The line opens left and lands on PLAY as the action.
- pnw-verse2-line11: The line shifts right and lands on TURNIN' as the movement.
- pnw-verse2-line12: REAL fills the frame as the truth claim.
- pnw-verse2-line13: The line opens left and lands on PILLS as the cause.
- pnw-verse2-line14: The line shifts right and lands on DAMN as the disregard.
- pnw-verse2-line15: CHILL fills the frame as the calm that is missing.
- pnw-verse2-line16: The line opens left and lands on BITCHES as the people addressed.
- pnw-verse2-line17: The line shifts right and lands on FEEL as the feeling that is missing.
- pnw-verse2-line18: BLAST fills the frame as the name called out.
- pnw-verse2-line19: The line opens left and lands on OUT as the release ahead.
- pnw-verse2-line20: The line shifts right and lands on DRILLED as the consequence.
- pnw-verse2-line21: MONEY fills the frame as the gain.
- pnw-verse2-line22: The line opens left and lands on CAP as the truth marker.
- pnw-verse2-line23: The line shifts right and lands on NO as the denial repeated.
- pnw-verse2-line24: The long spill fills the frame as the claim stretches out.
- pnw-verse2-line25: The tail opens left and lands on DRIVE as the place named.
- pnw-verse2-line26: The line shifts right and lands on ASS as the target.
- pnw-verse2-line27: SHOT fills the frame as the threat.
- pnw-verse2-line28: The line opens left and lands on LOOK as the scan.
- pnw-verse2-line29: The line shifts right and lands on SEE as the spotting.
- pnw-verse2-line30: OPPS fills the frame as the rivals spotted.
- pnw-verse2-line31: The line opens left and lands on COPS as the authority spotted.
- pnw-verse2-line32: The line shifts right and lands on RUN as the flight.
- pnw-verse2-line33: HOP fills the frame as the final jump.

## pnw-finalhook — FINAL HOOK (11 sheet lines → 24 display lines)

Timing source: house whisper-large-v3 timing grid on the V3 master (song_grid.json, 473 timed words; 90s head slice + 45s re-sliced tail); words are BO's lyric sheet ONLY -- ASR text was used for timing, never displayed; per-word timing provenance (ANCHORED / INTERPOLATED / ESTIMATED) is recorded line-by-line in PNW-PLAN.md. Sheet absolute times were NOT used: measured drift vs V3 runs +11.2s at HOOK 1 to -31.9s at FINAL HOOK.
Model: muse-wonder-1.0 · generated 2026-11-04T12:18:51-06:00 · receipts: resp_6aeb770ad08e15c63baa47b7 · Wonder spend this section: $0.2978 (1 call(s))

| Line | In | Out | Display | Placement | Hero | Effects | Timing |
|---|---|---|---|---|---|---|---|
| pnw-finalhook-line1 | 127.99 | 128.93 | NIGGA WHERE I'M FROM | left | FROM | — | ANCHORED (sheet L1) |
| pnw-finalhook-line2 | 128.93 | 129.67 | YOU CAN'T GET NO | right | GET | — | ANCHORED (sheet L1) |
| pnw-finalhook-line3 | 129.67 | 130.03 | SLEEP | full | SLEEP | — | ANCHORED (sheet L1) |
| pnw-finalhook-line4 | 130.03 | 131.51 | YOU CANNOT GET NO PEACE | left | PEACE | — | ANCHORED (sheet L2) |
| pnw-finalhook-line5 | 131.51 | 132.63 | NIGGA WHERE I'M FROM THE | right | WHERE | — | ANCHORED (sheet L3) |
| pnw-finalhook-line6 | 132.63 | 132.97 | BAY | full | BAY | — | ANCHORED (sheet L3) |
| pnw-finalhook-line7 | 132.97 | 134.77 | WE DO NOT FUCKING WEEP ALL WE | left | WEEP | — | ANCHORED (sheet L3/4) |
| pnw-finalhook-line8 | 134.77 | 136.59 | KNOW IS CRACK CARS WE HAD NO | right | CRACK | — | ANCHORED (sheet L4) |
| pnw-finalhook-line9 | 136.59 | 136.96 | OG | full | OG | — | ANCHORED (sheet L4) |
| pnw-finalhook-line10 | 136.96 | 138.77 | I WENT OUTSIDE WITH THE BARS | left | OUTSIDE | — | INTERPOLATED (sheet L5) |
| pnw-finalhook-line11 | 138.77 | 139.91 | HIT A CAR FOR NO | right | CAR | — | ANCHORED (sheet L5) |
| pnw-finalhook-line12 | 139.91 | 140.06 | REASON | full | REASON | — | ANCHORED (sheet L5) |
| pnw-finalhook-line13 | 140.06 | 141.23 | WE SMOOTH WITH IT TRUE | left | SMOOTH | — | INTERPOLATED (sheet L6) |
| pnw-finalhook-line14 | 141.23 | 142.49 | WITH IT CREEPIN' THROUGH THE | right | CREEPIN' | — | ANCHORED (sheet L6/7) |
| pnw-finalhook-line15 | 142.49 | 142.71 | NIGHT | full | NIGHT | — | ANCHORED (sheet L7) |
| pnw-finalhook-line16 | 142.71 | 143.99 | THEM NIGGAS ROUND ME I'M | left | NIGGAS | — | ANCHORED (sheet L7/8) |
| pnw-finalhook-line17 | 143.99 | 145.31 | BLOWIN' I BUST MY OWN | right | BUST | — | ANCHORED (sheet L8) |
| pnw-finalhook-line18 | 145.31 | 145.59 | PIPE | full | PIPE | — | ANCHORED (sheet L8) |
| pnw-finalhook-line19 | 145.59 | 147.23 | GOT THE MONEY THE POWER | left | MONEY | — | ANCHORED (sheet L9) |
| pnw-finalhook-line20 | 147.23 | 149.52 | BITCH IS ALRIGHT BITCH WE PUT IN | right | ALRIGHT | — | INTERPOLATED (sheet L9/10) |
| pnw-finalhook-line21 | 149.52 | 149.79 | WORK | full | WORK | — | INTERPOLATED (sheet L10) |
| pnw-finalhook-line22 | 149.79 | 150.74 | BITCH WE PUT IN WORK | left | PUT | — | INTERPOLATED (sheet L10) |
| pnw-finalhook-line23 | 150.74 | 151.56 | WE GRINDING HARD AHH | right | GRINDING | — | INTERPOLATED (sheet L11) |
| pnw-finalhook-line24 | 151.56 | 151.80 | YEAH | full | YEAH | — | INTERPOLATED (sheet L11) |

Director's rationale:
- pnw-finalhook-line1: The line opens left and lands on FROM as the origin.
- pnw-finalhook-line2: The line shifts right and lands on GET as the attempt to rest.
- pnw-finalhook-line3: SLEEP fills the frame as the rest that is missing.
- pnw-finalhook-line4: The line opens left and lands on PEACE as the calm that is missing.
- pnw-finalhook-line5: The line shifts right and lands on WHERE as the place recalled.
- pnw-finalhook-line6: BAY fills the frame as the home place.
- pnw-finalhook-line7: The line opens left and lands on WEEP as the grief denied.
- pnw-finalhook-line8: The line shifts right and lands on CRACK as what is known.
- pnw-finalhook-line9: OG fills the frame as the guide that was missing.
- pnw-finalhook-line10: The line opens left and lands on OUTSIDE as the move out.
- pnw-finalhook-line11: The line shifts right and lands on CAR as the target hit.
- pnw-finalhook-line12: REASON fills the frame as the missing cause.
- pnw-finalhook-line13: The line opens left and lands on SMOOTH as the manner.
- pnw-finalhook-line14: The line shifts right and lands on CREEPIN' as the movement.
- pnw-finalhook-line15: NIGHT fills the frame as the time of movement.
- pnw-finalhook-line16: The line opens left and lands on NIGGAS as the people nearby.
- pnw-finalhook-line17: The line shifts right and lands on BUST as the action taken.
- pnw-finalhook-line18: PIPE fills the frame as the object used.
- pnw-finalhook-line19: The line opens left and lands on MONEY as the gain.
- pnw-finalhook-line20: The line shifts right and lands on ALRIGHT as the claimed state.
- pnw-finalhook-line21: WORK fills the frame as the labor claimed.
- pnw-finalhook-line22: The line opens left and lands on PUT as the repeated effort.
- pnw-finalhook-line23: The line shifts right and lands on GRINDING as the ongoing work.
- pnw-finalhook-line24: YEAH fills the frame as the final affirmation.

## Validator measurement (the stress test's open item, closed)

`validator_rejects` = the REAL `validate()`'s errors on each section's FIRST candidate (attempt 0, before any repair), recorded separately from the wrapper's extra checks (motif/redlight discipline, cross-unit placement) and from the final clean pass.

- **pnw-hook1**: first-pass validate() rejects: **0**; wrapper rejects: 0; final: re-validated clean (1 unit(s), 0 errors)
- **pnw-verse1**: first-pass validate() rejects: **0**; wrapper rejects: 0; final: re-validated clean (1 unit(s), 0 errors)
- **pnw-bridge**: first-pass validate() rejects: **0**; wrapper rejects: 0; final: re-validated clean (1 unit(s), 0 errors)
- **pnw-hook2**: first-pass validate() rejects: **0**; wrapper rejects: 0; final: re-validated clean (1 unit(s), 0 errors)
- **pnw-verse2**: first-pass validate() rejects: **0**; wrapper rejects: 0; final: re-validated clean (1 unit(s), 0 errors)
- **pnw-finalhook**: first-pass validate() rejects: **0**; wrapper rejects: 0; final: re-validated clean (1 unit(s), 0 errors)

**Totals:** first-pass validate() rejects **0** across 6 sections · wrapper rejects 0 · final pass: **CLEAN** · Wonder calls 6 · **total Wonder spend $2.5662**.

## Flagged estimates (timing BO should sanity-check by ear)

Most of these display lines sit in the grid's dead/degraded zone (HOOK 2's back half + VERSE 2's opening, ≈81.8–100s). Two edge cases ride along: the song's very first word (chunk-0 artifact — HOOK 1 word 1's onset is estimated at 11.02s; the true vocal onset is ≈11.2s) and the FINAL HOOK's last line tail. Onsets in the dead zone are a word-rate spread between hard anchors — expect them to be close, not frame-true. The Northwood Drive passage lines are INTERPOLATED inside hard bounds (VERSE 2 line-10 anchor 115.32s → FINAL HOOK onset 128.06s) with garbled grid text; their words are the sheet's, their times are bounded estimates.

- pnw-hook1-line1 @ 10.95s — NIGGA WHERE I'M FROM (sheet L1)
- pnw-hook2-line16 @ 81.75s — WE SMOOTH WITH IT (sheet L6)
- pnw-hook2-line17 @ 82.79s — TRUE WITH IT CREEPIN' THROUGH THE (sheet L6/7)
- pnw-hook2-line18 @ 84.34s — NIGHT (sheet L7)
- pnw-hook2-line19 @ 84.60s — THEM NIGGAS ROUND ME (sheet L7)
- pnw-hook2-line20 @ 85.64s — I'M BLOWIN' I BUST MY OWN (sheet L8)
- pnw-hook2-line21 @ 87.20s — PIPE (sheet L8)
- pnw-hook2-line22 @ 87.46s — GOT THE MONEY (sheet L9)
- pnw-hook2-line23 @ 88.24s — THE POWER BITCH IS (sheet L9)
- pnw-hook2-line24 @ 89.27s — ALRIGHT (sheet L9)
- pnw-hook2-line25 @ 89.53s — BITCH WE PUT IN WORK BITCH WE (sheet L10)
- pnw-hook2-line26 @ 91.35s — PUT IN WORK WE GRINDING HARD AHH (sheet L10/11)
- pnw-hook2-line27 @ 93.16s — YEAH (sheet L11)
- pnw-verse2-line1 @ 93.42s — BITCH I PUT IN WORK OKAY NEVER (sheet L1)
- pnw-verse2-line2 @ 95.24s — TAKE NO DAYS OFF I'MA GET THIS (sheet L1/2)
- pnw-verse2-line3 @ 97.05s — CAKE (sheet L2)
- pnw-verse2-line4 @ 97.31s — OKAY I'MA MAKE SURE WE (sheet L2)
- pnw-verse2-line5 @ 98.61s — GON' BALL WHEN WE GET THE (sheet L2/3)

Plan total: **150 display lines** across 6 sections, sung span 11.02s → 151.80s on V3. The ~72s after 151.8s is instrumental outro — no lines, by design.

