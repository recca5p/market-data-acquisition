# Public Market-Data Acquisition Schema

## Contents

1. Status values
2. Required result structure
3. Source-attempt structure
4. Coverage-audit structure and reason vocabulary
5. Handoff rules

## 1. Status Values

- `COMPLETE`: every requested public-data field is sourced, timestamped, and labelled with its instrument basis and delay/uncertainty.
- `PARTIAL`: a requested public-data field is unavailable, stale, contradictory, or insufficiently identified.
- `BLOCKED`: the requested market/instrument is prohibited crypto, is ambiguous, or an essential public source cannot be accessed without bypassing restrictions.

## 2. Required Result Structure

```yaml
acquisition:
  schema_version: "2.4"
  acquisition_id: null
  status: COMPLETE | PARTIAL | BLOCKED
  acquired_at_vn: "YYYY-MM-DD HH:mm:ss ICT"
  timezone: Asia/Ho_Chi_Minh
  request:
    strategy_id: null
    strategy_version: null
    validation_id: null
    framework_status: VALIDATED_SYSTEMATIC | UNVALIDATED_DISCRETIONARY
    decision_horizon: null
    entry_timing_mode: M15 | HYBRID_M5
    timeframe_roles:
      regime: H1
      setup: M15
      trigger: M15 | M5
    required_timeframes: []
    required_fields: []
    minimum_bar_counts: {}
    maximum_quote_age_seconds: null
    maximum_completed_bar_lag_seconds: {}
    accepted_provider_delay_seconds: null
    price_discrepancy_tolerance_fraction: null
    event_lookback_hours: null
    event_lookahead_hours: null
    allowed_sessions: []
    scan_mode: BROAD_BASELINE | ACTIVE_SESSION_REFRESH | SINGLE_INSTRUMENT
    session_id: null
  scope:
    requested_market: null
    resolved_instrument: null
    canonical_identifier: null
    venue_or_reference: null
    instrument_basis: spot | futures | cash_index | etf | stock | cfd_reference | unknown
    asset_class: null
    currency: null
    exchange_timezone: null
    contract_month: null
    expiry: null
    adjustment_or_roll_method: null
    data_mode: PUBLIC_DELAYED
    xtb_interaction_allowed: false
    realtime_execution_data_source: USER_PROVIDED_ONLY

public_market_snapshot:
  quotes:
    - source_name: null
      source_identifier_or_url: null
      source_symbol: null
      venue_or_reference: null
      currency: null
      bid: null
      ask: null
      last: null
      mid: null
      absolute_change: null
      percentage_change: null
      provider_time: null
      stated_delay_seconds: null
      observed_at_vn: null
      age_at_acquisition_seconds: null
      executable: false
  bar_series:
    - source_name: null
      source_identifier_or_url: null
      source_symbol: null
      timeframe: null
      bar_timezone: null
      currency: null
      adjusted: null
      adjustment_or_roll_method: null
      completed_bar_count: null
      first_open_time: null
      last_close_time: null
      last_completed_bar_lag_seconds: null
      data_reference: null
      content_hash: null
      quality_flags: []
  instrument_lifecycle:
    corporate_actions: []
    symbol_changes: []
    halts: []
    contract_expiry: null
    roll_details: null

candidate_shortlist:
  - rank: null
    readiness: READY_NOW | NEAR_READY | REJECT
    entry_timing_mode: M15 | HYBRID_M5
    context_timeframes: [H1, M15]
    public_symbol: null
    intended_broker_symbol: null
    public_reference_basis: null
    directional_structure: BULLISH | BEARISH | MIXED
    setup_type: TREND_PULLBACK | BREAKOUT_CLOSE | FAILED_BREAKOUT | NONE
    trigger_timeframe: null
    trigger_data_state: PUBLIC_COMPLETED | STALE | NEEDS_USER_REALTIME | USER_PROVIDED_REALTIME
    last_completed_trigger_bar_at_vn: null
    last_completed_m5:
      opened_at_vn: null
      closed_at_vn: null
      open: null
      high: null
      low: null
      close: null
    reference_entry_area: null
    reference_invalidation: null
    context_setup_extension_atr: null
    extension_atr: null
    current_extension_atr: null
    current_price_in_valid_zone: null
    trigger_integrity: VALID | INVALID | UNCONFIRMED
    trigger_condition_met: null
    higher_timeframe_alignment_confirmed: null
    room_to_next_level_atr: null
    event_cutoff_at_vn: null
    supporting_facts: []
    conflicting_facts: []
    user_realtime_fields_needed_for_ticket: []

events_and_cross_markets:
  events:
    - event_name: null
      importance: null
      scheduled_or_released_at_vn: null
      status: scheduled | released | revised
      unit: null
      actual: null
      consensus: null
      prior: null
      revised_prior: null
      primary_source: null
      observed_market_response: null
  asset_specific_context: []

source_attempts: []
validation:
  fresh_fields: []
  missing_fields: []
  stale_fields: []
  contradictions: []
  identity_mismatches: []
  timestamp_or_session_errors: []
  duplicate_or_gap_errors: []
  ohlc_or_value_errors: []
  lifecycle_or_adjustment_errors: []
  abnormal_market_flags: []

coverage_audit:
  audit_version: "1.0"
  scan_mode: BROAD_BASELINE | ACTIVE_SESSION_REFRESH | SINGLE_INSTRUMENT | CUSTOM_SYMBOLS
  generated_at_vn: "YYYY-MM-DD HH:mm:ss ICT"
  timezone: Asia/Ho_Chi_Minh
  required_bucket_ids:
    - FX
    - EQUITY_INDICES
    - RATES_SOVEREIGN_BONDS
    - VOLATILITY
    - PRECIOUS_METALS
    - INDUSTRIAL_BASE_METALS
    - ENERGY
    - AGRICULTURE_SOFTS
    - LIVESTOCK
    - EMISSIONS_ENVIRONMENTAL
    - FERTILIZER_CHEMICALS
    - LIQUID_STOCKS
  session:
    session_id: null
    window: ASIA | EUROPE | US_PREOPEN | US_CASH | OVERNIGHT | ALL | null
    assessed_at_vn: null
    ict_timezone: Asia/Ho_Chi_Minh
  baseline_reuse:
    reuse_status: NEW_BASELINE | REUSED | NOT_REUSED | NOT_APPLICABLE
    baseline_acquisition_id: null
    baseline_acquired_at_vn: null
    baseline_age_seconds: null
    reused_fields: []
    refreshed_fields: []
    disclosure: null
  totals:
    required_bucket_count: 12
    bucket_row_count: 0
    attempted_instrument_count: 0
    succeeded_instrument_count: 0
    failed_instrument_count: 0
    configured_reference_gap_count: 0
    covered_bucket_count: 0
    partial_bucket_count: 0
    gap_bucket_count: 0
    skipped_bucket_count: 0
    not_scanned_bucket_count: 0
    promoted_instrument_count: 0
    not_promoted_instrument_count: 0
    rejected_instrument_count: 0
  bucket_rows:
    - bucket_id: FX | EQUITY_INDICES | RATES_SOVEREIGN_BONDS | VOLATILITY | PRECIOUS_METALS | INDUSTRIAL_BASE_METALS | ENERGY | AGRICULTURE_SOFTS | LIVESTOCK | EMISSIONS_ENVIRONMENTAL | FERTILIZER_CHEMICALS | LIQUID_STOCKS
      required_for_baseline: true
      scan_state: ATTEMPTED | NOT_SCANNED
      coverage_outcome: COVERED | PARTIAL | GAP | SKIPPED | NOT_SCANNED
      representative_instruments: []
      session_state: OPEN | PREOPEN | AFTER_HOURS | CLOSED | HALTED | HOLIDAY | UNKNOWN | MIXED | NOT_SCANNED
      session_evidence:
        - instrument_key: null
          provider_market_state: OPEN | PREOPEN | AFTER_HOURS | CLOSED | HALTED | HOLIDAY | UNKNOWN
          provider_market_state_raw: null
          status_source: null
          status_time_vn: null
          status_observed_at_vn: null
      instrument_attempt_count: 0
      instrument_success_count: 0
      instrument_failure_count: 0
      promoted_count: 0
      not_promoted_count: 0
      rejected_count: 0
      reason_codes: []
      plain_reason: null
      instrument_attempts:
        - instrument_key: null
          public_symbol: null
          intended_broker_symbol: null
          attempt_state: SUCCEEDED | FAILED | NOT_SCANNED
          promotion_state: PROMOTED | NOT_PROMOTED | REJECTED | NOT_SCANNED
          readiness: READY_NOW | NEAR_READY | REJECT | null
          provider_market_state: OPEN | PREOPEN | AFTER_HOURS | CLOSED | HALTED | HOLIDAY | UNKNOWN
          provider_market_state_raw: null
          status_source: null
          status_time_vn: null
          status_observed_at_vn: null
          source_identifier_or_url: null
          reason_codes: []
          plain_reason: null
  material_unpromoted_or_rejected: []

handoff:
  execution_ready: false
  manual_advisory_only: true
  manual_advisory_data_sufficient: false
  directional_decision_ready: false
  platform_translation_required: true
  decision_critical_missing_fields: []
  delay_accepted_or_disclosed: false
  decision_contract_failures: []
  blocking_reason: null
  journal_reference: null
```

## 3. Source-Attempt Structure

Record every source attempt with enough detail to reproduce a failure:

```yaml
source_attempt:
  purpose: market_quote | bars | event | filing | cross_market | instrument_spec | lifecycle
  source_class: official | public_market | public_news | search
  source_name: null
  source_identifier_or_url: null
  attempt_time_vn: null
  result: success | stale | unavailable | unauthorized | rate_limited | rejected
  fields_received: []
  note: null
```

`source_class` may never represent an authenticated XTB or broker source.
Google-assisted discovery, Investing.com/public market pages, official
publishers, and public news are allowed. Real-time XTB values are not acquired
by this skill; record them later as `USER_PROVIDED_REALTIME`.

## 4. Coverage-Audit Structure and Reason Vocabulary

`coverage_audit` is the single canonical record of breadth coverage for every
`BROAD_BASELINE` and `ACTIVE_SESSION_REFRESH` acquisition. It is additive to
the existing 2.3 package shape: readers that only understand 2.3 may ignore the
new field, while 2.4 producers must populate it for an open-ended scan.

Each audit has one `bucket_rows` entry for every `required_bucket_ids` value,
including buckets that were not scanned. `COVERED` means at least one usable
public reference was attempted successfully; it does not mean that a trade was
promoted. `PARTIAL` means an attempted bucket has a material provider failure
or configuration gap. `GAP` means no usable configured public reference was
available. `SKIPPED` is allowed only when the supported reason is a closed or
inactive session, unusable public data, or no liquid identifiable instrument.
`NOT_SCANNED` is required for a refresh bucket outside the refresh scope and
must carry `NOT_IN_REFRESH_SCOPE` rather than implying a new full baseline.

The normalized `provider_market_state` enum is exactly `OPEN`, `PREOPEN`,
`AFTER_HOURS`, `CLOSED`, `HALTED`, `HOLIDAY`, or `UNKNOWN`. Preserve the raw
provider value when exposed. Every state observation needs `status_source`,
the provider status time when available, and the ICT observation time. A bucket
may use `MIXED` or `NOT_SCANNED` only for its aggregate `session_state`.

Use only the following stable reason codes for audit causes; a producer may add
more specific codes only without changing the meaning of these values:

- `MARKET_CLOSED`: the provider exposes a closed, halted, or holiday state.
- `SESSION_INACTIVE`: the provider exposes pre-open or after-hours state, or
  the declared session is inactive for the reference.
- `STALE_TRIGGER_DATA`: the completed trigger data exceeds its stated
  freshness limit.
- `NO_COMPLETED_TRIGGER`: no completed, mechanically checkable trigger is
  available.
- `MIXED_TIMEFRAME_STRUCTURE`: required timeframes do not align.
- `TRIGGER_INTEGRITY_FAILED`: the current public reference invalidates the
  completed trigger.
- `OUTSIDE_VALID_ENTRY_ZONE` and `OVEREXTENDED`: the current public reference
  is outside the allowed entry zone or stretched beyond the stated threshold.
- `INSUFFICIENT_REWARD_RISK`: the available public structure cannot support the
  applicable reward/risk gate.
- `EVENT_RISK`: a recorded material event is inside the rule's cutoff.
- `SOURCE_UNAVAILABLE`: a permitted public source failed or returned unusable
  data.
- `IDENTITY_OR_BASIS_UNRESOLVED`: instrument identity, contract, or price basis
  cannot be reconciled.
- `NO_LIQUID_IDENTIFIABLE_INSTRUMENT`: no liquid, identifiable public
  instrument exists for the bucket.
- `NOT_IN_REFRESH_SCOPE`: a non-core bucket was deliberately not refreshed;
  it is not evidence of a new full scan.
- `NO_CONFIGURED_PUBLIC_REFERENCE`: the scanner configuration has no approved
  public reference. This is required for `ALUMINIUM` and `EMISS` until a
  reviewed reference is configured.

`NOT_REQUESTED_BY_CALLER` and `LOWER_RANKED_THAN_SHORTLIST` are permitted
additional mechanical codes for a custom-symbol call and a data-valid candidate
that did not fit the requested shortlist limit. They do not replace a material
market-state reason.

`baseline_reuse` is mandatory for `ACTIVE_SESSION_REFRESH`. If a baseline is
reused, populate its acquisition ID, acquired time, age, the metadata reused,
and the exact quotes/bars/status/events refreshed. If no baseline was supplied
or reused, say so with `NOT_REUSED`; never imply that a session-core refresh is
a new full baseline. A broker symbol, XTB quote, spread, account value, or any
other `USER_PROVIDED_REALTIME` field is not a coverage attempt and must never
be a market-skip reason.

## 5. Handoff Rules

Send the data mode and public/delayed limitation with every package passed to `$trade-decision-guardrails`. A package is manual-advisory only and never an executable quote. A `PARTIAL` package may continue when all decision-critical fields are usable. A `BLOCKED` package caused by ambiguity or missing data must produce `WAIT_FOR_DATA`. A package blocked by `UNSUPPORTED_ASSET_CLASS_CRYPTO` must produce `NO_TRADE` and `DO_NOT_CLICK`, with no directional plan, trade levels, sizing, or execution guidance.

Set `manual_advisory_data_sufficient: true` when:

- the decision horizon, instrument identity, public reference basis, currency, and decision-critical fields are explicit;
- required quote and bar series have known provider/observation times and enough coverage for the selected analysis;
- missing fields are explicitly classified as noncritical;
- no unresolved identity, timestamp, session, lifecycle, adjustment, roll, gap, duplicate, OHLC, currency, or material price-conflict error remains;
- every material field has a source and observation/provider timestamp.

Provider delay is acceptable when disclosed. If it is material relative to the
horizon, keep the package sufficient but require a conditional public entry
area followed by user-provided XTB real-time confirmation.

For `HYBRID_M5`, public H1/M15 context may remain directionally sufficient
while the trigger is not executable. If M5 lag is at least 300 seconds, set
the candidate to `NEAR_READY`, set
`trigger_data_state: NEEDS_USER_REALTIME`, and request only the promoted
candidate's current completed M5 bar and executable-side quote. `READY_NOW`
requires a completed, fresh M5 trigger plus a current price that preserves the
trigger and bounded entry zone.

Keep `execution_ready: false` in every case. Broker/account access is
prohibited for this skill. Missing broker symbol, bid/ask,
spread, account equity, open risk, or value per point must not set
`manual_advisory_data_sufficient: false` when the public directional evidence
is otherwise complete. Set `directional_decision_ready: true` and
`platform_translation_required: true` instead.

`READY_NOW` means ready for the decision layer now, not executable at the
public price. `NEAR_READY` must name one observable missing market condition.
Do not use account or platform fields as that missing market condition.

Log source attempts and the final status through `$trade-journal-review`.
Real-time XTB values may appear only later with source
`USER_PROVIDED_REALTIME`; never request or log credentials.
