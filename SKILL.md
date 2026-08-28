---
name: Manual-Trading-Advisory
description: >-
  Use this whenever the user wants a manual, non-crypto market scan,
  LONG/SHORT advisory, Hybrid M5 plan, risk size, ticket check, journal
  review, or strategy validation. Never log in to XTB or invent quotes.
  Load ONLY the files this router names. The running agent is the
  decision maker — do not spawn named subagents.
---

# Manual trading advisory (router)

**Load only what the question needs.** This file is the index. Do not read every skill. The running agent IS the decision maker; do not spawn named subagents.

All paths are next to this `SKILL.md`. Shared invariants live in `core.md`. Skill files are English. Open-ended scan replies default to Vietnamese.

## 1. Detect MODE (no extra files)

| Signal | MODE |
|---|---|
| “scan the market”, “có lệnh không”, refresh, breadth, open-ended session scan | `SCAN` |
| LONG/SHORT, READY_NOW, NO_TRADE, promote a candidate after a package is in thread | `DECISION` |
| size, heat, 0.25% cap, quantity, equity, risk budget | `RISK` |
| ticket, THAO TÁC, PLATFORM_TICKET_READY, BUY/SELL button check | `TICKET` |
| journal, append event, outcome review, AWAITING_USER_REPORT | `JOURNAL` |
| strategy spec, HYBRID_M5 research profile, validate, backtest gates | `STRATEGY` |
| full advisory, scan then decide, “what should I do now” | `SCAN` (orchestrator coordinates) |

“scan the market” / “có lệnh không” is `SCAN` plus the orchestrator.

## 2. Read map (mandatory)

After detection, **Read only these files** (in order). Stop. Do not browse unused skills.

| MODE | Files |
|---|---|
| `SCAN` / `REFRESH` | `core.md` → `skills/market-data-acquisition/SKILL.md` → `skills/trade-decision-guardrails/SKILL.md` → `skills/trade-orchestrator/SKILL.md` |
| `DECISION` | `core.md` → `skills/trade-decision-guardrails/SKILL.md` (+ the acquisition package if already in thread) |
| `RISK` / `SIZE` | `core.md` → `skills/portfolio-risk-manager/SKILL.md`; `skills/broker-account-snapshot/SKILL.md` **only if** the user supplied account data |
| `TICKET` / `CHECK` | `core.md` → `skills/order-execution-controls/SKILL.md` after `PLATFORM_TICKET_READY` |
| `JOURNAL` | `core.md` → `skills/trade-journal-review/SKILL.md` |
| `STRATEGY` / `VALIDATE` | `core.md` → `skills/trade-strategy-specification/SKILL.md` → `skills/strategy-validation/SKILL.md` |

The orchestrator at `skills/trade-orchestrator/SKILL.md` is the workflow coordinator for a full advisory. Follow it after the scan files when the user asked for a complete plan.

**Do not Read** unused skills or README while analyzing. This pack does not implement a code-change subagent. If you are changing this repo, edit files normally and run `python -m unittest discover -s tests -v`.

## 3. Then run

Follow `core.md` first. Public acquisition is read-only evidence for the calling agent. Crypto → `NO_TRADE`. Missing XTB is not a coverage skip. Lead with the plan or `NO_TRADE`, then the coverage audit.
