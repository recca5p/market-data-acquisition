# Manual Trade Card Contract

```yaml
manual_trade_card:
  schema_version: "2.2"
  decision_id: null
  risk_plan_id: null
  session_id: null
  execution_state: PLATFORM_TICKET_READY
  realtime_execution_data_source: USER_PROVIDED_REALTIME
  xtb_interaction_allowed: false
  instrument: null
  asset_class: null
  basis_incident_lock: CLEAR | ACTIVE
  basis_incident_scope:
    masked_account_alias: null
    broker_symbol: null
    contract_id: null
  public_reference_basis: null
  side: LONG | SHORT
  broker_symbol: null
  order_mode: MARKET | STOP_LIMIT
  order_type: MARKET | BUY_STOP | SELL_STOP | BUY_LIMIT | SELL_LIMIT
  platform_bid: null
  platform_ask: null
  platform_quote_observed_at_epoch_ms: null
  valid_market_entry_low: null
  valid_market_entry_high: null
  entry_price_for_calculation: null
  stop_loss: null
  targets: []
  signal_expires_at_epoch_ms: null
  observed_public_price: null
  public_price_observed_at_epoch_ms: null
  stated_delay_seconds: null
  optional_quantity: null
  quantity_source: RISK_CALCULATED | USER_SELECTED_NOT_APPROVED | NOT_CALCULATED
  optional_tick_size: null
  optional_quantity_step: null
  platform_pip_or_point_value: null
  platform_spread: null
  estimated_cost_per_unit: null
  minimum_reward_risk: null
  maximum_reference_deviation_fraction: null
  account_profile_id: null
  account_profile_status: PLANNED_PENDING_BROKER_CONFIRMATION | ACTIVE_CONFIRMED | NOT_USED
  confirmed_account_equity: null
  estimated_loss_at_stop: null
  estimated_net_profit_at_target: null
  existing_open_risk_amount: null
  maximum_trade_risk_fraction: null
  maximum_portfolio_heat_fraction: null
```

```yaml
manual_ticket_check:
  status: MANUAL_TICKET_VALID | MANUAL_TICKET_WARNING | MANUAL_TICKET_INVALID
  checked_at_epoch_ms: null
  gross_reward_risk_by_target: []
  estimated_net_reward_risk_by_target: []
  account_risk:
    confirmed_equity: null
    estimated_loss_at_stop: null
    estimated_net_profit_at_target: null
    estimated_trade_risk_fraction: null
    resulting_portfolio_heat_fraction: null
  errors: []
  warnings: []
  platform_ticket:
    tab: Lệnh theo giá thị trường | Lệnh Stop / Limit
    type: Market | Buy Stop | Sell Stop | Buy Limit | Sell Limit
    button: BUY | SELL
    quantity: null
    price: null
    stop_loss_enabled: true
    stop_loss: null
    take_profit_enabled: true
    take_profit: null
  agent_may_submit_orders: false
  broker_connection_required: false
  xtb_interaction_allowed: false
  user_platform_verification_required: true
```

Unknown tick, quantity step, costs, or account risk produces a warning, not an invented value.

A matching active basis incident lock for the same account alias, broker
symbol, and contract always produces `MANUAL_TICKET_INVALID` with
`PLATFORM_BASIS_RECONCILIATION_REQUIRED` and an empty platform ticket. An
unrelated scoped lock does not invalidate this ticket.

`REQUEST_USER_REALTIME` and `NEEDS_USER_REALTIME` are upstream states, not
manual tickets. Do not pass them through this validator or turn them into
`MANUAL_TICKET_INVALID`. Never access XTB to fill the missing fields.

A cryptoasset or instrument whose primary underlying/reference is a
cryptoasset always produces `MANUAL_TICKET_INVALID` with
`UNSUPPORTED_ASSET_CLASS_CRYPTO`. Do not populate a user-editable platform
ticket.

Reject a pending ticket whose trigger is on the wrong side of the supplied bid/ask. If platform bid/ask is absent, preserve the ticket as a warning and require the user to reconfirm it manually.

For `user-cfd-usd-2000-v1`, require `ACTIVE_CONFIRMED` before accepting a
risk-calculated quantity based on USD 2,000. Use `minimum_reward_risk: 1.8`,
`maximum_trade_risk_fraction: 0.01`, and
`maximum_portfolio_heat_fraction: 0.02` for normal tickets. A reduced-risk
exception from 1.5 through 1.79 must be explicitly labelled by the risk plan;
never accept less than 1.5.
