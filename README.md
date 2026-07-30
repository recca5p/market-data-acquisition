# Trading Skills Bundle

This repository contains a Codex skills bundle for manual, non-crypto trading research and risk planning.

## Skills

- `broker-account-snapshot`
- `market-data-acquisition`
- `order-execution-controls`
- `portfolio-risk-manager`
- `strategy-validation`
- `trade-decision-guardrails`
- `trade-journal-review`
- `trade-orchestrator`
- `trade-strategy-specification`

Each skill directory contains a `SKILL.md` file and may include `references/`, `agents/`, or `scripts/` used by that skill.

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

The repository tracks reusable skill source files only. Runtime artifacts such as temporary PDFs/images, Python caches, and local trade journal history are intentionally ignored.
