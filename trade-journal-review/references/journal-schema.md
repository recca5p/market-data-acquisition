# Manual Advisory Journal Schema

```yaml
journal_event:
  schema_version: "2.1"
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

## Frozen Plan Payload

```yaml
frozen_manual_plan:
  decision: LONG | SHORT | NO_TRADE | WAIT_FOR_DATA
  framework_status: VALIDATED_SYSTEMATIC | UNVALIDATED_DISCRETIONARY
  observed_public_price: null
  entry_trigger_or_zone: null
  stop_loss: null
  invalidation: null
  targets_or_exit_rules: []
  signal_expires_at_vn: null
  cancel_conditions: []
  gross_reward_risk: null
  estimated_net_reward_risk: null
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
