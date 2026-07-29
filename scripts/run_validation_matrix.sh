#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[matrix] Omni-BMO validation start"

echo "[matrix] 1/6 doctor"
./scripts/bmo_omni_doctor.sh

echo "[matrix] 2/6 agent py compile"
python3 -m py_compile agent.py

echo "[matrix] 3/6 Prismtek Buddy game adapter compile"
python3 -m py_compile adapters/prismtek_buddy_game.py

echo "[matrix] 4/6 Prismtek Buddy game adapter tests"
python3 -m unittest -v tests.test_prismtek_buddy_game_adapter

echo "[matrix] 5/6 apply balanced latency profile"
python3 ./scripts/apply_latency_profile.py balanced --config config.json

echo "[matrix] 6/6 config sanity"
python3 - <<'PY'
import json
cfg=json.load(open('config.json'))
required=['llm_backend','omni_base_url','transport_mode','omni_tool_route_mode']
missing=[k for k in required if k not in cfg]
if missing:
  raise SystemExit(f"missing config keys: {missing}")
print('config ok:', {k:cfg.get(k) for k in required})
PY

echo "[matrix] Static and adapter checks passed. Run manual interaction tests from docs/VALIDATION_MATRIX.md"
