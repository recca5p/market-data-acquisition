# Manual Advisory Risk Contract

```yaml
manual_risk_profile:
  schema_version: "2.4"
  profile_id: null
  base_currency: null
  profile_status: PLANNED_PENDING_BROKER_CONFIRMATION | ACTIVE_CONFIRMED
  basis_incident_lock: CLEAR | ACTIVE
  basis_incident_scope:
    broker_symbol: null
    contract_id: null
    masked_account_alias: null
  session_id: null
  consecutive_reported_session_losses: null
  account_snapshot_id: null
  account_snapshot_valid_for_session: false
  xtb_interaction_allowed: false
  realtime_execution_data_source: USER_PROVIDED_REALTIME
  confirmed_equity_at: null
  minimum_reward_risk: null
  preferred_reward_risk: null
  entry_timing_mode: M15 | HYBRID_M5
  strategy_validation_status: REJECTED | RESEARCH_ONLY | FORWARD_OBSERVATION | SUSPENDED | ADVISORY_VALIDATED
  account_inputs:
    equity: null
    explicit_risk_amount: null
    risk_fraction: null
    remaining_daily_loss_budget: null
    remaining_portfolio_heat_budget: null
    remaining_correlated_heat_budget: null
    realized_pnl_today: null
    consecutive_losses_today: null
  instrument_inputs:
    asset_class: null
    value_per_price_unit: null
    contract_multiplier: null
    quantity_step: null
    minimum_quantity: null
    margin_per_unit: null
  platform_ticket_inputs:
    source: USER_PROVIDED_REALTIME
    broker_symbol: null
    bid: null
    ask: null
    spread: null
    selected_quantity: null
    selected_quantity_source: USER_SELECTED_NOT_APPROVED | null
    pip_or_point_value_for_selected_quantity: null
    contract_value: null
    displayed_margin: null
    fee: null
    swap_buy_per_day: null
    swap_sell_per_day: null
  cost_inputs:
    estimated_round_trip_fee_per_unit: null
    estimated_slippage_per_unit: null
    financing_and_borrow_buffer_per_unit: null
    spread_included_in_entry_exit_geometry: null
    maximum_spread_to_stop_fraction: null
    maximum_total_cost_r: null
  research_limits:
    research_risk_cap_fraction: null
  optional_limits:
    maximum_notional: null
    maximum_quantity: null
    maximum_leverage: null
    maximum_correlated_exposure: null
```

Null optional fields mean unknown, not zero.

## Risk Plan

```yaml
manual_risk_plan:
  risk_plan_id: null
  decision_id: null
  status: PLAN_READY | PLAN_PARTIAL | NO_TRADE
  execution_state: PUBLIC_PLAN_READY | NEEDS_USER_REALTIME | PLATFORM_TICKET_READY | SESSION_STOPPED
  session_id: null
  instrument: null
  asset_class: null
  rejection_reason: null
  public_reference_basis: null
  side: LONG | SHORT
  order_mode: MARKET | STOP_LIMIT | REQUEST_USER_REALTIME
  order_type: MARKET | BUY_STOP | SELL_STOP | BUY_LIMIT | SELL_LIMIT | null
  entry_for_calculation: null
  stop_loss: null
  stop_distance: null
  spread_to_stop_fraction: null
  total_cost_per_unit: null
  total_cost_r: null
  break_even_win_rate: null
  invalidation: null
  targets:
    - price: null
      gross_reward_risk: null
      estimated_net_reward_risk: null
  signal_expires_at_vn: null
  indicative_quantity: null
  quantity_label: INDICATIVE_ONLY | USER_SELECTED_NOT_APPROVED | NOT_CALCULATED
  displayed_quantity_estimated_loss_to_stop: null
  displayed_quantity_estimated_reward_by_target: []
  estimated_net_profit_by_target: []
  monetary_estimate_excluded_costs: []
  estimated_account_risk_amount: null
  estimated_account_risk_fraction: null
  confirmed_equity_used: null
  planned_equity_not_used_for_sizing: null
  remaining_daily_loss_budget: null
  remaining_portfolio_heat_budget: null
  remaining_correlated_heat_budget: null
  time_stop_at_vn: null
  event_cutoff_at_vn: null
  sizing_formula: null
  missing_sizing_inputs: []
  user_must_verify: []
  agent_may_submit_orders: false
  journal_reference: null
```

## Optional Quantity Formula

```text
total_risk_per_unit =
  abs(entry - stop) * value_per_price_unit
  + round_trip_fee_per_unit
  + slippage_per_unit
  + financing_and_borrow_buffer_per_unit

risk_budget =
  min(
    explicit_risk_amount or equity * risk_fraction,
    remaining_daily_loss_budget,
    remaining_portfolio_heat_budget,
    remaining_correlated_heat_budget
  )

quantity = floor_to_step(risk_budget / total_risk_per_unit)
```

Use the formula only when all terms are known. Never infer missing account or instrument fields from an unrelated public reference.

For `HYBRID_M5`, every cost term is required and must be explicitly supplied,
including zero when a real cost is truly absent. Require current platform
spread and declare whether bid/ask entry/exit geometry already includes it so
spread is neither omitted nor double-counted. Reject
`spread / abs(entry - stop) > 0.20` or
`total_execution_cost / gross_price_risk > 0.25`.

Until `strategy_validation_status: ADVISORY_VALIDATED`, add
`equity * 0.0025` to the risk-budget minimum and reject any larger requested
risk fraction for `HYBRID_M5`. Confirmed equity is required; an explicit
currency budget alone cannot prove compliance with a percentage cap.

Never use the formula for a cryptoasset or an instrument whose primary
underlying/reference is a cryptoasset. Return `NO_TRADE`,
`rejection_reason: UNSUPPORTED_ASSET_CLASS_CRYPTO`, and null quantity.

Never use the account-sizing formula while a matching scoped
`basis_incident_lock: ACTIVE`. Public-reference risk geometry remains allowed;
return `PLAN_PARTIAL`, `execution_state: NEEDS_USER_REALTIME`, and
leave platform prices, quantity, and monetary account risk null. A basis lock
for another symbol, contract, or account does not block this plan.

Apply the loss ladder only to losses carrying the same `session_id`. After one
reported stop in that session, limit the next eligible risk fraction to
`0.5%`; after two consecutive losses, return `NO_TRADE` for the remainder of
that session.

For a platform-displayed quantity with a matching pip/point value:

```text
displayed_quantity_loss_to_stop =
  abs(entry - stop) * platform_value_per_price_unit
  + known_cost_buffers

displayed_quantity_reward_to_target =
  abs(target - entry) * platform_value_per_price_unit
  - known_cost_buffers
```

Use the platform's stated value convention exactly. Do not multiply by quantity again when the platform already states the value for the selected quantity. Displayed margin is collateral, not stop-defined loss.

For `user-cfd-usd-2000-v1`, load
[account-risk-profile.md](account-risk-profile.md). Keep the profile
`PLANNED_PENDING_BROKER_CONFIRMATION` until a fresh account snapshot confirms
the deposit. When active, require the target, stop, selected quantity, and
platform value-per-point to produce both a monetary loss and monetary net
profit before the ticket is labelled ready.

A valid full broker snapshot may be reused for the named session until its
expiry or an invalidation event. A fill, exit, working-order change, material
P&L/margin change, or explicit account-state update requires a delta refresh
before account sizing; it does not erase public-reference geometry.

Every broker snapshot and real-time ticket field must be
`USER_PROVIDED_REALTIME`. Never connect to XTB, call an API/connector, or
retrieve these values independently; request them from the user.
