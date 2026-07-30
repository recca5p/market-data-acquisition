# Manual Trade Decision Contract

```yaml
manual_trade_decision:
  schema_version: "2.2"
  decision_id: null
  created_at_vn: null
  decision: LONG | SHORT | NO_TRADE | WAIT_FOR_DATA
  decision_reason_code: null
  setup_type: TREND_PULLBACK | BREAKOUT_CLOSE | FAILED_BREAKOUT | NONE
  setup_readiness: READY_NOW | NEAR_READY | REJECT
  execution_state: PLATFORM_TICKET_READY | NEEDS_USER_REALTIME | DIRECTION_ONLY
  xtb_interaction_allowed: false
  framework_status: VALIDATED_SYSTEMATIC | UNVALIDATED_DISCRETIONARY
  control_state:
    basis_incident_lock: CLEAR | ACTIVE
    basis_incident_scope: null
    session_id: null
    session_state: CONFIRMED | PARTIAL | UNKNOWN
    consecutive_reported_session_losses: null
    replacement_risk_cap_fraction: null
  identity:
    acquisition_id: null
    strategy_id: null
    strategy_version: null
    validation_id: null
    requested_instrument: null
    resolved_public_instrument: null
    asset_class: null
    public_reference_basis: null
    decision_horizon: null
  data_state:
    acquisition_status: COMPLETE | PARTIAL | BLOCKED
    observed_public_price: null
    provider_time: null
    stated_delay_seconds: null
    observed_at_vn: null
    decision_critical_fields_present: false
    delay_material_to_horizon: null
    quality_flags: []
  platform_snapshot:
    source: USER_PROVIDED_REALTIME | null
    broker_symbol: null
    observed_at_vn: null
    bid: null
    ask: null
    spread: null
    displayed_quantity: null
    pip_or_point_value: null
    displayed_margin: null
    displayed_fee: null
    displayed_swap_buy: null
    displayed_swap_sell: null
    supported_ticket_tabs: []
    public_to_platform_basis_verified: false
  evidence:
    higher_timeframe_structure: []
    trigger_timeframe_structure: []
    momentum_and_volatility: []
    events_and_cross_markets: []
    supporting_facts: []
    conflicting_facts: []
  public_reference_plan:
    label: NON_EXECUTABLE_REFERENCE
    entry_zone: { low: null, high: null }
    stop_loss: null
    invalidation: null
    targets_or_exit_rules: []
    gross_reward_risk: null
    estimated_net_reward_risk: null
    valid_until_vn: null
  manual_plan:
    side: BUY | SELL | null
    quantity: null
    quantity_source: RISK_CALCULATED | USER_SELECTED_NOT_APPROVED | NOT_CALCULATED
    order_mode: MARKET | STOP_LIMIT | REQUEST_USER_REALTIME | DO_NOT_CLICK
    order_type: MARKET | BUY_STOP | SELL_STOP | BUY_LIMIT | SELL_LIMIT | null
    broker_symbol: null
    platform_bid: null
    platform_ask: null
    platform_basis_verified: false
    entry_trigger: null
    entry_zone: { low: null, high: null }
    stop_loss: null
    invalidation: null
    targets_or_exit_rules: []
    signal_expires_at_vn: null
    cancel_conditions: []
    gross_reward_risk: null
    estimated_cost_per_unit: null
    estimated_net_reward_risk: null
    risk_tier: BASE | REDUCED | REJECT
    target_r_multiple: null
    valid_market_entry_zone: { low: null, high: null }
    time_stop_at_vn: null
    event_cutoff_at_vn: null
  uncertainty:
    qualitative_confidence: LOW | MEDIUM | HIGH | null
    calibrated_probability: null
    calibration_reference: null
    limitations: []
  manual_execution:
    agent_may_submit_orders: false
    verify_platform_price: true
    verify_spread_and_instrument: true
    platform_ticket_mapping_required: false
    compact_user_realtime_fields_needed: []
    user_report_required: false
  handoff:
    risk_plan_eligible: false
    journal_status: CANDIDATE_PROMOTED | AWAITING_USER_REPORT
    journal_reference: null
```

## Invariants

- If `basis_incident_lock: ACTIVE`, scope it to the affected broker instrument
  or contract. A usable public package may still produce `LONG` or `SHORT`,
  `execution_state: NEEDS_USER_REALTIME`, and a populated
  `public_reference_plan`. Require `manual_plan.order_mode:
  REQUEST_USER_REALTIME`, keep all user-editable platform ticket fields and
  quantity null, and set
  `manual_execution.platform_ticket_mapping_required: true`.
- If the primary underlying/reference is a cryptoasset, require
  `decision: NO_TRADE`,
  `decision_reason_code: UNSUPPORTED_ASSET_CLASS_CRYPTO`,
  `manual_plan.order_mode: DO_NOT_CLICK`, and
  `handoff.risk_plan_eligible: false`; leave all trade levels and quantity
  null.
- Use `BUY` only with `LONG` and `SELL` only with `SHORT`.
- Require a finite stop, exit/target, and expiry for `LONG` or `SHORT`.
- Delayed public data is acceptable when disclosed; use a conditional trigger if delay is material.
- Keep quantity null unless sufficient risk and instrument inputs are supplied later.
- A user-selected platform quantity may be preserved only with `quantity_source: USER_SELECTED_NOT_APPROVED`.
- `BUY_STOP` must trigger above the platform ask; `SELL_STOP` below the platform bid; `BUY_LIMIT` below the platform ask; and `SELL_LIMIT` above the platform bid.
- Do not emit platform entry, stop, or target prices derived from an external reference until `platform_basis_verified: true`.
- Use `REQUEST_USER_REALTIME`, not `WAIT_FOR_DATA`, when the public directional
  plan is valid but user-provided XTB basis data is absent. Reserve
  `DO_NOT_CLICK` for prohibited assets, hard session stops, invalid/expired
  plans, or a rejected ticket.
- Never invoke a broker connector or access XTB. Accept XTB values only with
  `source: USER_PROVIDED_REALTIME`. Their absence does not block the public
  directional plan.
- Keep `manual_execution.user_report_required: false` and
  `handoff.journal_status: CANDIDATE_PROMOTED` for a public-reference plan.
  Change them to `true` and `AWAITING_USER_REPORT` only after platform
  translation produces an explicit manual action.
- Never emit a claimed fill or an executable quote.
- For `user-cfd-usd-2000-v1`, reject estimated net reward-to-risk below `1.5`,
  use reduced risk from `1.5` through `1.79`, require `1.8` for base risk, and
  prefer `2.0`.
- A Market ticket is valid only while the platform quote remains inside
  `valid_market_entry_zone`.
- Session-loss and session-override flags apply only to their exact
  `session_id`; expired prior-session flags cannot block a current decision.
- `READY_NOW` requires a completed trigger bar and a currently valid bounded
  public-reference entry zone. `NEAR_READY` must name exactly one missing
  market condition and cannot be presented as an executable ticket.
- Public-reference numbers must never be placed in `manual_plan` ticket fields
  before platform translation.
