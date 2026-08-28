---
name: broker-account-snapshot
description: Parse only XTB/account information that the user directly supplies by text, screenshot, or export into a reusable current-session sizing snapshot, including equity, available funds, open and pending risk, real-time quote, quantity, point value, fees, swap, specifications, and margin. Never connect to XTB, use credentials, call a broker API, control a browser/app, or retrieve account data independently.
---

# Broker Account Snapshot

## Mission

Optionally convert user-supplied XTB/account data into a point-in-time context
for manual sizing. Do not retrieve data, make a trade decision, or mutate
broker state. The core public advisory workflow must work without this skill.

Read [references/account-snapshot-schema.md](references/account-snapshot-schema.md) before collecting data.

## Access Rules

Use only text, screenshots, or exports directly supplied by the user in the
conversation. Set `xtb_interaction_allowed: false` and
`source: USER_PROVIDED_REALTIME`. Never use an API, connector, login,
credential, authenticated browser state, desktop control, or independent XTB
lookup.

If the user has not supplied the required fields, return
`OPTIONAL_UNAVAILABLE` and list the minimal fields to ask for. Do not block
`skills/trade-orchestrator/SKILL.md`, and never substitute an assumed balance, position,
margin, quote, or permission.

## Snapshot Workflow

### 1. Bind Identity and Time

Resolve the exact account alias, environment (`paper` or `live`), broker,
venue, symbol, contract, account currency, and current `session_id`. Generate a
`snapshot_id` and mark the snapshot as `FULL_SESSION` or `DELTA_UPDATE`.

Record the quote/account time visible in the user's data, the user's report
time when available, local observation time in ICT, and source status. Do not
invent provider latency. Mask identifiers in user-visible output.

### 2. Collect Account State

Extract only when visibly or explicitly supplied by the user:

- cash, equity/net liquidation value, available funds, buying power, initial/maintenance margin, and margin-call state;
- realized and unrealized P&L;
- positions with quantity, side, average price, current mark, currency, and instrument identity;
- working, pending, partially filled, rejected, and recently completed orders;
- trading permissions, restrictions, and risk-limit state.

### 3. Collect Optional Instrument Context

Extract bid, ask, last, quote time, market/session status, halt state, and
stated delay only when the user supplies them. Record spread and depth only
when visible in the supplied XTB data.

Collect tick size, quantity step, minimum quantity, contract multiplier or value per price unit, settlement currency, trading hours, price bands, expiration/roll, margin schedule, and supported order types.

From a ticket screenshot, capture only fields that are visibly stated: supported Market/Stop-Limit tabs, order type, bid/sell and ask/buy prices, selected quantity, contract value, displayed margin, spread, fees, pip/point value, swap, and whether stop-loss/take-profit inputs exist. Do not infer hidden account equity, available risk, tick size, or quantity step.

For a `HYBRID_M5` refresh, also capture the visible chart timeframe, current
quote receipt time, latest completed M5 bar open/close time and OHLC, current
in-progress bar state, and countdown when shown. Do not infer a completed bar
from candle color or screen position; if completion time is not defensible,
mark the trigger incomplete.

From an account/positions screenshot, also capture visibly stated account
equity or trading value, available funds, margin used, margin ratio, open
positions, pending orders, entry, current mark, stop, target, and displayed
P&L. Calculate remaining stop-defined risk only when quantity and value per
price unit are known from the same instrument or ticket.

For short sales, collect locate/borrow availability, estimated borrow fee, recall constraints, and any short-sale restriction. For derivatives, collect contract expiry, settlement, funding, and liquidation-relevant fields.

### 4. Validate and Reconcile

Verify that positions and working orders reconcile with the target instrument. Mark stale, missing, contradictory, permission-denied, and unsupported fields.

Set `manual_risk_context_ready: true` only when all user-requested sizing fields are present and within their maximum age.

Do not keep readiness true after the snapshot expires.

Reuse a `FULL_SESSION` snapshot for later candidates in the same named session
while it remains valid. Invalidate it after a fill, exit, working-order change,
material P&L/margin change, explicit user account-state update, or session end.
After invalidation, collect only the changed account fields with
`DELTA_UPDATE` when the existing baseline identity and unaffected fields remain
reliable. A compact user confirmation that nothing changed may refresh the
no-change state; do not demand a duplicate full screenshot.

For `user-cfd-usd-2000-v1`, mark the profile active only after current
user-supplied text, screenshot, or export shows equity of at least USD 2,000.
A statement that the user intends to deposit does not activate it.

### 5. Hand Off

Send the optional immutable snapshot to `skills/portfolio-risk-manager/SKILL.md`. Missing snapshot data leaves indicative quantity null; it does not invalidate entry, stop, or targets.

Log status and masked identifiers through `skills/trade-journal-review/SKILL.md`.

## Output

Return:

1. `Snapshot status:` `COMPLETE`, `PARTIAL`, or `OPTIONAL_UNAVAILABLE`.
2. `Identity and timing:` masked account, paper/live environment, instrument, snapshot ID, provider time, ICT time, and latency.
3. `Account state:` balances, margin, P&L, positions, and working orders.
4. `Market, instrument, and ticket state:` quote, session, visible ticket fields, permissions, specifications, and short/derivative details.
   Include visible completed-M5 trigger data when `HYBRID_M5` is requested.
5. `Validation:` missing, stale, contradictory, unsupported, and reconciliation flags.
6. `Readiness:` optional manual-sizing readiness, session scope, expiry, and
   invalidation conditions.
7. `Handoff:` risk-manager reference and
   `source: USER_PROVIDED_REALTIME`; never include a credential.
