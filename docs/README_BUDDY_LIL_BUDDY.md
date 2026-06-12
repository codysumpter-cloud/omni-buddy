# Buddy + Lil' Buddy Omni Routing

Status: alpha contract stub
Owner: omni-buddy
Last verified: 2026-06-12

## What was added

Omni Buddy now has a documented local embodied/device route for the Buddy + Lil' Buddy standard.

Files:

- `docs/BUDDY_LIL_BUDDY_DEVICE_ROUTING.md` - voice, vision, sensor, transport, and device action route
- `schemas/buddy-device-event-envelope.schema.json` - local device event envelope schema

## Default device route

```text
Human/device event -> Buddy -> Lil' Buddy -> Buddy Review -> response/action
```

Buddy classifies intent and risk, delegates scoped observation or draft work, reviews the result, then decides whether to respond, escalate, or authorize an action.

## Runtime demo

The local no-secrets orchestration demo lives in `buddy-agent`:

```bash
buddy-demo "Draft a safe project note"
```

## Safety note

Voice, vision, sensors, transport changes, and physical actions must not bypass Buddy Review. External writes, account actions, posting, purchases, and money movement remain blocked by default unless a reviewed adapter and explicit approval exist.
