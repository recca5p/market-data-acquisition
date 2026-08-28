---
name: order-execution-controls
description: Validate arithmetic, entry zone, platform mapping, confirmed-equity risk, monetary target, portfolio heat, and internal consistency of a translated manual ticket using only current XTB values supplied by the user. Use after a READY_NOW public plan and before user entry. REQUEST_USER_REALTIME is not yet a ticket. Never access XTB, call an API/connector, place, modify, or cancel an order.
---

# Manual Trade Card Check

## Mission

Check a proposed manual ticket for a supported market and return errors or warnings. Crypto tickets are invalid. This skill has no execution capability.

Read [references/execution-policy.md](references/execution-policy.md) before checking a plan. Use [scripts/validate_order.py](scripts/validate_order.py) for deterministic arithmetic.

## Workflow

### 1. Bind the Plan

Call this skill only after `execution_state: PLATFORM_TICKET_READY` and verify
that every current XTB field has `source: USER_PROVIDED_REALTIME`. If the
upstream action is `REQUEST_USER_REALTIME` or `NEEDS_USER_REALTIME`, return
control to `skills/trade-orchestrator/SKILL.md` without treating the public plan as an invalid
ticket. Never attempt to fetch the fields from XTB.

Require decision ID, risk-plan ID, current `session_id`, scoped
basis-incident status, asset class, instrument/reference basis, side, entry
price used for calculation, stop-loss, at least one target, current evaluation
time, and signal expiry.

For `HYBRID_M5`, additionally require strategy validation status, confirmed
H1/M15 alignment, `trigger_timeframe: M5`, completed-trigger timestamp, maximum
trigger age, current user-provided quote timestamp, maximum quote age,
platform spread, maximum spread-to-stop fraction, total estimated cost, total
cost-R limit, and research risk cap.

Accept optional order mode/type, broker symbol, platform bid/ask, platform quote time, valid Market-entry zone, tick size, quantity, quantity source, quantity step, pip/point value, reference price, maximum price deviation, estimated costs, account-profile status, confirmed equity, estimated monetary loss/profit, existing open risk, risk caps, and minimum reward-to-risk.

### 2. Check Direction and Levels

First reject a matching unresolved `BASIS_INCIDENT_LOCK_ACTIVE` for the same
account alias, broker symbol, and contract with
`MANUAL_TICKET_INVALID` and
`PLATFORM_BASIS_RECONCILIATION_REQUIRED`. Leave the user-editable platform
ticket empty. Do not apply a lock from another instrument or a prior session.

First reject crypto spot, perpetuals, futures, options, CFDs, and
crypto-tracking ETPs/ETFs with `MANUAL_TICKET_INVALID` and error
`UNSUPPORTED_ASSET_CLASS_CRYPTO`. Do not return user-editable prices, quantity,
or ticket actions for a prohibited instrument.

Require:

- `LONG`: stop below entry and targets above entry;
- `SHORT`: stop above entry and targets below entry;
- positive finite prices and nonexpired signal;
- quantity aligned to the supplied step when quantity is present;
- price alignment to the supplied tick when tick size is present.

When platform mapping is supplied, also require:

- `MARKET` maps to `MARKET`;
- `BUY_STOP` matches `LONG` and triggers above ask;
- `SELL_STOP` matches `SHORT` and triggers below bid;
- `BUY_LIMIT` matches `LONG` and triggers below ask;
- `SELL_LIMIT` matches `SHORT` and triggers above bid;
- platform bid does not exceed ask.

Calculate reward-to-risk from the same entry and stop. Do not silently change a level to make it valid.

Reject a Market ticket when its executable side has moved outside the supplied
valid-entry zone. Reject a ticket below its supplied minimum estimated net
reward-to-risk.

For `HYBRID_M5`, reject a stale quote, stale or incomplete M5 trigger,
unconfirmed H1/M15 alignment, spread-to-stop above `0.20`, total execution cost
above `0.25R`, or an unvalidated risk cap above `0.25%`. Missing costs are an
error because net reward-to-risk cannot be checked safely.

When the account-risk fields are supplied, reject a ticket whose estimated loss
exceeds the single-trade cap or whose existing plus proposed loss exceeds the
portfolio-heat cap. Do not accept `RISK_CALCULATED` quantity for a planned
profile that has not been confirmed by a fresh account snapshot.

### 3. Check Delayed-Data Implications

Compare the public observation time/delay and current reference price when supplied. A material move does not authorize the agent to update the entry automatically.

Return a warning requiring manual reconfirmation. Reject only when the original conditional trigger or expiry is no longer valid.

### 4. Return Manual-Only Status

Return `MANUAL_TICKET_VALID`, `MANUAL_TICKET_WARNING`, or `MANUAL_TICKET_INVALID`.

Always set:

- `agent_may_submit_orders: false`;
- `broker_connection_required: false`;
- `xtb_interaction_allowed: false`;
- `user_platform_verification_required: true`.

Do not produce broker, acknowledgement, fill, or execution statuses.

## Output

Return the user-editable platform ticket block first, followed by frozen
levels, computed reward-to-risk, confirmed equity status, estimated monetary
loss/net profit, risk fraction, remaining heat, optional quantity checks,
spread-to-stop fraction, total-cost-R, break-even win rate, errors, warnings,
public-data delay, and exact fields the user must verify.
