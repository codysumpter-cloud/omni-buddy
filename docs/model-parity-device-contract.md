# Model Parity Device Contract

Status: device/runtime contract  
Created: 2026-06-15

## Purpose

Omni Buddy treats Fable/Mythos-style parity as a device runtime problem, not only a model architecture problem.

OpenMythos and OpenFable can inspire local research backends, but Omni parity depends on device proof:

- wake/listen/speak loop
- local or hybrid LLM routing
- camera/vision routing
- speech-to-text and text-to-speech
- latency receipts
- offline-first fallback behavior
- guarded device actions

## Sources

- `https://platform.claude.com/docs/en/about-claude/models/introducing-claude-fable-5-and-claude-mythos-5`
- `https://github.com/kyegomez/OpenMythos`
- `https://github.com/lovestaco/OpenFable`

## Device parity map

| Capability | Omni target | Rule |
|---|---|---|
| Adaptive compute | Map effort levels to local loop budget or hosted provider effort. | Expose summaries and receipts, not private reasoning. |
| Memory | Sync durable events to Buddy/Vegapunk-compatible memory. | Keep private data out of public repo history. |
| Tools | Device commands pass through guarded adapters. | No unsupervised destructive actions. |
| Vision | Camera input routes through explicit local/hybrid vision adapters. | Require receipt before claiming support. |
| Compaction | Long sessions need summary/context management before device overflow. | Missing until implemented and tested. |
| Fallback | Device reports degraded mode when a route fails. | Silent fallback is not allowed. |

## Implementation targets

1. Add a device capability receipt format.
2. Add `quick`, `balanced`, and `deep` effort presets.
3. Add long-session compaction before context overflow.
4. Add a vision receipt whenever camera mode is used.

## Claim boundary

Allowed: "This device route implements Buddy's Fable/Mythos-inspired runtime controls."

Not allowed without proof: "This device runs Claude Fable 5 / Mythos 5 locally."
