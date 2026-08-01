---
name: trade-strategy-specification
description: Turn a non-crypto trading hypothesis into a complete, versioned, machine-testable strategy specification with fixed data, feature, regime, entry, exit, no-trade, cost, freshness, opportunity-frequency, and evaluation rules. Use when the user wants a repeatable systematic strategy or changes an existing one; include enough session coverage and qualified setup throughput to test whether the workflow can produce opportunities without weakening risk gates. It is optional for one-off advice and never creates autonomous alerts or pre-trigger pending orders.
---

# Trade Strategy Specification

## Mission

Translate a supported non-crypto hypothesis into deterministic rules that another agent can implement and validate without discretionary gap-filling. A new specification is `RESEARCH_ONLY` until `$strategy-validation` approves it. Do not block a separate one-off `UNVALIDATED_DISCRETIONARY` manual advisory merely because no specification exists.

Read [references/strategy-spec-schema.md](references/strategy-spec-schema.md) before writing a specification.
Use
[references/hybrid-m5-entry-research-v1.yaml](references/hybrid-m5-entry-research-v1.yaml)
as the current research profile when the hypothesis is H1/M15 context with M5
entry timing.

## Specification Workflow

### 1. Define the Hypothesis and Scope

State the economic or behavioral hypothesis, expected holding horizon,
supported instruments, exact instrument basis, venue/reference, sessions, and
conditions under which the hypothesis should fail. Predeclare the intended
decision windows, minimum qualified-opportunity frequency, and maximum
acceptable share of sessions with no eligible setup. These are workflow
viability metrics, not permission to lower quality or risk thresholds.

Reject the request before specification work when the primary
underlying/reference is a cryptoasset, including crypto spot, perpetuals,
futures, options, CFDs, or crypto-tracking ETPs/ETFs. Return
`Specification status: REJECTED_SCOPE` with
`UNSUPPORTED_ASSET_CLASS_CRYPTO`; do not create rules, parameters, data
contracts, backtest instructions, or sizing interfaces.

Do not create a strategy merely by fitting patterns to the current trade opportunity. Separate hypothesis-development data from the later untouched evaluation period.

### 2. Define Data Deterministically

Specify:

- source classes and canonical instrument mapping;
- timeframes, minimum history, completed/in-progress bar rules, timezone, session calendar, and freshness limits;
- corporate-action adjustment or futures contract/roll method;
- event, fundamental, cross-market, borrow, funding, and venue data when used;
- missing, stale, contradictory, delayed, revised, and abnormal-data behavior.
- distinct timeframe roles for regime, setup, and trigger; do not describe all
  timeframes as interchangeable confirmation.

Every public decision field must map to `$market-data-acquisition`. Treat `$broker-account-snapshot` as an optional source only when the user explicitly wants account-aware sizing.

Never specify or assume direct XTB access. Public analysis may use Google,
Investing.com, official sources, and local calculations; exact XTB translation
must consume only real-time values supplied by the user.

### 3. Define Features and Rules

Give an exact formula, lookback, input field, alignment, and warm-up rule for every feature. Define regime, setup, trigger, filter, entry, initial stop, invalidation, exit, target, expiry, and no-trade rules as testable boolean or numeric expressions.

Define `READY_NOW`, `NEAR_READY`, and `REJECT` mechanically. Measure candidate
generation separately from platform ticket translation so missing broker data
does not masquerade as lack of market opportunity.

For a lower-timeframe trigger, define current-quote validity, trigger
invalidation, maximum trigger age, spread-to-stop, total-cost-R, and what
happens when the public trigger feed is delayed by one full bar.

Specify precedence when multiple rules conflict. Do not use undefined terms such as "strong trend", "good volume", "important support", or "high confidence".

### 4. Define Costs and Execution Assumptions

Declare spread, slippage, fees, financing, borrow, roll, currency conversion,
order types, order eligibility, fill model, latency, partial-fill handling, and
liquidity constraints. Default to current-quote Market translation after a
completed trigger or valid pullback zone. Do not add autonomous alerts,
monitors, or pre-trigger pending orders; include Stop/Limit only when the user
explicitly requests it or the validated strategy requires it.

Keep position sizing as an interface to `$portfolio-risk-manager`; do not embed martingale, averaging down, or unbounded risk.

Any new lower-timeframe mode begins `RESEARCH_ONLY` with a conservative risk
cap. It may increase opportunity frequency, but its after-cost expectancy must
be compared with the frozen higher-timeframe baseline before promotion.

### 5. Predeclare Evaluation Gates

Before the untouched test, define required metrics, minimum coverage/trade
count, maximum drawdown/tail loss, minimum after-cost expectancy, robustness
tests, probability-calibration criteria when relevant, paper-forward duration,
qualified opportunities per session/week, READY_NOW frequency, and
candidate-to-ticket conversion.

Choose thresholds from the intended risk policy and use case, not from the final test results. Document uncertainty and reasons for each threshold.

### 6. Freeze and Handoff

Assign a strategy ID, semantic version, code/config hash when available, creation time, author/source, and change reason. Mark the artifact `RESEARCH_ONLY`.

Send the exact artifact to `$strategy-validation`. Any later change to logic, data, parameters, universe, basis, costs, or execution produces a new version.

## Output

Return:

1. `Specification status: RESEARCH_ONLY`;
2. identity, version, hypothesis, scope, and failure thesis;
3. exact data and freshness contract;
4. feature and trading rules with precedence;
5. cost, fill, liquidity, and sizing interfaces;
6. predeclared validation and paper-forward gates;
7. known limitations and forbidden discretionary overrides;
8. handoff to `$strategy-validation`.
