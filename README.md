# Trading Skills Bundle

This repository contains a project-scoped Codex multi-agent and skills bundle
for manual, non-crypto trading research, implementation, and risk planning.

## Codex Layout

```text
AGENTS.md                         Sol behavior for the primary thread
.codex/config.toml               Project model and multi-agent settings
.codex/agents/terra.toml         Workspace-write implementation subagent
.codex/agents/luna.toml          Read-only market-data subagent
.agents/skills/<name>/SKILL.md   Repo-scoped skills discovered by Codex
```

The project must be trusted for Codex to load `.codex/config.toml`. Start a new
Codex session after changing agent configuration so the instruction and agent
layers are reloaded.

Reasoning profile: Sol uses `ultra`; Terra and Luna use `max`. Sol owns
delegation, while Terra and Luna keep a flat hierarchy and return escalations
to Sol.

## Skills

- `sol` — decision, architecture, planning, and final review
- `terra` — implementation, debugging, refactoring, and integration
- `luna` — permitted public market-data acquisition and normalization
- `broker-account-snapshot`
- `market-data-acquisition`
- `order-execution-controls`
- `portfolio-risk-manager`
- `strategy-validation`
- `trade-decision-guardrails`
- `trade-journal-review`
- `trade-orchestrator`
- `trade-strategy-specification`

## Agent Roles

```text
Luna (subagent) -> public market data and normalized acquisition package
  -> Sol (primary thread) -> architecture, guardrails, decision, and plan
  -> Terra (subagent) -> implementation, integration, tests, and migrations
  -> Sol (primary thread) -> acceptance review and user-facing handoff
```

Use `$luna` when the task is primarily market-data collection, `$terra` when
the task is implementation or integration, and `$sol` when the task requires
reasoning, a decision, a plan, or a final review. The existing domain skills
remain the source of truth for acquisition, decision guardrails, risk, ticket
checks, strategy validation, and journaling.

Each skill lives under `.agents/skills/` and contains a `SKILL.md` file. A skill
may also include `references/`, `agents/`, or `scripts/` used by that workflow.

## Hybrid M5 Research Mode

The bundle includes a versioned `HYBRID_M5` research profile. H1 defines the
regime, M15 defines the setup, and only a completed M5 bar may trigger entry.
Public M5 data delayed by one bar cannot produce `READY_NOW`; current XTB
quotes and chart values must be supplied by the user.

Until validation, the profile caps risk at `0.25%`, requires explicit
execution costs, rejects spread above `20%` of stop distance, and rejects total
cost above `0.25R`.

Run the deterministic checks with:

```text
python -m unittest discover -s tests -v
```

## Repository Scope

The repository tracks reusable skill source files only. Runtime artifacts such
as temporary PDFs/images, Python caches, and local trade journal history are
intentionally ignored.
