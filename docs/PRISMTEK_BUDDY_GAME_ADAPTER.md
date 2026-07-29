# Omni Buddy → Prismtek Buddies Adapter

`adapters/prismtek_buddy_game.py` routes embodied Omni Buddy input through the canonical `prismtek-buddy-game-v1` contract.

It is deliberately an adapter, not another agent brain:

```text
wake word / push-to-talk / camera summary
  → Omni Buddy
  → Prismtek Buddy game adapter
  → buddy-serve or Prismtek.dev /api/buddy-game
  → BUAP + KnowledgeVault + Buddy Brain + task runtime
  → proposed game commands
  → Godot validates current room state and executes or rejects
```

## Local full-stack setup

Start Buddy Agent:

```bash
cd /path/to/buddy-agent
python -m pip install -e .
BUDDY_PROVIDER=ollama \
BUDDY_MODEL=qwen3:8b \
BUDDY_PROJECT_ROOT=/path/to/prismtek-apps \
BUDDY_VAULT_PATH=/path/to/knowledge-vault \
BUDDY_BRAIN_REPORT_PATH=/path/to/buddy-trust-fabric-report.json \
buddy-serve
```

Then from Omni Buddy:

```bash
python3 adapters/prismtek_buddy_game.py status
python3 adapters/prismtek_buddy_game.py voice "game ask Buddy what is near the desk"
python3 adapters/prismtek_buddy_game.py voice \
  "game ask Buddy what I can do with the laptop" \
  --vision-summary "A desk and laptop are visible near the character."
python3 adapters/prismtek_buddy_game.py voice "game task remember the bedroom layout"
python3 adapters/prismtek_buddy_game.py voice "game tasks"
```

## Configuration

Environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `BUDDY_GAME_BASE_URL` | `http://127.0.0.1:8765` | Buddy game runtime base URL |
| `BUDDY_GAME_TOKEN` | unset | Optional bearer token for a protected bridge |
| `BUDDY_GAME_TIMEOUT_SECONDS` | `45` | Request timeout |

The adapter can target the hosted endpoint only from a client that has an authenticated Prismtek.dev account session. A Raspberry Pi CLI does not copy browser cookies or account tokens; its normal route is the guarded local `buddy-serve` runtime.

## Safe voice forms

- `game status`
- `game tasks`
- `game task <objective>`
- `game <message>`
- `prismtek buddies <message>`

The adapter may call only game chat and persistent task lifecycle tools. It refuses Codex delegation, shell, `buddy-exec`, repository mutation, merge, release, and deployment tools.

## Vision boundary

A camera frame is not uploaded by this adapter. Omni Buddy may pass a bounded text summary through `vision_summary`. The Buddy runtime treats it as untrusted context, and Godot still validates every proposed target against the currently loaded room.

## Validation

```bash
python3 -m unittest -v tests.test_prismtek_buddy_game_adapter
./scripts/run_validation_matrix.sh
```

The tests prove:

- protocol/version verification;
- optional bearer authentication;
- voice and vision-summary routing;
- persistent task creation/listing;
- tool allowlisting;
- credentials are not returned by tool discovery.
