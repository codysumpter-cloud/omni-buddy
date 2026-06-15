# Omni Buddy AgentRQ and Monocle Orchestration Contract

Status: spec-only orchestration contract  
Owner repo: `codysumpter-cloud/omni-buddy`  
Related runtime repo: `codysumpter-cloud/buddy-agent`  
Related governance repo: `codysumpter-cloud/buddy-brain`  
Related receiver repo: `codysumpter-cloud/knowledge-vault`  
Reference systems: AgentRQ, Monocle

## Purpose

Omni Buddy is the multi-agent and multi-workspace orchestration layer. This document defines how Omni Buddy should coordinate AgentRQ-backed task workspaces and Monocle-backed observability without becoming the runtime executor, policy owner, or durable memory receiver.

This is not a live adapter yet. It is the routing and orchestration contract future adapters must follow.

## Integration intent

AgentRQ gives Omni Buddy a useful model for workspace-level task routing, approval visibility, task assignment, and supervisor-style multi-workspace control.

Monocle gives Omni Buddy a useful model for trace visibility, execution verification, and cross-agent debugging.

Together, they map to this stack shape:

```text
Omni Buddy
  routes work, selects workspace/agent, tracks cross-agent state
    ↓
AgentRQ-compatible control plane
  optional external task board, messages, approvals
    ↓
Buddy Agent / other workers
  execute guarded runtime tasks
    ↓
Monocle-compatible observability
  private trace capture and trace-based validation
    ↓
Knowledge Vault
  sanitized durable receipts only
```

## Responsibilities

Omni Buddy may:

- Route tasks to the correct AgentRQ workspace alias.
- Track task ownership across Buddy Agent, Buddy Brain, and other workers.
- Surface approval-required states to the operator.
- Summarize workspace status across agents.
- Link sanitized trace summaries to task receipts.
- Create cross-repo coordination records for Knowledge Vault.

Omni Buddy must not:

- Execute runtime tasks itself unless explicitly acting as a worker.
- Override Buddy Brain risk policy.
- Persist raw AgentRQ task messages.
- Persist raw Monocle traces.
- Store tokenized MCP URLs or OAuth credentials.
- Treat an external control plane as the source of truth for durable memory.

## Workspace routing model

Use stable public-safe aliases instead of raw workspace IDs.

```json
{
  "workspace_alias": "buddy-agent-runtime",
  "repo": "codysumpter-cloud/buddy-agent",
  "agent": "buddy-agent",
  "control_plane": "agentrq",
  "observability": "monocle",
  "knowledge_vault_source": "omni-buddy"
}
```

Workspace aliases should be safe to emit into Knowledge Vault. Tokenized URLs, private workspace IDs, and tenant IDs are not safe by default.

## AgentRQ supervisor mapping

If AgentRQ Supervisor/CoreMCP is configured, Omni Buddy may use it as a bird's-eye control plane for:

- listing workspaces
- selecting a workspace
- listing tasks
- checking task status
- assigning or reassigning tasks
- surfacing blocked tasks
- responding to permission requests only after Buddy Brain policy allows it

Permission updates remain high-risk operations and must preserve explicit approval records.

## Monocle trace mapping

Omni Buddy may request or read sanitized trace summaries for coordination.

Allowed summary fields:

- trace alias
- workflow name
- public task reference
- agent name
- status
- duration bucket
- validation result
- tool categories used
- approval pause count
- error class
- redaction status

Blocked summary fields:

- raw spans
- prompts
- full model outputs
- tool arguments
- tool outputs
- credentials
- local file paths
- browser session state
- private workspace identifiers
- unredacted user, tenant, or session IDs

## Cross-agent receipt event

When Omni Buddy emits a Knowledge Vault record, it should summarize orchestration rather than raw execution.

```json
{
  "source": "omni-buddy",
  "event_class": "task",
  "title": "Coordinated Buddy stack task through control-plane workflow",
  "summary": "Omni Buddy routed a task to Buddy Agent, observed approval status, and linked sanitized validation metadata.",
  "agents": [
    "omni-buddy",
    "buddy-agent"
  ],
  "control_plane": {
    "provider": "agentrq",
    "workspace_alias": "buddy-agent-runtime",
    "task_status": "completed"
  },
  "observability": {
    "provider": "monocle",
    "raw_trace_exported": false,
    "trace_summary_status": "sanitized"
  },
  "redaction": {
    "tokens": "excluded",
    "raw_prompts": "excluded",
    "private_paths": "excluded"
  }
}
```

## Routing safety defaults

- Prefer read-only status checks before mutation.
- Prefer smallest useful task scope.
- Require explicit approval before changing task permissions.
- Require explicit approval before broadening an agent's command permissions.
- Do not emit cross-workspace data unless the workspace alias is public-safe.
- Treat task attachments as private until separately reviewed.
- Keep raw trace storage outside Knowledge Vault.

## Implementation status

Current status: spec-only.

Omni Buddy is not AgentRQ-native or Monocle-native until a reviewed adapter exists with:

- local-only control-plane credentials
- workspace alias registry
- policy-aware task mutation
- sanitized trace summary reader
- Knowledge Vault schema validation
- redaction tests
- denied approval behavior tests
