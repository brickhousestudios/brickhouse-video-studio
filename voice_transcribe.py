# Adapted from Meta's meta-model-cookbook, 06_muse_voice/01_voice_api_fundamentals
# (transcribe_file.py + utils.py transcribe_recording()).
# Source: https://github.com/meta-models/meta-model-cookbook/blob/HEAD/06_muse_voice/01_voice_api_fundamentals/utils.py
# (Meta license: see the LICENSE file in the cookbook repository root.)
#
# The model (muse-voice-transcribe-1.0) is NOT served on the OpenAI-shaped
# routes of api.meta.ai: /v1/audio/transcriptions 404s, and both
# /v1/responses and /v1/chat/completions answer 404 "The requested model was
# not found" for it (probed 2026-11-02). It has a dedicated one-shot file
# endpoint instead: POST https://api.meta.ai/v1/asr/transcribe with a
# multipart body -- a JSON "request" part (mode, model, audioEncoding) and an
# "audio" part carrying a mono 16-bit WAV (24 kHz native; 16 kHz accepted).
# Caps: 10 minutes of audio / 32 MB. The response is one JSON object:
# {"sessionId", "transcript", "audioDurationMs", "turns": [...]} where turns
# (present in the ENDPOINTING / DIARIZATION modes) carry startMs/endMs and a
# per-turn transcript -- line-level timing only, no word timing.
#
# BrickHouse adaptations, kept minimal and marked:
#  1. The API key is sourced the way the M4 setup does it (same order as
#     sam_api.client()): env MODEL_API_KEY, otherwise the macOS login-keychain
#     item "brickhouse-meta-api". Held in memory only -- never printed,
#     logged, or written to disk.
#  2. Stdlib only (urllib), so the script needs nothing beyond the repo venv.
#  3. Non-WAV input is converted with the cookbook's prescribed ffmpeg line
#     (mono, 24 kHz, s16) into a temp file before upload.
#  4. A RECEIPTS line (house receipts.log JSON-lines format) is appended per
#     call: request id / session id and audio seconds only. No published rate
#     for this model exists in the repo materials or the cookbook, so cost is
#     recorded as null (UNKNOWN) rather than invented.
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

TRANSCRIBE_URL = "https://api.meta.ai/v1/asr/transcribe"
MODEL = "muse-voice-transcribe-1.0"
MODES = ("PUSH_TO_TALK", "ENDPOINTING", "DIARIZATION")
KEYCHAIN_SERVICE = "brickhouse-meta-api"
MAX_BYTES = 32 * 1024 * 1024
HERE = Path(__file__).resolve().parent


def _keychain_api_key() -> str | None:
    """Read the Model API key from the M4 login keychain (runtime only).

    Mirrors sam_api._keychain_api_key() so this script stays stdlib-only and
    does not import the SAM parser stack just to source a key.
    """
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def api_key() -> str:
    key = os.environ.get("MODEL_API_KEY") or _keychain_api_key()
    if not key:
        raise RuntimeError(
            "Set MODEL_API_KEY or provision the login-keychain item "
            f"{KEYCHAIN_SERVICE!r} before calling the Voice Transcribe API."
        )
    return key


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_wav(path: Path, tmpdir: Path) -> Path:
    """Return a mono 16-bit 24 kHz WAV for `path` (converting via ffmpeg)."""
    if path.suffix.lower() == ".wav":
        return path
    out = tmpdir / (path.stem + ".wav")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(path),
        "-ac", "1", "-ar", "24000", "-sample_fmt", "s16", str(out),
    ]
    subprocess.run(cmd, check=True)
    return out


def post_transcription(wav: Path, *, mode: str, key: str, session_id: str,
                       timeout: int = 300) -> tuple[int, str | None, dict[str, Any]]:
    """POST the WAV to the one-shot endpoint; return (status, request_id, json)."""
    request_part = json.dumps(
        {"mode": mode, "model": MODEL, "audioEncoding": "WAV"}
    ).encode("utf-8")
    boundary = "----brickhouse-" + uuid.uuid4().hex
    body = bytearray()
    body += f"--{boundary}\r\n".encode()
    body += b'Content-Disposition: form-data; name="request"\r\n'
    body += b"Content-Type: application/json\r\n\r\n"
    body += request_part + b"\r\n"
    body += f"--{boundary}\r\n".encode()
    body += (
        f'Content-Disposition: form-data; name="audio"; '
        f'filename="{wav.name}"\r\n'
    ).encode()
    body += b"Content-Type: audio/wav\r\n\r\n"
    body += wav.read_bytes() + b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    url = f"{TRANSCRIBE_URL}?sessionId={session_id}"
    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("Authorization", f"Bearer {key}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            return resp.status, resp.headers.get("x-request-id"), payload
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"Voice Transcribe HTTP {exc.code}: {detail}") from exc


def parse_turns(payload: dict[str, Any]) -> list[dict[str, Any]]:
    turns = []
    for turn in payload.get("turns") or []:
        start_ms = turn.get("startMs")
        end_ms = turn.get("endMs")
        turns.append(
            {
                "start_s": None if start_ms is None else start_ms / 1000,
                "end_s": None if end_ms is None else end_ms / 1000,
                "text": turn.get("transcript", ""),
                **({"speaker": turn["speaker"]} if turn.get("speaker") else {}),
            }
        )
    return turns


def append_receipt(receipts_path: Path, *, request_id: str | None,
                   session_id: str, audio_seconds: float | None,
                   turn_count: int) -> None:
    line = {
        "ts_ct": datetime.now(ZoneInfo("America/Chicago")).isoformat(),
        "step": "voice-transcribe-108-bounce",
        "kind": "voice_transcribe_call",
        "model": MODEL,
        "request_id": request_id,
        "session_id": session_id,
        "units": audio_seconds,
        "unit": "audio_seconds",
        "unit_price_usd": None,
        "unit_price_basis": (
            "UNKNOWN - no published rate for muse-voice-transcribe-1.0 in the "
            "repo materials or the meta-model-cookbook (checked 2026-11-02)"
        ),
        "cost_usd": None,
        "note": (
            "route=one-shot-file-endpoint POST /v1/asr/transcribe; "
            f"mode=ENDPOINTING; turns={turn_count}"
        ),
    }
    with receipts_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", help="audio file to transcribe (WAV, or anything ffmpeg reads)")
    parser.add_argument("--mode", default="ENDPOINTING", choices=MODES,
                        help="ENDPOINTING = model-detected line boundaries (default)")
    parser.add_argument("--out", default=None, help="results JSON path")
    parser.add_argument("--receipts", default=str(HERE / "receipts.log"),
                        help="receipts.log to append to")
    args = parser.parse_args()

    source = Path(args.audio)
    out_path = Path(args.out) if args.out else HERE / f"voice-transcribe-{source.stem}.json"
    session_id = uuid.uuid4().hex

    with tempfile.TemporaryDirectory() as td:
        wav = ensure_wav(source, Path(td))
        size = wav.stat().st_size
        if size > MAX_BYTES:
            raise RuntimeError(f"Converted WAV is {size} bytes; the one-shot cap is {MAX_BYTES}.")
        status, request_id, payload = post_transcription(
            wav, mode=args.mode, key=api_key(), session_id=session_id
        )

    turns = parse_turns(payload)
    duration_ms = payload.get("audioDurationMs")
    results = {
        "source": {
            "file": source.name,
            "sha256": sha256_of(source),
        },
        "request": {
            "endpoint": TRANSCRIBE_URL,
            "model": MODEL,
            "mode": args.mode,
            "audio_encoding": "WAV (mono, 16-bit, 24 kHz)",
            "session_id": session_id,
            "http_status": status,
            "http_request_id": request_id,
        },
        "response": payload,
        "turns": turns,
    }
    out_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    append_receipt(
        Path(args.receipts),
        request_id=request_id,
        session_id=payload.get("sessionId") or session_id,
        audio_seconds=None if duration_ms is None else duration_ms / 1000,
        turn_count=len(turns),
    )
    print(f"session={payload.get('sessionId')} turns={len(turns)} "
          f"audio={None if duration_ms is None else duration_ms / 1000}s -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
