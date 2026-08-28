---
name: strategy-validation
description: Validate a fully specified repeatable non-crypto trading strategy using leakage controls, cost-aware backtests, out-of-sample and walk-forward tests, robustness analysis, opportunity-throughput and conversion metrics, probability calibration, paper observation, and ongoing drift review. Use for systematic strategy development or changes; distinguish a genuine absence of setups from workflow/platform blockers. It is optional for one-off manual advice and never authorizes automated alerts or orders.
---

# Strategy Validation

## Mission

Decide whether an exact repeatable supported strategy version is `REJECTED`, `RESEARCH_ONLY`, `FORWARD_OBSERVATION`, `SUSPENDED`, or `ADVISORY_VALIDATED`. Validation never authorizes or submits an order and is not a prerequisite for a clearly labelled one-off discretionary manual plan. Never backtest or validate a crypto strategy.

Read [references/validation-protocol.md](references/validation-protocol.md) before testing.

## Validation Workflow

### 0. Apply the Asset-Class Gate

If the strategy's primary underlying/reference is a cryptoasset, including
crypto spot, perpetuals, futures, options, CFDs, or crypto-tracking ETPs/ETFs,
return `Validation status: REJECTED` with
`UNSUPPORTED_ASSET_CLASS_CRYPTO`. Do not acquire data, run simulations, compute
performance metrics, or promote the strategy.

### 1. Freeze the Strategy

Require a versioned specification defining:

- universe, instrument basis, venue/reference, sessions, horizon, and timeframes;
- data sources, feature calculations, bar-completion rules, and event inputs;
- regime, setup, entry, exit, stop, target, expiry, and no-trade rules;
- sizing interface and portfolio assumptions;
- spread, fees, slippage, financing, borrow, roll, and currency-conversion model;
- every parameter and its allowed range;
- evaluation metrics and pass/fail thresholds declared before the final test.

Reject ambiguous prose that permits rules to change after results are seen.

### 2. Audit Data and Simulation Integrity

Check timestamp alignment, exchange calendars, daylight-saving handling, missing/duplicate bars, corporate actions, delistings, survivorship bias, futures expiry/roll, point-in-time fundamentals, revised macro data, and look-ahead leakage.

Model order eligibility and fills without using future bar information. Apply conservative costs and liquidity constraints. Record all exclusions.

### 3. Separate Development and Evaluation

Use chronological train, validation, and untouched test periods. Use walk-forward evaluation and purge or embargo overlapping labels when relevant.

Keep the final test locked until the strategy and thresholds are frozen. Treat any post-test change as a new version requiring a new untouched test.

### 4. Measure Robustness

Report after-cost trade count, coverage, expectancy, win/loss distribution,
profit factor, turnover, drawdown, time under water, tail loss, and
risk-adjusted return. Also report qualified candidates per session/week,
READY_NOW frequency, candidate-to-ticket conversion, platform-translation miss
rate, and the share of no-trade outcomes caused by market rules versus data or
workflow blockers. Break results down by time, instrument, side, regime,
volatility, session, and event proximity.

Run parameter perturbation, cost/slippage stress, delayed-data stress, missing-data stress, and bootstrap or other uncertainty analysis. Flag dependence on a few trades, a narrow parameter optimum, or one market regime.

When validating `HYBRID_M5`, freeze `M15` as the baseline and compare both
versions on identical instruments, sessions, data periods, event exclusions,
and portfolio constraints. Report whether the added M5 candidates improve
after-cost expectancy rather than only trade count. Include M5 false-trigger
rate, spread-to-stop, total-cost-R, break-even win rate, MAE/MFE, latency from
zero to two M5 bars, and platform-translation misses.

If the strategy outputs probabilities, evaluate out-of-sample calibration and store the calibration method and validity range.

### 5. Stage Deployment

Allow `FORWARD_OBSERVATION` only when all predeclared historical gates pass. Require a new, time-forward observation period with the same code path, data timing, and cost model before `ADVISORY_VALIDATED`.

Keep the `0.25%` `HYBRID_M5` research risk cap through
`FORWARD_OBSERVATION`. Only an exact `ADVISORY_VALIDATED` artifact may activate
the normal account-profile risk tier.

Define review thresholds for drift, realized slippage, calibration, drawdown,
error rate, missing/stale data, setup drought, and translation miss rate. Set
status to `SUSPENDED` or `REJECTED` when a stop condition is breached. This
review contract does not create an autonomous monitoring service, alert, or
pre-trigger pending order and never accesses XTB. Forward execution inputs
must come from values supplied by the user.

### 6. Record the Artifact

Create a versioned `validation_id` linked to strategy code/config, data references, cost model, test periods, metrics, limitations, approvals, and next review date. Send it to `skills/trade-journal-review/SKILL.md`.

## Output

Return:

1. `Validation status:` one allowed status.
2. `Identity:` strategy version, validation ID, code/config and data references.
3. `Integrity checks:` pass/fail with evidence.
4. `Evaluation design:` splits, walk-forward schedule, fill and cost assumptions.
5. `Results:` after-cost metrics, uncertainty, regime breakdown, and stress tests.
6. `Gates:` predeclared thresholds and outcomes.
7. `Advisory limits:` validated scope, monitoring thresholds, expiry, and next review.
