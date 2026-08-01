# Manual Advisory Journal Schema

```yaml
journal_event:
  schema_version: "2.3"
  journal_event_id: null
  event_type: SESSION_STATE | SCAN_REFRESH | CANDIDATE_PROMOTED | ACQUISITION | DECISION | RISK_PLAN | MANUAL_TICKET_CHECK | NO_TRADE | WAIT_FOR_DATA | USER_SKIPPED | USER_ENTERED | USER_UPDATED_POSITION | USER_EXITED | USER_OUTCOME_REPORTED | BASIS_INCIDENT | REVIEW | CORRECTION
  occurred_at_source: null
  occurred_at_vn: null
  recorded_at_vn: null
  mode: MANUAL_ADVISORY
  session_id: null
  source_of_fact: PUBLIC_SOURCE | AGENT_ANALYSIS | USER_PROVIDED_REALTIME | USER_REPORT
  links:
    acquisition_id: null
    strategy_id: null
    strategy_version: null
    validation_id: null
    decision_id: null
    risk_plan_id: null
    corrected_event_id: null
  instrument:
    symbol: null
    public_reference_basis: null
    actual_user_instrument: null
    currency: null
  payload: {}
  source_references: []
  stated_delay_seconds: null
  data_quality_flags: []
  control_flags: []
  control_scope:
    session_id: null
    masked_account_alias: null
    broker_symbol: null
    contract_id: null
  plan_deviations: []
  journal_status: SCAN_RECORDED | CANDIDATE_PROMOTED | AWAITING_USER_REPORT | USER_SKIPPED | POSITION_OPEN_REPORTED | POSITION_CLOSED_REPORTED | REVIEWED
```

Schema 2.3 is additive. Existing append-only 2.2 events remain valid and must
not be rewritten, reordered, or backfilled merely to add a scan audit.

## Compact Immutable Scan-Audit Payload

For a `SCAN_REFRESH` or material `ACQUISITION` event created from an
open-ended scan, store this compact immutable projection of the canonical
acquisition `coverage_audit` in `payload.scan_coverage_audit`:

```yaml
scan_coverage_audit:
  acquisition_schema_version: "2.4"
  audit_version: "1.0"
  acquisition_id: null
  scan_mode: BROAD_BASELINE | ACTIVE_SESSION_REFRESH | SINGLE_INSTRUMENT | CUSTOM_SYMBOLS
  generated_at_vn: null
  session:
    session_id: null
    window: null
    assessed_at_vn: null
  baseline_reuse:
    reuse_status: NEW_BASELINE | REUSED | NOT_REUSED | NOT_APPLICABLE
    baseline_acquisition_id: null
    baseline_age_seconds: null
    reused_fields: []
    refreshed_fields: []
    disclosure: null
  totals:
    attempted_instrument_count: 0
    succeeded_instrument_count: 0
    failed_instrument_count: 0
    covered_bucket_count: 0
    partial_bucket_count: 0
    gap_bucket_count: 0
    skipped_bucket_count: 0
    not_scanned_bucket_count: 0
  bucket_rows:
    - bucket_id: null
      coverage_outcome: COVERED | PARTIAL | GAP | SKIPPED | NOT_SCANNED
      representative_instruments: []
      session_state: OPEN | PREOPEN | AFTER_HOURS | CLOSED | HALTED | HOLIDAY | UNKNOWN | MIXED | NOT_SCANNED
      reason_codes: []
      plain_reason: null
  material_unpromoted_or_rejected:
    - instrument_key: null
      promotion_state: NOT_PROMOTED | REJECTED | NOT_SCANNED
      reason_codes: []
      plain_reason: null
```

Copy values without reinterpretation. The journal projection is compact but
must preserve every required bucket outcome and all material unpromoted,
rejected, skipped, or gap reasons. It never stores XTB/broker/account values as
coverage evidence, and those values cannot become a scan-skip reason.

## Frozen Plan Payload

```yaml
frozen_manual_plan:
  decision: LONG | SHORT | NO_TRADE | WAIT_FOR_DATA
  framework_status: VALIDATED_SYSTEMATIC | UNVALIDATED_DISCRETIONARY
  strategy_validation_status: REJECTED | RESEARCH_ONLY | FORWARD_OBSERVATION | SUSPENDED | ADVISORY_VALIDATED
  entry_timing_mode: M15 | HYBRID_M5
  timeframe_roles:
    regime: H1
    setup: M15
    trigger: M15 | M5
  trigger_bar_completed_at_vn: null
  trigger_data_source: PUBLIC_SOURCE | USER_PROVIDED_REALTIME | null
  current_quote_age_seconds: null
  higher_timeframe_alignment_confirmed: null
  observed_public_price: null
  entry_trigger_or_zone: null
  stop_loss: null
  invalidation: null
  targets_or_exit_rules: []
  signal_expires_at_vn: null
  cancel_conditions: []
  gross_reward_risk: null
  estimated_net_reward_risk: null
  spread_to_stop_fraction: null
  total_cost_r: null
  break_even_win_rate: null
  indicative_quantity: null
  limitations: []
```

## User Outcome Payload

```yaml
user_reported_outcome:
  entered: null
  actual_instrument: null
  side: null
  entry_time_vn: null
  entry_price: null
  quantity: null
  exit_time_vn: null
  exit_price: null
  fees: null
  financing_or_borrow_cost: null
  gross_pnl: null
  net_pnl: null
  realized_r_multiple: null
  maximum_adverse_excursion_r: null
  maximum_favorable_excursion_r: null
  trigger_to_entry_latency_seconds: null
  false_trigger: null
  exit_reason: STOP | TARGET | MANUAL | EXPIRY | OTHER | null
  notes: null
  missing_fields: []
```

## Review Rules

- Never convert a proposal into an entered trade without an explicit user report.
- Never acquire XTB data directly. Record current XTB values only as
  `USER_PROVIDED_REALTIME`.
- Use `AWAITING_USER_REPORT` only for a translated manual ticket or explicit
  action instruction. A scan and public-reference plan use `SCAN_RECORDED` or
  `CANDIDATE_PROMOTED`.
- Preserve skipped, no-trade, and missing-report cases.
- Compute performance only from supplied actual values and declared formulas.
- Compare the user-reported result with the original frozen plan, not a revised hindsight plan.
- Set `BASIS_INCIDENT_LOCK_ACTIVE` when reported broker execution cannot be
  reconciled with the public-reference path. Scope it to exact account alias,
  platform symbol, and contract; keep it active until platform symbol,
  bid/ask, spread, quote time, and contract basis are verified. Do not apply it
  to unrelated instruments.
- Derive consecutive loss and session-stop controls only from explicit stopped
  outcomes carrying the active `session_id`. Old expired proposals and
  unreported tickets do not count as losses.
- Suppress duplicate blocker events when session, instrument, missing fields,
  and source state are unchanged.
- Do not infer directional-edge failure from one stopped trade.
- For an open-ended scan, keep `payload.scan_coverage_audit` immutable and
  append a new event for a material refresh rather than rewriting its baseline
  audit. Old 2.2 events remain valid without this field.
