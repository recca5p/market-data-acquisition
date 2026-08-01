---
name: portfolio-risk-manager
description: Proactively calculate bounded public-reference risk geometry for a non-crypto LONG or SHORT setup, then add XTB quantity only from current real-time and account inputs directly supplied by the user. Use before a user-executed Market or explicitly requested Stop/Limit ticket under the planned USD 2,000 profile. Never access XTB, call a broker API/connector, infer missing platform fields, place, or authorize an order.
---

# Manual Trade Risk Planner

## Mission

Check whether a proposed manual trade in a supported market has bounded and internally consistent risk. Provide an indicative quantity only when the required inputs are explicit. Never size a crypto trade.

Read [references/risk-policy.md](references/risk-policy.md) before evaluating.
For this user's account, also read
[references/account-risk-profile.md](references/account-risk-profile.md).
Use [scripts/calculate_position_size.py](scripts/calculate_position_size.py)
only when every required sizing input is supplied.

## Required and Optional Inputs

Require for public-reference risk geometry:

- current `session_id`, session-scoped basis-incident status, and consecutive
  reported losses for that same session;
- supported asset class with a non-crypto primary underlying/reference;
- `LONG` or `SHORT`, entry trigger/zone, finite stop-loss, invalidation, target/exit, expiry, and instrument basis;
- public reference price, timestamp, delay, and cost assumptions.
- `entry_timing_mode`, strategy validation status, and the active timing
  profile's spread-to-stop, total-cost-R, and research-risk limits.

Treat as optional unless the account-risk profile is being used:

- account equity and available risk budget;
- current portfolio exposures and daily P&L;
- broker-specific tick, quantity, multiplier, margin, spread, and borrow data.
- platform bid/ask, displayed quantity, pip/point value, fees, swap, and ticket type captured from a user screenshot.

Missing optional inputs must not block the directional plan. Instead return `PLAN_PARTIAL`, leave quantity/account loss null, and list what the user must verify.

Spread, round-trip fees, slippage, and financing/borrow buffers are
decision-critical for `HYBRID_M5`, not optional zeros. If any is missing,
return `PLAN_PARTIAL` and do not calculate quantity or net reward-to-risk.

Treat the USD 2,000 balance as planned until current XTB text, screenshot, or
account export supplied by the user confirms it. Never
calculate a USD 2,000-sized quantity from the user's intention to deposit.

## Workflow

### 0. Apply the Asset-Class Gate

If the instrument's primary underlying/reference is a cryptoasset, return
`NO_TRADE` with
`rejection_reason: UNSUPPORTED_ASSET_CLASS_CRYPTO`. Leave quantity, leverage,
monetary risk, entry, stop, and targets null. Do not run the sizing script.

### 0.5 Apply Session-Scoped Controls

Apply loss counts only when their `session_id` matches the proposed trade. A
loss or stop flag from an earlier Asia, Europe, U.S., or overnight session does
not carry into a new session.

Scope a basis incident to its broker symbol, contract, and account alias. While
that lock is active, continue to calculate clearly labelled non-executable
public-reference entry/stop/target geometry. Return `PLAN_PARTIAL`, keep
platform ticket prices, quantity, and monetary account risk null, and require
reconciliation only before platform translation for the affected contract.

After one reported stop in the current session, cap the next eligible risk at
`0.5%` of confirmed equity. After two consecutive losses in that session,
reject further trades until the next session.

### 1. Validate Price Risk

For `LONG`, require stop below the intended entry and targets above it. For `SHORT`, require stop above entry and targets below it.

Reject an absent stop, zero/negative stop distance, invalid price, expired signal, or target on the wrong side. Treat gap and slippage risk as capable of exceeding the stop.

### 2. Calculate Reward-to-Risk

Calculate gross price risk from entry to stop and gross reward to each target. Include estimated spread, fees, slippage, financing, and borrow cost when known.

Return both gross and estimated net reward-to-risk. If costs are unknown, label net reward-to-risk unavailable rather than assuming zero cost.

Apply the active account profile thresholds. Reject estimated net
reward-to-risk below `1.5`, restrict risk to at most `0.5%` from `1.5` through
`1.79`, and use normal size only at `1.8` or better. Prefer a target near `2R`.

For `HYBRID_M5`, calculate `spread_to_stop_fraction`, `total_cost_r`, and
break-even win rate. Reject spread-to-stop above `0.20` or total cost above
`0.25R`. Until the exact strategy version is `ADVISORY_VALIDATED`, cap risk at
`0.25%` of confirmed equity even when the base account profile permits more.

### 3. Calculate Optional Quantity

Run the bundled script only when all of these are known:

- `realtime_execution_data_source: USER_PROVIDED_REALTIME` and
  `xtb_interaction_allowed: false`;
- equity or explicit risk amount;
- risk fraction when equity-based;
- entry, stop, value per price unit, quantity step, and minimum quantity;
- remaining daily and portfolio risk budgets;
- remaining correlated-exposure budget;
- conservative cost buffers.
- for `HYBRID_M5`, current platform spread, an explicit statement of whether
  spread is already included in entry/exit geometry, the strategy validation
  status, and the research risk cap.

When any field is missing, return the formula and `indicative_quantity: null`.
Do not downgrade a valid public-reference plan to `NO_TRADE` merely because
the user has not supplied an XTB quote, account snapshot, or contract value. A public
contract specification may support an estimate only when it matches the
user's actual instrument; otherwise require manual verification.

Never round quantity upward. Label any result `INDICATIVE_ONLY`.

If the user has selected a platform quantity and the matching platform value per price unit is visible, calculate the estimated monetary loss to the stop and gain to each target for that selected quantity. Label the quantity `USER_SELECTED_NOT_APPROVED`; this is an explanation of the displayed ticket, not account-risk approval.

Do not treat displayed margin, contract value, or buying power as maximum loss. For stop-defined risk, use price distance × matching value per price unit × quantity, then add known spread, fee, slippage, and financing buffers. State which costs remain excluded.

For an activated USD 2,000 profile, use USD 15 as the normal per-trade risk
budget and USD 20 as a hard ceiling. Cap aggregate worst-case open risk at USD
40 and correlated U.S.-equity risk at USD 30. Deduct existing positions and
pending orders before sizing.

Reuse a valid full account snapshot throughout its named session. Request a
compact delta refresh only after a fill, exit, order change, material P&L or
margin change, snapshot expiry, or an explicit user report that account state
changed. Do not require a full account screenshot before every candidate.

### 4. Return the Plan

Use:

- `PLAN_READY` when direction, entry, stop, targets, expiry, and reward/risk are valid;
- `PLAN_PARTIAL` when the price plan is valid but costs, quantity, or account-specific exposure is unknown;
- `NO_TRADE` when price risk is invalid or an explicit user/strategy threshold fails.

Quantity is not required for `PLAN_READY` or `PLAN_PARTIAL`.
Use `execution_state: NEEDS_USER_REALTIME` when only current user-provided XTB
quote or contract mapping is missing. Ask for the minimal values; never attempt
to retrieve them from XTB.

### 5. Hand Off

Send the manual plan to `$trade-orchestrator` and `$trade-journal-review`. Do not send anything to a broker and do not describe a suggested quantity as approved.

## Output

Return status, decision/risk IDs, confirmed or planned equity status, ticket
mode/type, entry or trigger, stop, stop distance, invalidation, targets,
gross/net reward-to-risk, estimated loss at stop, estimated net profit at
target, risk fraction, remaining portfolio/daily/correlated budgets, expiry and
time stop, spread-to-stop fraction, total-cost-R, break-even win rate,
indicative quantity or null, quantity source, sizing formula,
missing inputs, gap/slippage warnings, user verification checklist, and journal
reference.
