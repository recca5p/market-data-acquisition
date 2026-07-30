---
name: trade-decision-guardrails
description: Proactively evaluate ranked public non-crypto candidates built from Google, Investing.com, official sources, and local calculations, then return LONG, SHORT, NO_TRADE, or a true public-data block with readiness and bounded public-reference geometry. Use before manual XTB translation. Never access XTB; missing user-provided real-time or account data must not block direction, and ask the user for current XTB fields only after promoting a setup.
---

# Manual Trade Decision Guardrails

## Mission

Turn public market context into a proactive manual trade proposal for supported
markets. Promote a ready-now candidate when one exists instead of defaulting to
a watchlist. Never place an order, claim an executable price, guarantee profit,
or produce a crypto trade.

Read [references/decision-contract.md](references/decision-contract.md) before evaluating.

## Required Inputs

Apply the asset-class gate before evaluating evidence. When the primary
underlying/reference is a cryptoasset, including crypto spot, perpetuals,
futures, options, CFDs, or crypto-tracking ETPs/ETFs, return `NO_TRADE`,
`DO_NOT_CLICK`, and
`decision_reason_code: UNSUPPORTED_ASSET_CLASS_CRYPTO`. Leave direction, entry,
stop, targets, quantity, and risk-plan eligibility null or false.

Require:

- current `session_id` and session-scoped journal controls;
- any unresolved basis incident with its exact instrument/contract scope;
- identified public instrument/reference basis;
- for commodity and sector-proxy ideas, a clear separation between the exact
  traded instrument and related physical benchmarks, futures, ETFs, or
  producer equities used only as cross-market evidence;
- for FX, rates, and volatility, a clear separation between spot/index data,
  dated exchange futures, yields, and the broker CFD used for the ticket;
- displayed or derived reference price with provider or observation time;
- enough labelled bars and context for the chosen horizon;
- known or estimated provider delay;
- material scheduled-event and abnormal-market flags when relevant.

Do not require a broker snapshot, account balance, margin, open positions, or
real-time XTB quote. A `PARTIAL` public acquisition package may be used when
all decision-critical fields are present. Never attempt to obtain real-time
XTB data directly.

When the user supplies XTB data by compact text or screenshot, capture the
broker symbol, bid, ask, spread, quote time, displayed quantity, supported
ticket tabs, pip/point value, margin, fees, and swap when visible. Label the
source `USER_PROVIDED_REALTIME`; treat it as a point-in-time transcription, not
authorization or a complete account snapshot.

## Decision Workflow

### 0. Apply the Prior-Outcome Gate

Derive active controls only from the current `session_id`. A consecutive-loss,
session-stop, or one-time-override flag from an earlier session must not carry
forward. Daily and weekly loss caps follow their own declared periods.

Treat `BASIS_INCIDENT_LOCK_ACTIVE` as instrument/contract scoped unless the
evidence explicitly proves a wider account or platform problem. A scoped lock:

- does not block scanning or a public-basis LONG/SHORT decision;
- blocks numeric platform ticket fields and quantity for the affected
  instrument;
- sets `execution_state: NEEDS_USER_REALTIME` when the public plan
  is otherwise valid.

Clear the lock only from current user-provided XTB values whose broker symbol,
bid, ask, spread, quote time, and contract basis can be reconciled. Use
`WAIT_FOR_DATA` only when the public directional evidence itself is unusable,
not merely because platform translation remains.

### 1. Freeze the Context

Create a `decision_id`. Record acquisition ID, instrument basis, horizon, timeframes, sources, timestamps, and delay before deciding.

Set `framework_status`:

- `VALIDATED_SYSTEMATIC` when an eligible validation artifact governs the exact rules;
- `UNVALIDATED_DISCRETIONARY` for a one-off analysis.

Do not convert discretionary confidence into a backtested probability.

### 2. Evaluate Direction

Evaluate and cite:

- higher-timeframe trend and market structure;
- nearby support, resistance, breakout, rejection, and invalidation levels;
- momentum and volatility state;
- volume/liquidity context when the source provides meaningful volume;
- scheduled events and verified cross-market drivers;
- facts that conflict with the preferred direction.

Use only indicators whose inputs and completed-bar status are known. Do not copy an opaque provider `BUY/SELL` label as the decision.

Assign one setup type:

- `TREND_PULLBACK`: higher-timeframe structure aligns with direction and a
  completed trigger-timeframe bar holds or reclaims a bounded pullback area;
- `BREAKOUT_CLOSE`: a completed trigger-timeframe bar closes beyond a defined
  level with acceptable extension and room to the next obstacle;
- `FAILED_BREAKOUT`: a completed bar rejects an attempted break and closes back
  through the failure level with coherent higher-timeframe context.

Classify readiness:

- `READY_NOW`: the completed public trigger exists now, the public price is
  inside a bounded reference entry zone, estimated geometry can reach at least
  1.5R, and no hard event/session gate applies;
- `NEAR_READY`: direction is coherent but exactly one named market condition
  is absent;
- `REJECT`: no coherent edge, excessive extension, insufficient room,
  unacceptable event exposure, or invalid data.

For an unvalidated discretionary M15 setup, use `0.75 ATR` beyond the trigger
or intended entry area as the default maximum extension unless market
structure justifies a tighter bound. Do not require a retest after every
breakout: a completed breakout close may be `READY_NOW` when extension,
liquidity, conflicting evidence, and target room are acceptable.

Public completed bars from Investing.com or another identified public source
may satisfy the trigger. Do not require duplicate XTB M15 and H1 candle
screenshots when the public instrument, completion state, delay, and
directional basis are usable. User-provided current XTB values are still
required to translate the plan into an exact CFD ticket.

### 3. Choose One Outcome

Return:

- `LONG` when bullish evidence, trigger, invalidation, and reward/risk are coherent;
- `SHORT` when bearish evidence, trigger, invalidation, and reward/risk are coherent;
- `NO_TRADE` when the setup is mixed, late, abnormal, event-exposed, or offers insufficient reward/risk;
- `WAIT_FOR_DATA` only when a decision-critical public field is unusable.

For prohibited crypto, use `NO_TRADE`, not `WAIT_FOR_DATA`, regardless of data
availability or apparent setup quality.

Delayed data alone is not a blocker. When delay matters, narrow the valid
public-reference entry zone and require current platform translation before a
ticket.

If the user supplies a current XTB text quote or screenshot, its quote basis
controls all ticket prices. If reconciliation is not yet defensible, preserve
the LONG/SHORT decision and public-reference plan, set
`execution_state: NEEDS_USER_REALTIME`, and leave the user-editable ticket
null. Never copy an external level into the broker ticket.

After one reported stop in the same session, cap the next eligible plan at
`0.5%` confirmed-equity risk and require a fresh scan plus one completed public
or platform trigger bar. After two consecutive reported losses in the same
session, return `NO_TRADE` for that session. Reset the consecutive count when a
new declared session begins; never infer a loss from an unreported proposal.

### 4. Construct the Manual Plan

For `LONG` or `SHORT`, require:

- a bounded public-reference entry zone;
- a finite stop-loss beyond the stated invalidation;
- at least one target or deterministic exit rule;
- signal expiry and cancel conditions;
- gross and estimated net reward-to-risk;
- data-delay and basis-risk warnings.

For the user's USD 2,000 risk profile, design the price levels for an estimated
net reward-to-risk near `2.0`. Return `NO_TRADE` below `1.5`. From `1.5`
through `1.79`, mark the plan reduced-risk-only; normal risk requires at least
`1.8`. Do not stretch a target through major resistance/support only to improve
the ratio.

Keep quantity null until `$portfolio-risk-manager` receives sufficient sizing
inputs. Missing sizing inputs do not downgrade a `READY_NOW` directional
decision.

Separate:

- `public_reference_plan`: analytical entry zone, stop, target, reward/risk,
  and expiry on the named public basis;
- `platform_ticket`: exact broker symbol and user-editable fields, populated
  only after current basis translation.

Label every public-reference number `NON_EXECUTABLE_REFERENCE`.

When platform fields are available, map the plan to exactly one supported ticket action:

- `MARKET` with `BUY` or `SELL`;
- `STOP_LIMIT` with `BUY_STOP`, `SELL_STOP`, `BUY_LIMIT`, or `SELL_LIMIT`;
- `DO_NOT_CLICK` when no valid ticket can be constructed.

In proactive mode, prefer a Market ticket only when a `READY_NOW` signal is
confirmed and the current user-provided XTB quote remains inside the valid
entry zone.
Do not create autonomous alerts, monitors, or pre-trigger pending orders.
Support a pending order only when the user explicitly requests one or an exact
validated strategy requires it. For any pending order, require the trigger to
be on the correct side of platform bid/ask. Preserve a displayed quantity only
as `USER_SELECTED_NOT_APPROVED` until risk sizing is complete.

For a Market ticket, include a bounded valid-entry price range. If the current
platform ask/bid moves outside it, return `DO_NOT_CLICK` and rebuild the levels;
do not preserve an old stop and target after a late fill.

### 5. State Uncertainty

Separate observed facts from interpretation. Include the strongest disconfirming evidence.

Use qualitative confidence `LOW`, `MEDIUM`, or `HIGH` only as an evidence-strength label. Set `calibrated_probability` only for an exact validated strategy with out-of-sample calibration; otherwise use null.

### 6. Hand Off

Send `LONG` or `SHORT` plus the proposed ticket mapping to `$portfolio-risk-manager`. Send every outcome to `$trade-journal-review` as a proposed manual plan. Never call a broker or claim the user entered.

## Output

When current user-provided XTB values exist and translation succeeds, return a
concise `THAO TÁC TRÊN TICKET` block before the analysis:

- tab;
- order type;
- button;
- quantity and quantity source;
- current price or pending trigger;
- stop-loss enabled and price;
- take-profit enabled and price.

When platform translation is still needed, return `KẾ HOẠCH CHỦ ĐỘNG` instead
of an empty ticket. Lead with the highest-ranked `READY_NOW` candidate, its
public-basis geometry, and one `REQUEST_USER_REALTIME` block asking the user
for the compact XTB values needed for translation. Do not access XTB or ask for
chart screenshots that duplicate usable public bars.

Then return:

1. decision, setup type, readiness, execution state, reason code, and framework status;
2. source/instrument identity, timestamps, and delay;
3. supporting and conflicting evidence;
4. entry trigger/zone, stop-loss, invalidation, targets/exits, expiry, and cancel conditions;
5. gross/net reward-to-risk and cost assumptions;
6. risk tier (`BASE`, `REDUCED`, or `REJECT`), target-R multiple, time stop, and
   event cutoff;
7. confidence label, calibrated probability or null, and limitations;
8. manual verification checklist and journal handoff.
