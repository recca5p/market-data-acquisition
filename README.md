# Trading skills pack

Portable skill pack for **any agent** (Cursor, Grok Bot, Claude Code, Codex, and others): manual, non-crypto trading research and risk planning. The user executes. The agent never logs in to a broker.

**How to start:** Read `SKILL.md`. That router detects MODE and names the only files to load. Skill files are English. Open-ended market-scan replies default to Vietnamese.

## Layout

```text
SKILL.md                              router (always)
core.md                               shared invariants
AGENTS.md                             short tool-agnostic contract
.cursor/rules/manual-trading.mdc      optional Cursor pointer at SKILL.md
skills/market-data-acquisition/       public data + coverage audit
skills/trade-decision-guardrails/     LONG / SHORT / NO_TRADE
skills/trade-orchestrator/            full advisory coordinator
skills/portfolio-risk-manager/        size and heat
skills/broker-account-snapshot/       only if the user supplied account data
skills/order-execution-controls/      ticket arithmetic after PLATFORM_TICKET_READY
skills/trade-journal-review/          append-only journal
skills/trade-strategy-specification/  versioned strategy spec
skills/strategy-validation/           research / validation gates
tests/                                Hybrid M5 + coverage-audit contracts
```

## Load graph

| User asks | Read |
|---|---|
| “scan the market” / “có lệnh không” | `SKILL.md` → `core.md` → acquisition → decision-guardrails → orchestrator |
| Decide LONG/SHORT | core + decision-guardrails (+ acquisition package already in thread) |
| Size / risk | core + portfolio-risk-manager; snapshot skill only if user supplied account data |
| Check a ticket | core + order-execution-controls after `PLATFORM_TICKET_READY` |
| Journal | core + trade-journal-review |
| Strategy / validate | core + trade-strategy-specification + strategy-validation |

## Hybrid M5 research mode

H1 defines the regime, M15 defines the setup, and only a completed M5 bar may trigger entry. Public M5 data delayed by one bar cannot produce `READY_NOW`; current XTB quotes and chart values must be supplied by the user.

Until validation, the profile caps risk at `0.25%`, requires explicit execution costs, rejects spread above `20%` of stop distance, and rejects total cost above `0.25R`.

Run the deterministic checks with:

```text
python -m unittest discover -s tests -v
```

## Repository scope

The repository tracks reusable skill source files only. Runtime artifacts such as temporary PDFs/images, Python caches, and local trade journal history (`trade-history/*.jsonl`) are intentionally ignored.

## Related

Same owner, different job. Do not mix loaders or time horizons.

- Long-term accumulation (1–2y quality-at-a-discount): https://github.com/recca5p/quality-at-a-discount
- Discover both under GitHub topic [`skills`](https://github.com/search?q=topic%3Askills+user%3Arecca5p) on `recca5p`.
