# Public Market-Data Acquisition Schema

## Contents

1. Status values
2. Required result structure
3. Source-attempt structure
4. Handoff rules

## 1. Status Values

- `COMPLETE`: every requested public-data field is sourced, timestamped, and labelled with its instrument basis and delay/uncertainty.
- `PARTIAL`: a requested public-data field is unavailable, stale, contradictory, or insufficiently identified.
- `BLOCKED`: the requested market/instrument is prohibited crypto, is ambiguous, or an essential public source cannot be accessed without bypassing restrictions.

## 2. Required Result Structure

```yaml
acquisition:
  schema_version: "2.3"
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

## 4. Handoff Rules

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
