# Knowledge Vault Native Emitter: Omni Buddy

## Status

This document is a **native emitter specification only**. Omni Buddy does not yet include a production code adapter that writes directly into Knowledge Vault / Vegapunk Brain. Until that adapter exists and is reviewed, any emitted event is a drafted, reviewed artifact rather than automatic live device output.

BUAP remains the profile and routing layer. Omni Buddy owns local device, runtime, transport, and validation receipts; BUAP does not become the runtime owner.

## Source identity

- Source repo: `codysumpter-cloud/omni-buddy`
- Source name for Vegapunk Brain events: `omni-buddy`
- Receiver contract: `knowledge-vault/99-System/Vegapunk Brain/integrations/satellite-native-emitters.md`
- Receiver schema: `knowledge-vault/99-System/Vegapunk Brain/emitters/graph-event.schema.json`

## Emitter responsibility

Omni Buddy may emit public-safe event drafts for local runtime and transport validation:

- doctor run summaries;
- validation matrix results;
- runtime profile changes;
- latency profile changes;
- transport mode changes;
- repo/runtime capability concepts that should be searchable across the Buddy ecosystem.

Omni Buddy must not claim live device state without actual device receipts. If validation was simulated, partial, stale, or not run on-device, the event payload must say so clearly.

## Allowed event classes

Omni Buddy may draft the following event classes when they pass sanitization and receipt rules:

| Event class | Typical Vegapunk event types | Purpose |
| --- | --- | --- |
| `system` | `device_registered`, `model_changed`, `repo_updated` | Record public-safe runtime, device profile, and transport changes. |
| `task` | `task_created`, `task_completed` | Record validation work and safe result summaries. |
| `repo` | `repo_created`, `repo_updated`, `feature_added`, `feature_removed` | Record public repo capability changes tied to Omni runtime support. |
| `concept` | `concept_created`, `concept_updated`, `relationship_created` | Record reusable runtime, device, or transport concepts. |

## Trigger points

Native emitter code, once implemented, should draft an event at these points:

1. **Doctor run** — command summary, environment class, validation outcome, and public-safe receipt references.
2. **Validation matrix run** — target matrix, pass/fail/partial state, and known missing receipts.
3. **Runtime profile change** — profile name, public capabilities, compatibility notes, and validation state.
4. **Latency profile change** — summarized metrics, measurement context, and whether data is real-device or simulated.
5. **Transport mode change** — transport name, public-safe mode summary, compatibility state, and rollback note.

## Receipt truthfulness rules

Omni Buddy events must separate verified device state from assumptions:

- `verified` requires an actual receipt from the target runtime/device;
- `partially_verified` requires a receipt plus a clear missing-coverage note;
- `simulated` means the result was not measured on the live target device;
- `unverified` means no claim should be made beyond planned support or expected behavior;
- stale receipts must include the date and should not be presented as current state.

## Never emit

The native emitter must reject or strip all of the following:

- tokens, credentials, private keys, or other secret material;
- private local-network details, pairing material, host identifiers, or device identifiers that are not intentionally public;
- camera/audio private data, raw transcripts, raw frame captures, or private media metadata;
- raw prompts, hidden reasoning, private browser sessions, or private document excerpts;
- private local paths, personal machine names, account identifiers, or environment-specific absolute paths;
- unverifiable claims that a live device state exists without actual receipts.

## Event draft shape

Emitter output should be an event JSON object that validates against `graph-event.schema.json` before intake:

```json
{
  "event_id": "evt-omni-buddy-doctor-example",
  "event_type": "device_registered",
  "source": "omni-buddy",
  "timestamp": "2026-06-15T00:00:00Z",
  "payload": {
    "class": "system",
    "summary": "Public-safe Omni Buddy runtime validation receipt.",
    "validation_state": "simulated",
    "receipts": ["public log, commit, or artifact reference only"],
    "adapter_status": "spec-only"
  }
}
```

The example above is intentionally fake and public-safe. Real adapter output must provide real validation receipts without exposing secret material, local-network details, private media, or raw transcripts.

## Adapter requirements

Before Omni Buddy can be considered a complete native satellite emitter, it needs reviewed adapter code that:

1. builds event drafts from sanitized device/runtime/transport receipts only;
2. validates every draft against Knowledge Vault's `graph-event.schema.json`;
3. blocks emission on sanitizer failure;
4. labels validation truthfully as verified, partially verified, simulated, stale, or unverified;
5. writes to the reviewed receiver intake path rather than directly mutating compiled graph outputs;
6. includes tests for secret stripping, private-network-detail stripping, private-media exclusion, raw-transcript exclusion, private-path stripping, and live-device-claim prevention.

Until then, this spec defines the contract and guardrails, not a live emitter implementation.
