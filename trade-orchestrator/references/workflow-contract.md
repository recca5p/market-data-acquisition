# Manual Advisory Workflow Contract

## Core Skills

1. `$market-data-acquisition`
2. `$trade-decision-guardrails`
3. `$portfolio-risk-manager`
4. `$trade-journal-review`

Optional:

- `$trade-strategy-specification` and `$strategy-validation` for repeatable systematic strategies;
- `$order-execution-controls` for local arithmetic and manual-ticket validation only;
- `$broker-account-snapshot` only when the user explicitly requests optional account-aware sizing.

The skills have no XTB or broker access. Absence of user-provided real-time or
account data does not block a public-reference manual advisory.

## State Machine

```text
START
  -> ASSET_CLASS_GATE
     -> CRYPTO: NO_TRADE + DO_NOT_CLICK
     -> SUPPORTED: SESSION_BOOTSTRAP
  -> SESSION_BOOTSTRAP
     -> CURRENT SESSION CONTROLS
     -> PRIOR SESSION STOP FLAGS EXPIRE
  -> BROAD_BASELINE | ACTIVE_SESSION_REFRESH
  -> ENTRY_TIMING_MODE
     -> M15: COMPLETED_M15_TRIGGER
     -> HYBRID_M5: H1_M15_CONTEXT + COMPLETED_M5_TRIGGER
  -> RANK READY_NOW / NEAR_READY / REJECT
  -> DIRECTIONAL_DECISION
     -> PUBLIC DATA UNUSABLE: WAIT_FOR_DATA
     -> NO EDGE: NO_TRADE
     -> LONG/SHORT: PUBLIC_REFERENCE_PLAN
  -> MANUAL_RISK_PLAN
     -> MISSING ACCOUNT INPUTS: PLAN_PARTIAL
  -> PLATFORM_TRANSLATION
     -> USER PROVIDED CURRENT BASIS: PLATFORM_TICKET
     -> USER DATA ABSENT: REQUEST_USER_REALTIME
  -> OPTIONAL_TICKET_CHECK
  -> PRESENT_TO_USER
     -> PUBLIC PLAN ONLY: CANDIDATE_PROMOTED
     -> TRANSLATED MANUAL ACTION: AWAITING_USER_REPORT
  -> OUTCOME_REVIEW
```

## Shared Identity

```yaml
workflow_identity:
  workflow_id: null
  mode: MANUAL_ADVISORY
  acquisition_id: null
  decision_id: null
  risk_plan_id: null
  strategy_id: null
  strategy_version: null
  validation_id: null
  journal_reference: null
  session_id: null
  entry_timing_mode: M15 | HYBRID_M5
  strategy_validation_status: REJECTED | RESEARCH_ONLY | FORWARD_OBSERVATION | SUSPENDED | ADVISORY_VALIDATED
```

Strategy and validation IDs may be null for a one-off discretionary analysis. Instrument basis, source timestamps, and delay labels may not be null.

## Terminal Result

```yaml
workflow_result:
  mode: MANUAL_ADVISORY
  xtb_interaction_allowed: false
  realtime_execution_data_source: USER_PROVIDED_REALTIME
  basis_incident_lock: CLEAR | ACTIVE
  basis_incident_scope: null
  status: DIRECTION_READY | PLAN_READY | PLAN_PARTIAL | NO_TRADE | WAIT_FOR_DATA
  decision: LONG | SHORT | NO_TRADE | WAIT_FOR_DATA
  decision_reason_code: null
  setup_type: TREND_PULLBACK | BREAKOUT_CLOSE | FAILED_BREAKOUT | NONE
  setup_readiness: READY_NOW | NEAR_READY | REJECT
  execution_state: PLATFORM_TICKET_READY | NEEDS_USER_REALTIME | DIRECTION_ONLY
  framework_status: VALIDATED_SYSTEMATIC | UNVALIDATED_DISCRETIONARY
  entry_timing:
    mode: M15 | HYBRID_M5
    regime_timeframe: H1
    setup_timeframe: M15
    trigger_timeframe: M15 | M5
    higher_timeframe_alignment_confirmed: null
    trigger_bar_completed: null
    trigger_bar_completed_at_vn: null
    trigger_data_state: PUBLIC_COMPLETED | STALE | NEEDS_USER_REALTIME | USER_PROVIDED_REALTIME
    current_quote_age_seconds: null
  platform_ticket:
    source: USER_PROVIDED_REALTIME | null
    action: MARKET | STOP_LIMIT | REQUEST_USER_REALTIME | DO_NOT_CLICK
    order_type: MARKET | BUY_STOP | SELL_STOP | BUY_LIMIT | SELL_LIMIT | null
    button: BUY | SELL | null
    broker_symbol: null
    quantity: null
    quantity_source: USER_SELECTED | INDICATIVE_ONLY | NOT_CALCULATED
    current_bid: null
    current_ask: null
    entry_or_trigger_price: null
    stop_loss_enabled: false
    stop_loss_price: null
    take_profit_enabled: false
    take_profit_price: null
  user_realtime_request:
    status: REQUIRED | SATISFIED | NOT_NEEDED
    ask_once: true
    accepted_formats: [TEXT, SCREENSHOT, EXPORT]
    required_fields:
      - broker_symbol
      - bid
      - ask
      - spread
      - quote_time
      - value_per_point_or_pip
    hybrid_m5_fields_if_needed:
      - latest_completed_m5_open_time
      - latest_completed_m5_close_time
      - latest_completed_m5_ohlc
    sizing_fields_if_needed:
      - equity
      - open_positions
      - working_orders
  manual_trade_card:
    instrument: null
    public_reference_basis: null
    observed_public_price: null
    source_time: null
    stated_delay: null
    observed_at_vn: null
    entry_trigger_or_zone: null
    stop_loss: null
    invalidation: null
    targets_or_exit_rules: []
    gross_reward_risk: null
    estimated_net_reward_risk: null
    confirmed_equity_used: null
    account_profile_status: PLANNED_PENDING_BROKER_CONFIRMATION | ACTIVE_CONFIRMED | NOT_USED
    risk_budget_amount: null
    estimated_loss_at_stop: null
    estimated_net_profit_at_target: null
    estimated_risk_fraction: null
    remaining_daily_loss_budget: null
    remaining_portfolio_heat_budget: null
    remaining_correlated_heat_budget: null
    time_stop_at_vn: null
    event_cutoff_at_vn: null
    signal_expires_at_vn: null
    cancel_conditions: []
    indicative_quantity: null
    public_reference_label: NON_EXECUTABLE_REFERENCE
  user_must_verify: []
  blockers_or_limitations: []
  journal_status: SCAN_RECORDED | CANDIDATE_PROMOTED | AWAITING_USER_REPORT
  journal_reference: null
```

`DIRECTION_READY` contains a valid public-basis LONG/SHORT plan whose exact
platform translation is still needed. `PLAN_PARTIAL` may contain valid
public-basis or translated entry geometry when quantity or account-specific
risk is unavailable.

When `basis_incident_lock: ACTIVE`, scope it to the affected instrument or
contract. Scanning and public-basis LONG/SHORT geometry may continue. Keep all
user-editable platform ticket fields and quantity null for the affected scope,
set `platform_ticket.action: REQUEST_USER_REALTIME`, and require a current
user-provided XTB quote to clear the lock.

Apply the asset-class gate before public-data acquisition. Crypto spot,
perpetuals, futures, options, CFDs, and crypto-tracking ETPs/ETFs must terminate
with `status: NO_TRADE`, `decision: NO_TRADE`,
`decision_reason_code: UNSUPPORTED_ASSET_CLASS_CRYPTO`, and
`platform_ticket.action: DO_NOT_CLICK`. Leave every trade level and quantity
null. Do not route a prohibited instrument to risk sizing or ticket checks.

When a platform screenshot is available, `platform_ticket` is the primary
user-facing result. Do not expose external-reference levels as ticket inputs
until they are reconciled to the broker symbol and price scale.

When a platform quote is absent, a usable public package must not become
`WAIT_FOR_DATA`. Return `DIRECTION_READY`, preserve the non-executable public
plan, set `execution_state: NEEDS_USER_REALTIME`, and request from the user
only symbol, bid, ask, spread, quote time, and matching point value needed for
translation/sizing. Never attempt to obtain these values from XTB.

For `HYBRID_M5`, H1/M15 can make the direction package sufficient while a
stale M5 trigger keeps the candidate `NEAR_READY`. A public M5 lag of at least
300 seconds requires `NEEDS_USER_REALTIME` and the promoted candidate's latest
completed M5 OHLC/time. Only current quote and M5 trigger data may advance it
to `READY_NOW`.

Session stops and consecutive-loss counts are scoped to `session_id`.
Unreported or expired proposals from earlier sessions remain missing-report
records but cannot block a new session's scan or directional decision.

For the `user-cfd-usd-2000-v1` profile, keep
`account_profile_status: PLANNED_PENDING_BROKER_CONFIRMATION` until a fresh
account snapshot supplied by the user confirms the funded equity. A planned
deposit cannot populate `confirmed_equity_used`.
