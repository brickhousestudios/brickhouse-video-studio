# API SPEND LEDGER — Meta Hackathon / BrickHouse Video Studio

Running ledger BO asked for 2026-11-05 01:16 ("keep track of all the api
spent with sam or usin musewonder etc"). Source of truth for per-call detail:
`receipts.log` + regenerated `receipts.md` in video-studio-meta on the M4
(make_receipts_md.py; fixed its None-cost crash 2026-11-05).

## Meta Model API — receipts.log (39 calls, VERIFIED sum 2026-11-05)
- wonder_director_call (muse-wonder-1.0): 23 calls — $5.2936
- wonder_director_repair: 3 calls — $0.1374
- sam_video_segmentation (sam-3.1, Nov 1 recon): 4 calls — $0.0396
- muse_image_call (muse-image-1.0): 3 calls — $0.0300
- voice_transcribe_call: 1 call — $0.0000
- file_upload / models_list: $0.0000
- **TOTAL: $5.5006** (matches the $5.500609 figure carried in the submission copy)

## SAM 3.1 — Nov 4 evening SPILL runs (BUILD-LOG receipts; their JSONL was not preserved)
- Run 1 window-only: **$0.0092** — resp_6aec06de0217dcb04a0a49e3 (BUILD-LOG line 896)
- Run 2 full clip: 144 frames x $0.20/1k = **$0.0288** — resp_6aec08063eb4ba1653fb4619
- Subtotal: **$0.0380**

## Event total
- **$5.5386 of the $150 Meta Model API credit** (receipts-backed $5.5006 + SAM $0.0380)
- Separate, per the submission copy: BO's Muse subscription is also part of production cost.
- Boundary: this ledger covers Meta Model API calls in receipts.log plus the two
  BUILD-LOG SAM runs. Anything billed outside those lanes is not in here.
