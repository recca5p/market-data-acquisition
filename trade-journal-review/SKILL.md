---
name: trade-journal-review
description: Create compact append-only records for proactive public scans, ranked candidates, manual LONG/SHORT plans, optional platform translation, NO_TRADE cases, and outcomes later reported by the user. Derive controls by exact session and instrument so expired proposals and unrelated basis incidents do not block new opportunities. Use for performance, conversion, missed-setup, rule-adherence, and data-quality review; never assume entry, invent fills, or rewrite the original plan.
---

# Manual Trade Journal Review

## Mission

Preserve what the agent proposed and what the user later reports. Keep the original trade card frozen so outcome review is not distorted by hindsight.

Read [references/journal-schema.md](references/journal-schema.md) before recording or reviewing.

## Recording Rules

Create stable IDs and link acquisition, optional strategy/validation, decision, risk plan, manual ticket check, user entry report, user exit report, and review records.

Use append-only events. Corrections must point to the original event and
explain the change. Store source timestamps and normalize observation/report
times to ICT. Bind every control-bearing event to a `session_id`; bind basis
incidents to account alias, broker symbol, and contract.

Never infer that the user entered a trade. A public scan or directional plan is
`SCAN_RECORDED` or `CANDIDATE_PROMOTED`, not an assumed trade. Use
`AWAITING_USER_REPORT` only after a platform-translated ticket or an explicit
user action instruction has been presented. It remains awaiting until the user
reports an entry or says it was skipped.

When the workspace contains `trade-history/manual-advisory-history.jsonl`,
append one compact JSON object per line. Never rewrite, reorder, or delete prior
events. Keep unknown actual prices, quantity, costs, and P&L null.

Do not append another identical `WAIT_FOR_DATA` or blocker event when its
instrument, session, missing fields, and source state have not changed. Record
a new event only for a material refresh, candidate promotion/demotion, decision
change, ticket translation, user report, or control-state transition.

## Workflow

### 1. Record the Frozen Proposal

Record:

- instrument and public reference basis;
- sources, timestamps, stated delay, and data-quality flags;
- framework status and optional strategy/validation version;
- decision, supporting/conflicting evidence, and confidence label;
- entry trigger/zone, stop-loss, invalidation, targets/exits, expiry, and cancel conditions;
- reward-to-risk, cost assumptions, indicative quantity or null;
- user verification requirements.

Record `NO_TRADE` and `WAIT_FOR_DATA` cases to reduce selection bias.
Record baseline scans as one compact `SCAN_REFRESH` event and the ranked
shortlist as `CANDIDATE_PROMOTED` events. Do not create one blocker record per
unchanged symbol.

### 2. Await the User Report

For a translated manual ticket, set
`journal_status: AWAITING_USER_REPORT`. When the user reports back, append one
of:

- `USER_SKIPPED`;
- `USER_ENTERED`;
- `USER_UPDATED_POSITION`;
- `USER_EXITED`;
- `USER_OUTCOME_REPORTED`.

Ask only for missing fields needed for review: actual instrument, side, entry/exit times and prices, quantity, fees/financing when known, whether SL/TP/manual exit occurred, and notes.

### 3. Record Actuals Without Invention

Treat user-reported values as reported facts and label their source `USER_REPORT`. Do not replace them with a public quote.

If the user provides incomplete results, keep P&L, R multiple, or costs null rather than estimating silently. Record later corrections as new events.

### 4. Review the Outcome

Compare actual entry with the proposed trigger/zone, actual exit with SL/TP/expiry rules, and actual result with the original risk plan.

Separate:

- directional signal quality;
- timing/entry deviation;
- manual execution deviation;
- cost/slippage effect when supplied;
- adherence to stop, target, expiry, and cancel rules.

If a reported broker trigger, fill, or stop cannot be reconciled with the
public-reference price path, record
`BASIS_INCIDENT_LOCK_ACTIVE` for that exact account alias, broker symbol, and
contract. Do not label the cause as spread, slippage, broker error, or user
deviation without evidence. Ask the user for current XTB symbol, bid, ask,
spread, quote time, and contract basis before another numeric ticket for the
affected contract. Record them as `USER_PROVIDED_REALTIME`; never access XTB
or a broker connector. Continue public-reference analysis and other
instruments. A single stopped trade must not be used to reject an instrument
or strategy class.

### 4.5 Derive Current-Session Controls

Build session loss counts only from explicit user-reported stopped outcomes
whose `session_id` matches the active session. Expired or unreported proposals
remain missing-report records but do not count as losses or block a new
session. Reset session-local stop and override states at the next session
boundary; preserve daily and weekly realized-loss controls separately.

### 5. Review Aggregates

Group by framework/strategy version, instrument, side, horizon, regime,
session, source, and delay. Report after-known-cost expectancy, win/loss
distribution, drawdown, realized R, adherence, skipped plans, stale-data rate,
missing-report rate, READY_NOW frequency, candidate-to-ticket conversion, and
qualified setups missed because platform translation arrived too late.

Label small samples and unvalidated discretionary plans clearly. Route systematic drift back to `$strategy-validation` when that optional workflow is in use.

## Output

For a scan or public proposal, return its immutable journal ID and
`SCAN_RECORDED` or `CANDIDATE_PROMOTED`. For a translated ticket, return
`AWAITING_USER_REPORT`. For a user report, return recorded facts, missing
fields, computed outcome metrics that are supportable, deviations from the
frozen plan, and the next review action.
