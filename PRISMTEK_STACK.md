# Prismtek Buddy Stack

Omni Buddy is the **local and device runtime** of the Prismtek Buddy Agent Platform. It owns voice, vision, local models, device transport, and embodied interaction—not durable project memory, central policy, or guarded cloud execution.

The machine-readable declaration is [`prismtek.component.json`](prismtek.component.json). The canonical topology is maintained by BUAP.

## Runtime boundary

Omni Buddy consumes compiled BUAP policy, verified Buddy Agent receipts, and KnowledgeVault context. Device actions should emit sanitized events and must not treat local model output as verified work without the same evidence and receipt discipline used elsewhere in the stack.

```text
BUAP policy + KnowledgeVault context
              ↓
          Omni Buddy
              ↓
voice / vision / device action
              ↓
sanitary device event + Buddy Agent receipt
```
