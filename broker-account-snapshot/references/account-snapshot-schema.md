# Broker Account Snapshot Schema

```yaml
broker_snapshot:
  schema_version: "2.2"
  snapshot_id: null
  parent_snapshot_id: null
  snapshot_kind: FULL_SESSION | DELTA_UPDATE
  session_id: null
  status: COMPLETE | PARTIAL | OPTIONAL_UNAVAILABLE
  environment: MANUAL_ADVISORY
  source: USER_PROVIDED_REALTIME
  xtb_interaction_allowed: false
  accepted_input_format: TEXT | SCREENSHOT | EXPORT
  broker: null
  venue: null
  masked_account_alias: null
  provider_time: null
  observed_at_vn: null
  user_reported_or_visible_quote_time: null
  expires_at_vn: null
  account:
    currency: null
    cash: null
    equity: null
    net_liquidation_value: null
    available_funds: null
    buying_power: null
    initial_margin_used: null
    maintenance_margin_used: null
    margin_call: null
    realized_pnl_today: null
    unrealized_pnl: null
    displayed_trading_value: null
    displayed_margin_ratio: null
  permissions:
    instrument_allowed: null
    long_allowed: null
    short_allowed: null
    order_types_allowed: []
    restrictions: []
  positions: []
  working_orders: []
  recent_orders: []
  instrument:
    requested_symbol: null
    broker_symbol: null
    asset_class: null
    contract_id: null
    expiry: null
    settlement_currency: null
    tick_size: null
    quantity_step: null
    minimum_quantity: null
    contract_multiplier: null
    value_per_price_unit: null
    supported_order_types: []
    trading_hours: null
    price_bands: null
    margin_per_unit: null
  executable_quote:
    bid: null
    ask: null
    last: null
    quote_time: null
    stated_delay_seconds: null
    market_status: null
    halted: null
  ticket_ui:
    market_tab_supported: null
    stop_limit_tab_supported: null
    visible_order_types: []
    selected_order_type: null
    selected_quantity: null
    contract_value: null
    displayed_margin: null
    spread: null
    fee: null
    pip_or_point_value: null
    swap_buy_per_day: null
    swap_sell_per_day: null
    stop_loss_input_supported: null
    take_profit_input_supported: null
  short_state:
    locate_required: null
    locate_available: null
    borrow_available: null
    estimated_borrow_fee_fraction: null
    recall_or_restriction_flags: []
  validation:
    missing_fields: []
    stale_fields: []
    contradictions: []
    reconciliation_errors: []
    unsupported_fields: []
  readiness:
    manual_risk_context_ready: false
    reusable_for_session: false
    valid_until_vn: null
    invalidated_at_vn: null
    invalidation_reason: null
    invalidation_conditions:
      - FILL_OR_EXIT
      - WORKING_ORDER_CHANGE
      - MATERIAL_PNL_OR_MARGIN_CHANGE
      - EXPLICIT_ACCOUNT_STATE_UPDATE
      - SNAPSHOT_EXPIRY
      - SESSION_END
    account_risk_profile_id: null
    account_risk_profile_status: PLANNED_PENDING_BROKER_CONFIRMATION | ACTIVE_CONFIRMED | NOT_USED
    confirmed_equity_used_for_sizing: null
    aggregate_open_stop_risk: null
    aggregate_pending_stop_risk: null
    remaining_daily_loss_budget: null
    remaining_portfolio_heat_budget: null
    remaining_correlated_heat_budget: null
    blockers: []
```

## Readiness Rules

- Compute optional sizing readiness against the named manual risk profile; do not use an implicit age threshold.
- Bind reuse to the exact `session_id`; a snapshot never carries into a new
  named session without an explicit refresh.
- Require exact instrument identity across snapshot and decision.
- Include working and pending orders in exposure and duplicate-order checks.
- Keep `manual_risk_context_ready: false` when required sizing, exposure, or instrument fields are missing; this leaves quantity null but does not block the directional plan.
- Return only masked account identifiers and never include authentication material.
- Reject any workflow that would require logging in, calling an API/connector,
  controlling XTB, or reading authenticated state. Ask the user for the
  missing values instead.
- Do not activate a planned-equity profile until a fresh screenshot or
  other current user-supplied snapshot confirms the funded equity.
- Prefer one `FULL_SESSION` baseline plus `DELTA_UPDATE` records after
  invalidation events. Do not require a duplicate full screenshot when the
  account identity is unchanged and a compact no-change confirmation is
  sufficient.
- For `user-cfd-usd-2000-v1`, use USD 40 maximum aggregate open risk, USD 30
  maximum correlated U.S.-equity risk, USD 40 daily loss, and USD 100 weekly
  loss only after activation.
