# Buddy + Lil' Buddy Device Routing

Status: alpha contract stub
Owner: omni-buddy
Last verified: 2026-06-12

## Purpose

`omni-buddy` owns local embodied/device integration for Buddy. This document defines how voice, vision, sensor, transport, and device tasks route through the default Buddy + Lil' Buddy standard.

Default route:

```text
Human/device event -> Buddy -> Lil' Buddy -> Buddy Review -> response/action
```

This extends the existing runtime boundary. It does not replace `agent.py`, transport contracts, council mode, or runtime health checks.

## Role split

### Buddy

Buddy must:

- classify the device event and user intent
- decide whether the task is observation, response, or action
- create a scoped Lil' Buddy task envelope
- review worker results before speech, display output, transport action, or physical action
- escalate before risky device, network, account, or physical-world effects
- produce the final response/action decision

### Lil' Buddy

Lil' Buddy may:

- transcribe or summarize a voice event
- inspect a local vision caption or camera observation reference
- read product-safe runtime state
- prepare a draft response
- prepare a proposed device action for review

Lil' Buddy must not:

- speak directly to the human without Buddy Review
- actuate hardware without approval
- bypass camera/microphone privacy gates
- change transport/network state outside an approved contract
- perform account, message, purchase, or posting actions

## Event classes

| Event class | Example | Default safety class | Review rule |
|---|---|---|---|
| `voice_intent` | Wake word + spoken prompt | medium | Buddy reviews transcript and response |
| `vision_observation` | Camera caption or object summary | high | Buddy checks privacy and intent |
| `runtime_status` | Transport mode or health query | low | Buddy can answer after review |
| `device_action_draft` | Turn display on, play sound, change mode | high | Buddy escalates before action |
| `external_action_draft` | Send message, post, API write | blocked by default | Human approval and audited adapter required |

## Required device event envelope

Use `schemas/buddy-device-event-envelope.schema.json` for local events.

Minimum fields:

```json
{
  "schema_version": "buddy.device_event.v1",
  "event_id": "event-001",
  "modality": "voice",
  "device_source": "raspberry-pi-local",
  "user_intent": "What the human/device event requested",
  "safety_class": "medium",
  "observation_refs": [],
  "proposed_action": null,
  "review_status": "pending"
}
```

## Routing examples

### Voice question

```text
Wake word -> speech capture -> transcript ref -> Buddy intent capture -> Lil' Buddy drafts answer -> Buddy Review -> TTS response
```

### Vision request

```text
Camera request -> local caption/observation ref -> Buddy privacy/risk check -> Lil' Buddy summarizes observation -> Buddy Review -> spoken/display response
```

### Device action

```text
Human asks for local action -> Buddy classifies high risk -> Lil' Buddy prepares proposed action -> Buddy Review -> approval gate -> device adapter action or refusal
```

## Guardrails

- Camera and microphone events require explicit local intent and should store references, not raw private media, unless a reviewed adapter requires otherwise.
- Physical actions are high risk until proven harmless and reversible.
- Transport changes must remain consistent with `docs/TRANSPORT_CONTRACT.md`.
- Runtime capability claims must remain consistent with `docs/BUDDY_RUNTIME_BOUNDARY.md`.
- External writes, account actions, posting, purchases, or money movement are blocked by default.
- Every meaningful action should produce a product-safe receipt.

## Integration with the broader standard

| Concern | Owner |
|---|---|
| Durable standard | `knowledge-vault/99-System/Buddy Standards/` |
| Governance | `buddy-brain/context/council/BUDDY_LIL_BUDDY_ORCHESTRATION.md` |
| Local runtime scaffolds | `buddy-agent/src/buddy_agent/orchestration/` |
| Device event routing | `omni-buddy/docs/BUDDY_LIL_BUDDY_DEVICE_ROUTING.md` |

## Future implementation hook

A future adapter should transform raw local events into the device event envelope, then hand the envelope to Buddy before any worker execution or device action.
