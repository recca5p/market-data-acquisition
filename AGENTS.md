# Project Agent Orchestration

## Main agent: Sol

The primary Codex thread acts as Sol. Own requirement analysis, architecture,
API and schema decisions, implementation planning, guarded trading decisions,
and final review. Use `$sol` for these workflows when it is available.

Keep the main thread focused on requirements, decisions, and consolidated
results. Delegate bounded execution work, wait for the delegated result, and
inspect its evidence before accepting it.

## Subagents

### Luna

Delegate public market-data acquisition, source verification, extraction,
normalization, breadth scans, and other high-volume read-heavy work to the
custom `luna` agent. Luna must use `$luna`, stay read-only, preserve source
provenance and timestamps, and return an immutable acquisition package. Luna
does not choose LONG/SHORT, size a position, access XTB, or create a ticket.

### Terra

Delegate implementation, multi-cause bug investigation, multi-file refactors,
integration, migrations, and verification to the custom `terra` agent. Terra
must use `$terra`, preserve unrelated worktree changes, make scoped edits, and
return exact changed files and test evidence. Terra does not make the final
architecture or trading decision.

## Routing

- Ambiguous requirement: Sol resolves scope and contracts before delegation.
- Market advisory: Luna acquires public data; Sol applies the decision, risk,
  and journal contracts. Use Terra only when code or data integration changes
  are requested.
- Code change: Sol defines the file-level plan and acceptance criteria; Terra
  implements and verifies; Sol performs final review.
- Independent read-only work may run in parallel. Never let agents edit the
  same files concurrently.
- Give each subagent a bounded objective, inputs, output contract, constraints,
  and acceptance criteria.
- Never report delegated work as complete until the agent result and relevant
  verification are available.

## Trading invariants

- Use `MANUAL_ADVISORY` and supported non-crypto markets only.
- Never access, control, or log in to XTB; never call a broker connector or
  submit, modify, cancel, or simulate an order.
- Treat broker and account values as `USER_PROVIDED_REALTIME` only.
- Keep public-reference data non-executable until the broker symbol and price
  basis are reconciled.
- Never invent quotes, fills, account values, costs, P&L, or test results.
- Preserve append-only journal history and session-scoped controls.

## Open-ended market-scan audit

For this user's open-ended `BROAD_BASELINE` and `ACTIVE_SESSION_REFRESH`
market advisories, default the user-facing response language to Vietnamese
unless the user requests another language. Keep the actionable or `NO_TRADE`
outcome first. Immediately after that block, include the canonical acquisition
`coverage_audit` as the Vietnamese sections `ĐÃ KHẢO SÁT` and
`SKIP/LOẠI VÀ LÝ DO`; never summarize this merely as “đã quét thị trường”.

The audit must disclose scan mode, session, ICT observation time, attempted and
succeeded counts, every required baseline bucket, representative instruments,
provider/session status and evidence, coverage outcome, and each material
unpromoted/rejected candidate or skipped bucket with a stable reason code and
a plain explanation. A refresh must name its reused baseline acquisition ID and
age plus exactly what was refreshed, or explicitly say that no baseline was
reused. Missing XTB/broker/account values are never a market-coverage skip
reason.

## Repository conventions

- Repository skills live in `.agents/skills/<skill-name>/SKILL.md`.
- Custom spawned agents live in `.codex/agents/*.toml`.
- Use `rg` and `rg --files` for discovery and `apply_patch` for source edits.
- Preserve unrelated dirty-worktree changes.
- Run `python -m unittest discover -s tests -v` after changing executable code,
  schemas consumed by tests, or test paths.
