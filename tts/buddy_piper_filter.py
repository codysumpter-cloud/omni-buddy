#!/usr/bin/env python3
"""
Buddy Piper voice filter.

Transparent wrapper for Piper:
- `--install-wrapper` moves `piper/piper` to `piper/piper.real`
- creates a small shim at `piper/piper`
- normal agent calls keep working, then output WAV is post-processed
  into a bright, cute, toy-robot profile.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.json"
PIPER_DIR = ROOT / "piper"
WRAPPER_PATH = PIPER_DIR / "piper"
REAL_PIPER_PATH = PIPER_DIR / "piper.real"

DEFAULTS = {
    "buddy_voice_enabled": True,
    "tts_voice_profile": "bright_toy_robot",
    "buddy_voice_speed": 1.11,
    "buddy_voice_pitch_shift_steps": 2.0,
    "buddy_voice_gain_db": 1.5,
    "buddy_voice_bitcrush_bits": 12,
    "buddy_voice_vibrato_hz": 5.2,
    "buddy_voice_vibrato_depth": 0.006,
    "buddy_voice_max_chars": 260,
}


def load_config() -> dict:
    cfg = dict(DEFAULTS)
    try:
        if CONFIG_PATH.exists():
            with CONFIG_PATH.open("r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            cfg.update(user_cfg)
    except Exception as exc:
        print(f"[buddy-tts] warning: could not read config.json: {exc}", file=sys.stderr)
    return cfg


def install_wrapper() -> int:
    PIPER_DIR.mkdir(parents=True, exist_ok=True)

    if not WRAPPER_PATH.exists():
        print("[buddy-tts] piper/piper not found yet; run setup.sh after Piper downloads.", file=sys.stderr)
        return 0

    try:
        current = WRAPPER_PATH.read_text("utf-8", errors="ignore")[:256]
    except Exception:
        current = ""

    if "buddy_piper_filter.py" in current:
        print("[buddy-tts] Piper wrapper already installed")
        return 0

    if not REAL_PIPER_PATH.exists():
        shutil.move(str(WRAPPER_PATH), str(REAL_PIPER_PATH))
    else:
        WRAPPER_PATH.unlink()

    shim = """#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$ROOT/tts/buddy_piper_filter.py" "$@"
"""
    WRAPPER_PATH.write_text(shim, encoding="utf-8")
    WRAPPER_PATH.chmod(0o755)
    try:
        REAL_PIPER_PATH.chmod(0o755)
    except Exception:
        pass

    print("[buddy-tts] installed Piper wrapper -> piper/piper.real")
    return 0


def find_output_file(argv: list[str]) -> Path | None:
    for i, arg in enumerate(argv):
        if arg == "--output_file" and i + 1 < len(argv):
            return Path(argv[i + 1]).expanduser()
        if arg.startswith("--output_file="):
            return Path(arg.split("=", 1)[1]).expanduser()
    return None


def read_wav(path: Path):
    with wave.open(str(path), "rb") as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        rate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())

    if sampwidth != 2:
        return None

    import numpy as np

    audio = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)
    return rate, audio


def write_wav(path: Path, rate: int, audio) -> None:
    import numpy as np

    audio = np.asarray(audio, dtype=np.float32)
    audio = np.clip(audio, -0.98, 0.98)
    pcm = (audio * 32767.0).astype("<i2")

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(pcm.tobytes())


def shape_voice(path: Path, cfg: dict) -> None:
    if not cfg.get("buddy_voice_enabled", True):
        return

    loaded = read_wav(path)
    if not loaded:
        return

    import numpy as np
    from scipy import signal

    rate, audio = loaded
    if audio.size < 16:
        return

    audio = audio - float(np.mean(audio))
    peak = float(np.max(np.abs(audio))) or 1.0
    audio = audio / peak * 0.82

    speed = float(cfg.get("buddy_voice_speed", 1.11))
    speed = min(max(speed, 0.85), 1.35)
    if abs(speed - 1.0) > 0.01:
        target_len = max(16, int(len(audio) / speed))
        audio = signal.resample(audio, target_len)

    semis = float(cfg.get("buddy_voice_pitch_shift_steps", 2.0))
    semis = min(max(semis, -4.0), 5.0)
    pitch_factor = 2 ** (semis / 12.0)
    if abs(pitch_factor - 1.0) > 0.01:
        lifted_len = max(16, int(len(audio) / pitch_factor))
        lifted = signal.resample(audio, lifted_len)
        audio = signal.resample(lifted, len(audio))

    vibrato_hz = float(cfg.get("buddy_voice_vibrato_hz", 5.2))
    vibrato_depth = float(cfg.get("buddy_voice_vibrato_depth", 0.006))
    if vibrato_depth > 0:
        t = np.arange(len(audio), dtype=np.float32) / float(rate)
        audio = audio * (1.0 + vibrato_depth * np.sin(2 * math.pi * vibrato_hz * t))

    bits = int(cfg.get("buddy_voice_bitcrush_bits", 12))
    bits = min(max(bits, 8), 16)
    if bits < 16:
        levels = float(2 ** (bits - 1))
        audio = np.round(audio * levels) / levels

    gain_db = float(cfg.get("buddy_voice_gain_db", 1.5))
    audio = audio * (10 ** (gain_db / 20.0))

    fade = min(len(audio) // 8, int(rate * 0.012))
    if fade > 2:
        ramp = np.linspace(0.0, 1.0, fade, dtype=np.float32)
        audio[:fade] *= ramp
        audio[-fade:] *= ramp[::-1]

    peak = float(np.max(np.abs(audio))) or 1.0
    if peak > 0.95:
        audio = audio / peak * 0.95

    write_wav(path, rate, audio)


def run_piper(argv: list[str]) -> int:
    if not REAL_PIPER_PATH.exists():
        print("[buddy-tts] piper.real missing; run ./setup.sh first", file=sys.stderr)
        return 127

    output = find_output_file(argv)
    proc = subprocess.run([str(REAL_PIPER_PATH), *argv])
    if proc.returncode != 0:
        return proc.returncode

    if output and output.exists():
        cfg = load_config()
        try:
            shape_voice(output, cfg)
        except Exception as exc:
            print(f"[buddy-tts] warning: voice filter failed; using raw Piper output: {exc}", file=sys.stderr)

    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--install-wrapper", action="store_true")
    parser.add_argument("--print-config", action="store_true")
    known, remaining = parser.parse_known_args(argv)

    if known.install_wrapper:
        return install_wrapper()
    if known.print_config:
        print(json.dumps(load_config(), indent=2))
        return 0

    return run_piper(remaining)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
