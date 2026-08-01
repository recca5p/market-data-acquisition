---
name: market-data-acquisition
description: Proactively collect, verify, calculate, and rank public non-crypto market opportunities using Google-assisted discovery, publicly visible Investing.com data, official releases, public news, and the bundled breadth scanner. Use before a manual LONG/SHORT advisory or active-session refresh; never access XTB, a broker account, a broker API, or a logged-in platform. Return a ready-now public-reference shortlist first, then identify the minimal real-time XTB fields the user must provide for ticket translation.
---

# Public Market Data Acquisition

## Mission

Collect publicly available market and event data for supported trading markets
without waiting for XTB data. Produce an immutable `acquisition_id`, a cited
time-stamped package, calculated ranking features, and a ranked shortlist in
**Asia/Ho_Chi_Minh (ICT, UTC+7)**. Do not access XTB, make the final LONG/SHORT
decision, submit an order, or acquire crypto data for a trade proposal.

This skill uses only public sources. Prices may be delayed, indicative, or based on a different instrument from the user's execution venue. State that limitation prominently and do not infer account, margin, spread, fill, or trading-permission data.

Never open or control the user's XTB app, log in to XTB, call an XTB or broker
API, use a broker connector, inspect authenticated browser state, or claim
real-time broker data. Real-time XTB values enter this workflow only when the
user supplies them as text, screenshot, or export after a candidate is
promoted.

## Source Hierarchy

Read [references/source-hierarchy.md](references/source-hierarchy.md) before collecting data. Read [references/acquisition-schema.md](references/acquisition-schema.md) before returning a package.

Use sources in this order:

1. **Official or primary sources** - macro releases, central-bank decisions, commodity inventories, company filings, earnings, and official statements.
2. **Public market-data or aggregator pages** - use publicly visible
   Investing.com price, chart, change, technical inputs, session information,
   and event calendars when accessible under its terms and visible timestamps.
3. **Public news/reporting** - time-stamped contextual reporting from a named publisher.
4. **Permitted web/search discovery** - Google or another search tool to locate public sources. A timestamped snippet may be recorded as low-confidence context, but do not use it as the sole evidence for a decision-critical price, release, or event when the original source can be opened.

Public prices, including those displayed by Investing.com, may be used as delayed market context. They are never an executable quote, a substitute for account/margin data, or proof of a fillable price. Do not scrape protected or private endpoints, bypass access controls, use an unauthorized login/session, or copy, store, or distribute data beyond permitted use.

## Input Contract

For a manual-advisory request, resolve:

- asset class and whether the primary underlying/reference is prohibited crypto;
- requested instrument plus venue or reference basis;
- decision horizon, `entry_timing_mode`, timeframe roles, required fields, and
  minimum bar counts;
- accepted provider delay or freshness expectation, allowed session, and event lookback/lookahead;
- adjustment rules for equities and roll/expiry rules for futures.

Strategy and validation references are optional for a one-off discretionary advisory. If freshness limits are absent, record the actual delay and let `$trade-decision-guardrails` use a conditional entry that the user must verify. Never invent a continuous-futures roll method.

For an open-ended request such as "scan the market," use a two-pass scan:

1. Run a fast breadth pass over a broad liquid non-crypto universe.
2. Run a deep pass over the active-session core plus the strongest breadth
   candidates.

On the first broad scan of a session, include at least one identifiable public
reference from each currently open or relevant bucket:

- FX;
- equity indices;
- rates and sovereign bonds;
- volatility;
- precious metals;
- industrial/base metals, including copper and aluminum when usable;
- energy;
- agriculture and soft commodities;
- livestock;
- emissions/environmental markets;
- fertilizer/chemical exposures;
- liquid single stocks.

Skip a bucket only when its market is closed, its public data is unusable, or
no reasonably liquid, identifiable instrument exists; record the matching
stable `coverage_audit` reason code and a plain explanation. A missing XTB
symbol, quote, spread, account value, or point value is never a market-skip
reason. The fertilizer bucket may use liquid listed producers or an
exchange-listed instrument as the tradable candidate while using fragmented
physical fertilizer benchmarks only as context. A producer stock, ETF, future,
cash benchmark, and broker CFD are different instruments and must never share
undisclosed price levels.

Create the canonical `coverage_audit` in the acquisition schema for every
open-ended scan, including all 12 required baseline buckets even if a bucket
was not scanned. Record totals, attempted/succeeded instrument attempts,
representative instruments, provider market state and source/time evidence,
coverage outcome, and every material unpromoted/rejected candidate or skipped
bucket. Use `NO_CONFIGURED_PUBLIC_REFERENCE` for unconfigured `ALUMINIUM` or
`EMISS` references; never let an adjacent copper or unrelated environmental
reference silently count those gaps as covered.

After a broad baseline exists for the current session, an active-session
refresh may reuse unchanged instrument metadata and official event facts for
up to four hours. Refresh quotes, completed bars, session status, material
headlines, and event proximity for:

- the prior top candidates;
- the active-session core;
- any market with a new material catalyst.

Do not repeat a full deep acquisition for every bucket on every refresh. Set
`coverage_audit.baseline_reuse` with the reused baseline acquisition ID,
acquired time, age, fields reused, and the exact fields refreshed. For a
session-core refresh, mark every non-core bucket `NOT_IN_REFRESH_SCOPE`; do not
describe it as a new full scan. If there is no valid baseline to reuse, say
`NOT_REUSED` rather than implying one exists.

Use this default liquid core unless a strategy or user request supplies a
different one:

- Asia: `USDJPY`, `AUDUSD`, `JP225`, and `GOLD`;
- Europe: `EURUSD`, `GBPUSD`, `DE40`, `GOLD`, and `OIL.WTI`;
- U.S. futures/pre-open: `US500`, `US100`, `GOLD`, `OIL.WTI`, and `NATGAS`;
- U.S. cash session: the same core plus liquid stocks with current catalysts;
- agriculture window: add `WHEAT`, `CORN`, or `SOYBEAN` only when their
  session, liquidity, and event calendar are usable.

When the user's execution venue is XTB, read
[references/xtb-supported-universe.md](references/xtb-supported-universe.md)
before selecting candidates. Use its verified symbols as a discovery
allowlist. It is a static public-document reference, not access to XTB.
Current symbol availability must be confirmed by the user before an actionable
ticket. A public exchange future may provide context for an XTB CFD, but it
does not prove the CFD's current price, basis, or availability.

When the public reference has a stable, identified relationship to the user's
XTB instrument, record the relationship and any user-supplied discrepancy. Do
not require real-time XTB data to rank or hand off a directional candidate.
After promotion, request from the user only the current XTB symbol, bid, ask,
spread, quote time, and value per point needed to translate
public-reference geometry into an exact user-editable ticket and size account
risk.

Use `HYBRID_M5` as the research entry-timing mode when the user wants more
qualified opportunities without abandoning the existing directional filter:
H1 is regime context, M15 is setup context, and M5 is only the completed entry
trigger. Keep `M15` as the comparison baseline. Never let an M5 signal override
conflicting H1/M15 direction.

## Autonomous Acquisition Workflow

### 1. Resolve Scope Without a Screenshot

Use the explicit symbol, asset, or market requested in the task. Resolve the closest publicly quoted instrument and asset class, and disclose its basis (for example, spot, front-month future, cash index, ETF, stock, or CFD-style reference) before requesting data.

Before any price, chart, funding, derivatives, or news lookup, return `BLOCKED`
with `blocking_reason: UNSUPPORTED_ASSET_CLASS_CRYPTO` when the primary
underlying/reference is a cryptoasset. This includes crypto spot, perpetuals,
futures, options, CFDs, and crypto-tracking ETPs/ETFs. Set
`manual_advisory_data_sufficient: false` and do not pass directional evidence
or levels downstream.

If the requested instrument is ambiguous, choose a widely used public reference only when that is unlikely to mislead; otherwise return `BLOCKED` with the exact ambiguity. Do not require private market-data access or a chart screenshot.

### 2. Collect Public Market Data

For each candidate instrument, collect from permitted public sources:

- bid, ask, last, mid or displayed level when available; percentage/absolute change; session status; provider timestamp; stated delay; and local observation time;
- publicly available OHLCV bars when available, recording the source symbol, timeframe, currency, bar timezone, open/close time, completion state, adjustment state, and coverage;
- instrument metadata including canonical identifier, venue/reference, currency, tick and quantity units when public, spot/future/cash-index basis, contract month, expiry, and roll basis.

For the breadth pass, calculate only reproducible ranking features from
identified bars, such as completed-bar trend alignment, ATR, RSI, recent range,
relative strength, volume change when meaningful, and distance from recent
support/resistance. Use
[scripts/scan_public_markets.mjs](scripts/scan_public_markets.mjs) when its
public source is available. Use its default broad scan at session bootstrap;
use `--session auto` or an explicit session name for the active-core refresh,
then verify the promoted candidates and material events independently.

Classify each deep-pass candidate:

- `READY_NOW`: a completed public trigger exists, the reference is not
  materially stale for the horizon, the move is not excessively extended, and
  there is plausible room for the decision layer to construct at least 1.5R;
- `NEAR_READY`: direction is coherent but one named market condition is absent;
- `REJECT`: mixed, stale, closed, overextended, event-blocked, or structurally
  unable to offer acceptable reward/risk.

Use a default extension check of `0.75 ATR` from the relevant trigger or
bounded entry area for an unvalidated discretionary M15 setup. For
`HYBRID_M5`, apply the versioned research profile in
`$trade-strategy-specification` and separately measure extension from the M15
setup area and the completed M5 trigger. These are ranking heuristics, not
validated probabilities or ticket rules.

For `HYBRID_M5`, a public M5 feed delayed by one full M5 bar or more may
support H1/M15 context but cannot produce `READY_NOW`. Return `NEAR_READY` with
`trigger_data_state: NEEDS_USER_REALTIME`, then request the current user
provided M5 completed bar and quote only for the promoted candidate. A stale
trigger must not be converted into an executable-looking plan.

Do not calculate a broker ticket, position size, expected account loss,
platform spread, margin, or fill reconciliation from public data. Public-basis
analytical levels may be handed off when clearly labelled as non-executable.

### 3. Collect Event and Cross-Market Context

Collect the next 24-hour high-impact calendar and recent material releases. Record actual, consensus, prior, release time in ICT, primary source, and observed public-market response where available.

Collect asset-specific context from the source hierarchy:

- **FX:** exact spot/CFD or futures basis, both central banks, rate
  differentials, macro releases, intervention risk, and session liquidity.
- **Rates/sovereign bonds:** exact contract and maturity, cash-yield curve,
  central-bank expectations, auction/supply calendar, inflation and labor
  releases, duration direction, and roll.
- **Volatility:** exact index, future, or CFD basis, contract month, term
  structure, settlement method, event calendar, and equity-index context.
- **Gold:** public gold reference, DXY, US yields/real-yield proxy, central-bank/inflation events, and verified geopolitical facts.
- **Industrial/base metals:** exact exchange contract or cash reference,
  warehouse inventories, China/global manufacturing demand, USD, supply
  disruptions, smelter/refining economics, and contract units/currency.
- **Natural gas:** exact public contract/reference and roll, EIA storage, weather, production, LNG/export, and seasonality.
- **Crude oil and refined energy:** exact grade and contract, official
  inventory data, OPEC+ or other primary supply announcements, refinery
  conditions, freight, and geopolitical supply facts.
- **Agriculture and soft commodities:** exact exchange contract, crop year,
  USDA or relevant primary releases, weather, export flows, seasonality, and
  exchange price-limit or delivery considerations.
- **Livestock:** exact delivery contract, USDA supply and demand reports,
  feed costs, disease/trade facts, seasonality, and price limits.
- **Emissions:** exact allowance and venue, policy/compliance calendar,
  auction supply, energy/fuel-switching context, currency, and expiry.
- **Fertilizer/chemicals:** distinguish physical urea, ammonia, phosphate, and
  potash benchmarks from liquid producer equities or listed derivatives.
  Collect feedstock costs, crop economics, freight, export restrictions,
  company filings/earnings, and benchmark methodology when public.
- **Equity index:** yields, volatility index/equivalent, market breadth, sector leadership, and major constituent earnings.
- **Single stock:** earnings, filings, material legal/corporate events, average volume, short-interest/squeeze risk, and sector/index context.

Use a web/search provider to find sources or confirm a public event. Open the cited source before treating a claim as fact. Record failed source attempts and uncertainty.

For equities, identify splits, dividends, symbol changes, halts, and whether historical bars are adjusted. For futures, identify contract expiry and the exact continuous-series or roll method. Do not join incompatible series silently.

### 4. Normalize and Validate

Before returning:

- convert all displayed times to ICT and label the timezone;
- verify that every quote and OHLCV series belongs to the declared public instrument, not a similarly named spot/futures/index reference;
- calculate indicator inputs only from identified, completed or explicitly labelled in-progress public bars; do not import an opaque buy/sell indicator;
- enforce supplied age/lag limits when present; otherwise record the actual age and whether delay is material to the requested horizon;
- for `HYBRID_M5`, confirm that H1 and M15 directions agree, the M5 trigger bar
  is complete, and the current observed price has not invalidated or outrun
  that trigger;
- validate timestamp order, bar intervals, duplicates, gaps, nonpositive prices, impossible OHLC relationships, currency, adjustment state, session boundaries, and provider revisions;
- compare multiple public prices where required by the request, apply its explicit discrepancy tolerance, record conflicts, and do not claim that any public source controls execution;
- mark missing, stale, contradictory, delayed, or abnormal data explicitly.
- rank no more than three promoted candidates, with `READY_NOW` before
  `NEAR_READY`; do not hide a valid ready-now candidate behind a broad
  watchlist.

If a requested field cannot be retrieved, return `PARTIAL` and identify whether it is decision-critical. Use `BLOCKED` only for an unresolved instrument/basis or when no usable public price, timestamps, bars, or material context can be obtained. Do not fabricate values or silently use stale cache.

### 5. Hand Off a Reproducible Package

Return the acquisition schema, source log, and shortlist to
`$trade-decision-guardrails`. Set `manual_advisory_data_sufficient: true` when
every directional decision-critical field is usable, including for an
explicitly delayed source. Missing broker quote, account equity, open risk, or
platform point value must not make the directional package insufficient.
Mark whether the package is ready for a directional decision and whether a
separate platform translation is still required. Then create an acquisition
event using `$trade-journal-review`.

Do not issue `LONG`, `SHORT`, or a speculative size. `$trade-decision-guardrails` alone evaluates the completed package.

## Failure Rules

- Retry only within provider rate limits and published usage terms.
- Never bypass CAPTCHA, bot mitigation, paywalls, robots directives, authentication, rate limits, or access controls.
- Never automate scraping of a Google result page. Use an approved search capability; open the original source when practical and label snippet-only context as low confidence.
- A displayed Investing.com quote may be used as delayed context when its page is accessible under the site's terms; label it with the observed time and any stated delay.
- For an unavailable source, record `source_unavailable` with the ICT time and proceed only if the remaining permitted sources support the requested public-data package.
- Do not create autonomous alerts, recurring monitors, or pre-stage pending
  orders. Proactivity in this skill means scanning now, ranking now, and
  promoting a ready-now candidate when the evidence supports one.

## Output Contract

Return this order:

1. `Acquisition status:` `COMPLETE`, `PARTIAL`, or `BLOCKED`.
2. `Scope:` acquisition ID, strategy/version, requested market, resolved public instrument/basis, venue/reference, horizon, required fields, and ICT observation time.
3. `Candidate shortlist:` at most three ranked candidates with readiness,
   entry-timing mode, timeframe roles, public basis, setup type, completed
   trigger-bar state, trigger-data state, current-zone validity, extension,
   event cutoff, and rejection/conflict facts.
4. `Public market data:` field-level provenance, quote fields, provider timestamp/delay, local observation time, instrument lifecycle, and OHLCV quality/coverage.
5. `Event and cross-market data:` confirmed facts, ICT times, and source links/identifiers.
6. `Validation:` stale, missing, contradictory, delayed, or abnormal fields.
7. `Handoff:` whether the directional package is sufficient and whether exact
   platform translation remains; state that public prices are not executable.
8. `Coverage audit:` the complete canonical `coverage_audit`, not only the
   top-N shortlist.
9. `Journal record:` acquisition ID/reference and source-acquisition summary.

For an open-ended scan that becomes user-visible, default to Vietnamese unless
the user asks for another language. The actionable plan or `NO_TRADE` outcome
comes first. Immediately after that block, render the canonical audit under
the exact Vietnamese headings `ĐÃ KHẢO SÁT` and `SKIP/LOẠI VÀ LÝ DO`. The first
section must state scan mode, session, ICT time, attempted/succeeded totals,
all required buckets, representative instruments, provider/session state and
coverage outcome. The second must list every material unpromoted/rejected
candidate and skipped or gap bucket with its stable reason code and plain
explanation. Do not replace these sections with a bare claim that the market
was scanned.

Do not ask the user for XTB data before public acquisition and candidate
promotion. When real-time translation is needed, ask once for compact text
values; accept a screenshot only if the user prefers it.
