# Strategy Specification Schema

```yaml
strategy_spec:
  schema_version: "1.1"
  strategy_id: null
  version: null
  status: RESEARCH_ONLY | REJECTED_SCOPE
  created_at_vn: null
  code_or_config_hash: null
  change_reason: null
  hypothesis:
    rationale: null
    expected_failure_conditions: []
  scope:
    asset_classes: []
    instruments: []
    instrument_basis: []
    venue_or_reference: []
    sessions: []
    decision_horizon: null
    holding_horizon: null
    decision_windows: []
    target_qualified_opportunities_per_week: null
    maximum_no_setup_session_fraction: null
    long_allowed: true
    short_allowed: true
  data_contract:
    required_timeframes: []
    required_fields: []
    minimum_bar_counts: {}
    completed_bar_policy: null
    maximum_quote_age_seconds: null
    maximum_completed_bar_lag_seconds: {}
    event_lookback_hours: null
    event_lookahead_hours: null
    allowed_sessions: []
    exchange_timezone: null
    equity_adjustment_method: null
    futures_roll_method: null
    missing_or_stale_action: WAIT_FOR_DATA
  features:
    - feature_id: null
      formula: null
      input_fields: []
      lookback: null
      alignment: null
      warmup: null
  rules:
    regime: []
    setup: []
    trigger: []
    filters: []
    entry: []
    initial_stop: []
    invalidation: []
    exits: []
    signal_expiry: []
    no_trade: []
    precedence: []
    readiness:
      ready_now: []
      near_ready: []
      reject: []
  execution_assumptions:
    allowed_order_types: []
    default_translation_mode: REQUEST_USER_REALTIME_THEN_MARKET
    autonomous_alerts_allowed: false
    pretrigger_pending_orders_allowed: false
    fill_model: null
    latency_model: null
    spread_model: null
    slippage_model: null
    fees: null
    financing: null
    borrow: null
    roll_cost: null
    currency_conversion: null
    liquidity_constraints: null
  sizing_interface:
    risk_policy_required: true
    maximum_unbounded_loss_allowed: false
    averaging_down_allowed: false
  predeclared_validation_gates:
    minimum_trade_count_or_coverage: null
    minimum_net_expectancy: null
    maximum_drawdown: null
    maximum_tail_loss: null
    robustness_requirements: []
    calibration_requirements: []
    paper_forward_duration: null
    minimum_qualified_opportunities_per_session_or_week: null
    minimum_ready_now_frequency: null
    minimum_candidate_to_ticket_conversion: null
    maximum_platform_translation_miss_rate: null
    monitoring_thresholds: {}
  limitations: []
  forbidden_discretionary_overrides: []
```

## Determinism Rules

- If the primary underlying/reference is a cryptoasset, set
  `status: REJECTED_SCOPE`, record
  `UNSUPPORTED_ASSET_CLASS_CRYPTO` in limitations, and do not populate trading
  rules or a sizing interface.
- Give every feature and rule a stable ID.
- Define formula inputs, time alignment, and comparison operators exactly.
- Define what happens at equality, missing data, session boundaries, gaps, halts, expiry, and simultaneous stop/target touches.
- Never select validation thresholds after seeing the untouched test.
- Keep all current opportunities out of the final test period used to justify the same strategy version.
