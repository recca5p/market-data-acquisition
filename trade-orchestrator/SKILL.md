---
name: trade-orchestrator
description: Coordinate a proactive manual-only non-crypto workflow that uses Google-assisted discovery, Investing.com/public data, official releases, and local calculations to rank and promote a ready-now LONG or SHORT plan. Use for market scans, active-session refreshes, and manual XTB ticket preparation. Never access or control XTB; after public analysis, ask the user once for current XTB symbol, bid, ask, spread, quote time, value per point, and account fields needed for exact translation and sizing.
---

# Manual Trade Orchestrator

## Mission

Produce a cited, ranked manual trade plan from public market context and move a
ready-now candidate to ticket translation without unnecessary waiting. The
user alone reads XTB, supplies real-time fields, and decides whether and how to
place it. Never open or control XTB, call a broker, claim a fill, imply
guaranteed profit, or produce a crypto trade.

Read [references/workflow-contract.md](references/workflow-contract.md) before starting.
When a platform screenshot or ticket description is available, also read
[references/platform-ticket-profile.md](references/platform-ticket-profile.md).

## Fixed Mode

Use `MANUAL_ADVISORY` for every workflow. Default to Google-assisted discovery,
publicly visible Investing.com data, official releases, public news, and local
calculations. Disclose basis, timestamp, delay, and uncertainty.

Set `xtb_interaction_allowed: false`. Do not use an XTB API, connector,
authenticated browser session, desktop control, or login. Treat all XTB
real-time and account fields as `USER_PROVIDED_REALTIME`.

The skills do not have broker or account access. Missing user-provided margin,
account, or executable-quote data is never a blocker for scanning, candidate
ranking, direction, or public-reference risk geometry. It only blocks exact
platform ticket fields, quantity, and account-specific monetary estimates.

At the start of each active trading window, create a `session_id` and derive
current controls once. Consecutive-loss, session-stop, and override flags from
an older session expire. An unresolved basis incident remains only for its
named instrument/contract and blocks only that instrument's user-editable
ticket and sizing until reconciled.

## Workflow

### 1. Resolve the Request

Resolve the instrument, public reference basis, direction horizon, and useful timeframes. If the user does not name a venue, choose a common public reference and disclose that it may differ from the user's platform.

Choose one `entry_timing_mode`:

- `M15` for the existing completed-M15 baseline;
- `HYBRID_M5` when the user wants a higher opportunity rate while retaining
  H1 regime and M15 setup filters. Treat it as `RESEARCH_ONLY` until the exact
  profile is validated.

In `HYBRID_M5`, H1/M15 determine direction and M5 only confirms timing. Never
promote a countertrend M5 pattern.

Define one session window:

- `ASIA`;
- `EUROPE`;
- `US_PREOPEN`;
- `US_CASH`;
- `OVERNIGHT`.

Use `<ICT-date>-<window>` as the default `session_id`. Before the first
account-sized ticket in that session, obtain or reuse one valid session
snapshot. If account state is unknown, proceed with market work and mark only
sizing/ticket readiness as conditional.

After a reported stop in the same `session_id`, require at least one completed
public or platform trigger-timeframe bar and a fresh market scan before
considering a replacement. Never increase risk to recover the loss. If this is
the first reported loss in that session, cap any eventual replacement ticket
at `0.5%` confirmed equity; after two consecutive losses, return `NO_TRADE` for
the rest of that session. Do not carry the count into a later session.

Apply the asset-class gate before acquiring data. If the requested instrument's
primary underlying or reference is a cryptoasset, including crypto spot,
perpetuals, futures, options, CFDs, or crypto-tracking ETPs/ETFs, stop the
workflow and return:

- `status: NO_TRADE`;
- `decision: NO_TRADE`;
- `decision_reason_code: UNSUPPORTED_ASSET_CLASS_CRYPTO`;
- `platform_ticket.action: DO_NOT_CLICK`;
- no direction, entry, stop, target, quantity, leverage, or execution guidance.

Do not reinterpret an ambiguous request as crypto. Ask for or select a
supported liquid market from precious metals, industrial/base metals, energy,
agriculture/soft commodities, livestock, emissions, fertilizer/chemical
exposures, FX, rates/sovereign bonds, volatility, equity indices, or liquid
stocks. Crypto-related operating-company stocks remain single stocks unless
the instrument being traded is primarily a cryptoasset tracker.

For the first open-ended scan of a session, call `$market-data-acquisition`
with `BROAD_BASELINE`. For subsequent scans in the same session, call
`ACTIVE_SESSION_REFRESH` and deep-scan the liquid session core, prior promoted
candidates, and new catalysts. Do not repeat a deep scan of every bucket when a
recent baseline remains usable.

Rank candidates by readiness, identifiable basis, liquidity, completed trigger,
extension, fresh catalyst, event risk, and attainable reward/risk. Promote at
most one `READY_NOW` primary and two secondary candidates. Do not return only a
watchlist when a ready-now setup exists. Include `NO_TRADE` when none meets the
gates; breadth is not permission to lower risk standards.

For an XTB workflow, require `$market-data-acquisition` to apply its verified
XTB universe. Do not promote a generally traded futures market unless the
current public XTB documents list a corresponding instrument and the user
confirms it is visible and openable. Never search inside the user's XTB
platform. Treat FX pairs as FX CFDs and futures-referenced indices, rates,
volatility, and commodities as XTB OTC instruments unless the specification
explicitly states otherwise.

Do not ask for XTB data before public acquisition or to duplicate usable
public bars. After promoting the primary candidate, ask the user once for
compact real-time text containing symbol, bid, ask, spread, quote time, and
value per point. Accept a screenshot only when the user prefers it.

For `HYBRID_M5`, public M5 delayed by at least one full bar cannot produce
`READY_NOW`. In that case ask once for the promoted symbol's current quote and
latest completed M5 OHLC/time; a focused platform screenshot is acceptable
because it refreshes the trigger and does not duplicate the usable H1/M15
context.

When the user already provides a platform screenshot, capture its broker
symbol, bid, ask, spread, selected quantity, supported order tabs, point/pip
value, margin, fees, and swap when visible. Treat the platform quote as the
ticket basis and public sources as analytical context. Never silently copy a
spot, futures, or cash-index level into a differently priced CFD.

### 2. Acquire Public Context

Call `$market-data-acquisition`. Accept delayed data when the provider timestamp/delay is known or the local observation time is recorded.

Continue with `PARTIAL` data when every decision-critical field is available
and the missing fields are explicitly noncritical. Do not stop merely because
public data is delayed; broker connectors are prohibited and must never be
attempted.

If delay is material relative to the horizon, narrow the public valid-entry
zone and require platform translation before a ticket. Use `WAIT_FOR_DATA`
only when the public instrument, timestamps, required bars, or material event
facts are unusable or contradictory. Missing account or platform fields are
not public-data blockers.

For `HYBRID_M5`, distinguish directional sufficiency from trigger readiness:
usable H1/M15 plus stale/absent current M5 returns `NEAR_READY` and
`NEEDS_USER_REALTIME`, not `WAIT_FOR_DATA` and not `READY_NOW`.

### 3. Build the Directional Plan

Call `$trade-decision-guardrails`.

- `LONG` or `SHORT`: continue to the manual risk plan.
- `NO_TRADE`: explain the failed setup or unacceptable reward/risk.
- `WAIT_FOR_DATA`: state the exact unusable public field that is needed.

For a valid public-basis LONG/SHORT, require
`setup_readiness: READY_NOW | NEAR_READY` and an execution state. A
`READY_NOW` decision without user-provided XTB data proceeds as
`NEEDS_USER_REALTIME`, not `WAIT_FOR_DATA`.

A validated strategy may be used when available. For a one-off discretionary analysis, do not require `$trade-strategy-specification` or `$strategy-validation`; label the framework `UNVALIDATED_DISCRETIONARY`.

### 4. Build the Manual Risk Plan

Call `$portfolio-risk-manager`.

Always calculate public-reference entry-to-stop distance, targets, gross/net
reward-to-risk, expiry, and invalidation. If the user supplies current
platform and risk inputs, translate the geometry and calculate an indicative
quantity. Otherwise leave platform fields and quantity null without blocking
the ready-now directional plan.

Use the user's `user-cfd-usd-2000-v1` profile when account sizing is requested.
Treat USD 2,000 as planned, not confirmed, until a broker snapshot activates
the profile. Reuse a current-session snapshot until its declared expiry or a
state-changing event. Do not request a full account screenshot before every
ticket when no fill, exit, order change, or material account change has been
reported. After confirmation, normally risk USD 15, never more than USD 20,
cap total open risk at USD 40, and target approximately 2R after costs. Deduct
every known open and pending order before sizing.

Until the `HYBRID_M5` profile is `ADVISORY_VALIDATED`, cap risk at `0.25%` of
confirmed equity. Require explicit spread, fee, slippage, and financing
buffers; reject spread greater than `0.20` of stop distance or total estimated
execution cost above `0.25R`.

### 5. Optionally Check the Manual Ticket

Call `$order-execution-controls` only after
`execution_state: PLATFORM_TICKET_READY` to validate the arithmetic and
internal consistency of the translated manual trade card. Do not call it for
`REQUEST_USER_REALTIME` or `NEEDS_USER_REALTIME`. This skill cannot
contact a broker or submit anything.

### 6. Map to the User's Ticket

Choose:

- `MARKET` with `BUY` or `SELL`;
- `STOP_LIMIT` with `BUY_STOP`, `SELL_STOP`, `BUY_LIMIT`, or `SELL_LIMIT`;
- `REQUEST_USER_REALTIME` when a ready-now public plan needs the user's current
  XTB values for translation;
- `DO_NOT_CLICK`.

Default proactive behavior is a Market ticket only after a completed trigger
and while the current user-provided XTB quote is inside the valid entry zone.
Do not create alerts, monitors, or pre-trigger pending orders. Use a pending
order only when the user explicitly requests it or an exact validated strategy
requires it.

For `HYBRID_M5`, the translated Market ticket additionally requires a fresh
current quote, a completed M5 trigger timestamp, confirmed H1/M15 alignment,
and preserved trigger integrity. Do not pre-stage an order while waiting for
the M5 bar.

If platform basis is not reconciled, preserve the ready-now direction and
public-reference plan, choose `REQUEST_USER_REALTIME`, and ask the user once
for the compact XTB fields. Do not attempt to retrieve them and do not print
external-reference numbers as ticket inputs.

### 7. Present the Trade Card

Show `THAO TÁC TRÊN TICKET` first only when exact current platform translation
exists. It must contain only the fields the user can enter: tab, order type,
button, quantity, entry/trigger price, stop-loss, and take-profit.

Otherwise show `KẾ HOẠCH CHỦ ĐỘNG` first with:

- primary candidate and direction;
- `READY_NOW` or `NEAR_READY`;
- named public reference and non-executable entry geometry;
- expiry and event cutoff;
- `REQUEST_USER_REALTIME` plus the minimal fields the user must provide for
  translation.

When `REQUEST_USER_REALTIME` is required, end the actionable block with this
compact template and omit fields that are not needed:

```text
DỮ LIỆU REAL-TIME CẦN BẠN CUNG CẤP
Mã XTB:
Bid:
Ask:
Spread:
Giờ báo giá:
Giá trị mỗi point/pip:
Equity + lệnh đang mở/chờ: <chỉ hỏi nếu cần tính khối lượng>
```

Ask once for the promoted primary candidate. Accept compact text as the
default; do not require a screenshot and do not ask the user for public chart
data the skills can obtain from Google/Investing.

For `HYBRID_M5`, append only `M5 vừa đóng (giờ + O/H/L/C)` to that compact
request when the public M5 feed is delayed by one bar or more.

After that concise block, show:

- decision and public instrument basis;
- observed public price, source time, delay, and ICT observation time;
- gross/net reward-to-risk;
- signal expiry and cancel conditions;
- estimated monetary risk/reward when the platform point value is known;
- confirmed equity used, risk amount and fraction, target net profit, and
  remaining portfolio/daily risk budgets;
- a time stop and scheduled-event cutoff;
- strongest supporting and conflicting evidence.

State: `Manual execution only - verify the current price, spread, instrument, and order details on your platform before acting.`

### 8. Journal and Await User Report

Call `$trade-journal-review` for a material acquisition baseline, candidate
promotion, final decision, ticket, or user outcome. Do not append a new
blocking event when an identical missing field persists across a refresh. Set
`AWAITING_USER_REPORT` only for a translated ticket or explicit proposed
manual action. Never assume the user entered.

When the user later reports entry, exit, quantity, fees, or result, append the actual manual outcome and compare it with the original frozen plan.

## Fail-Closed Rules

Never:

- propose, size, map, or validate a cryptoasset trade or a trade whose primary
  underlying is a cryptoasset;
- emit actionable numeric ticket fields while
  an applicable instrument-scoped `BASIS_INCIDENT_LOCK_ACTIVE` is unresolved;
- place, modify, cancel, or simulate a broker acknowledgement;
- turn a public price into a claimed executable quote;
- present an external-reference level as a broker-CFD ticket level without
  reconciling the basis;
- invent an account balance, spread, fill, leverage, margin, contract multiplier, or quantity;
- size from a planned deposit before the funded balance is confirmed;
- present a normal-size ticket below `1.8` estimated net reward-to-risk or any
  ticket below `1.5`;
- call an unvalidated discretionary signal a tested strategy;
- use delay as a hidden assumption;
- carry a session stop or consecutive-loss count into another `session_id`;
- convert `REQUEST_USER_REALTIME` into `WAIT_FOR_DATA` when public evidence is
  sufficient;
- access, log in to, search inside, or control XTB, or call any broker API or
  connector;
- create an autonomous alert, monitor, or pre-trigger pending order as a
  substitute for a ready-now decision;
- report `FILLED`, profit, or loss before the user provides the actual result.

## Final Output

Return either:

- the concise translated platform ticket followed by `RỦI RO & MỤC TIÊU`; or
- `KẾ HOẠCH CHỦ ĐỘNG` followed by the public-reference plan and one compact
  `REQUEST_USER_REALTIME` request.

Then return `MANUAL_ADVISORY`, session ID, setup readiness, workflow status,
acquisition/decision/risk IDs, data-delay warning, manual verification fields,
and journal reference.
