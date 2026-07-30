# Planned USD 2,000 CFD Risk Profile

Use this profile for the user's manual CFD tickets.

## Eligible Instrument Scope

- Allow liquid FX, equity-index, rates/sovereign-bond, volatility,
  precious-metal, industrial/base-metal, energy, agriculture/soft-commodity,
  livestock, emissions, fertilizer/chemical, and liquid-stock instruments
  that pass the normal decision and risk gates.
- For XTB, restrict new-entry candidates to symbols verified in the current
  public specification or confirmed by the user as visible and openable in
  their platform. The skills never inspect XTB. Reject instruments the user
  reports as `CLOSE ONLY`.
- Require an identifiable platform-listed instrument, contract/reference
  basis, quantity step, and value per price unit before sizing. A physical
  commodity assessment or a related producer stock is contextual evidence,
  not a substitute for the traded instrument's price.
- Prohibit crypto spot, perpetuals, futures, options, CFDs, and
  crypto-tracking ETPs/ETFs.
- For prohibited crypto, return `NO_TRADE`,
  `UNSUPPORTED_ASSET_CLASS_CRYPTO`, and `DO_NOT_CLICK` before calculating
  quantity, leverage, loss, or profit.

```yaml
account_risk_profile:
  profile_id: user-cfd-usd-2000-v1
  status: PLANNED_PENDING_BROKER_CONFIRMATION
  base_currency: USD
  planned_equity: 2000
  activation_rule: current_user_supplied_xtb_text_screenshot_or_export_confirms_equity_at_or_above_2000
  snapshot_reuse:
    scope: NAMED_SESSION
    full_snapshot_required_at_session_bootstrap: true
    delta_refresh_after_account_state_change: true
  risk_per_trade:
    base_fraction: 0.0075
    base_amount_at_planned_equity: 15
    hard_maximum_fraction: 0.01
    hard_maximum_amount_at_planned_equity: 20
    hybrid_m5_research_fraction: 0.0025
    hybrid_m5_research_amount_at_planned_equity: 5
  reward:
    reject_below_estimated_net_reward_risk: 1.5
    reduced_risk_below_estimated_net_reward_risk: 1.8
    preferred_estimated_net_reward_risk: 2.0
    normal_net_profit_target_at_base_risk: 30
    normal_net_profit_target_range: [27, 40]
  execution_cost_gates:
    maximum_spread_to_stop_fraction: 0.20
    maximum_total_cost_r: 0.25
  aggregate_limits:
    maximum_open_risk_fraction: 0.02
    maximum_open_risk_at_planned_equity: 40
    maximum_correlated_open_risk_fraction: 0.015
    maximum_correlated_open_risk_at_planned_equity: 30
    maximum_daily_loss_fraction: 0.02
    maximum_daily_loss_at_planned_equity: 40
    maximum_weekly_loss_fraction: 0.05
    maximum_weekly_loss_at_planned_equity: 100
    stop_after_consecutive_losses: 2
```

## Activation and Freshness

- Treat USD 2,000 as planned equity, not current equity, until a fresh broker
  screenshot, text value, or export supplied by the user confirms it.
- Never access XTB, a broker API, connector, authenticated browser, or desktop
  app. Ask the user for any real-time/account value required for sizing.
- Before activation, size from the latest confirmed equity. Never size from the
  planned deposit, available margin, contract value, or buying power.
- Capture one full account snapshot at session bootstrap, then reuse it until
  expiry or an invalidation event. A fill, exit, working-order change, material
  P&L/margin move, or explicit account-state update requires a compact delta
  refresh before the next account-sized ticket.
- If no account state changed, accept a compact no-change confirmation; do not
  require another full screenshot for every candidate.
- Include every open and pending order in portfolio heat. Deduct its
  stop-defined remaining risk before sizing a new order.
- Treat Tesla and U.S. equity-index CFDs as correlated exposure for the gross
  correlated-risk cap. Do not assume opposite directions form a reliable hedge.
- Treat a commodity and its producer equities, close substitutes within one
  commodity complex, and fertilizer producers sharing feedstock or crop-demand
  drivers as potentially correlated until evidence supports a lower estimate.

## Target and Quantity Rules

- Use USD 15 as the normal risk budget after activation. Use less when the
  remaining daily, portfolio, or correlated-risk budget is smaller.
- Use at most USD 5 (`0.25%`) for `HYBRID_M5` while its strategy status is
  `RESEARCH_ONLY` or `FORWARD_OBSERVATION`. `REJECTED` and `SUSPENDED` permit
  no ticket. The normal USD 15 budget becomes eligible only after
  `ADVISORY_VALIDATED`.
- Never exceed USD 20 on one trade.
- Require estimated net reward-to-risk of at least 1.8 for normal size and aim
  for 2.0. A setup from 1.5 through 1.79 may use at most 0.5% equity risk only
  when the evidence and event calendar remain acceptable.
- Reject a setup below 1.5 estimated net reward-to-risk.
- Calculate quantity from the stop and the platform's value-per-point display,
  then round down to the broker quantity step.
- Do not widen a technically valid stop to consume the full money budget.
- Always show estimated loss at stop, estimated net profit at target, risk as a
  percentage of confirmed equity, net reward-to-risk, and the quantity step.
- For `HYBRID_M5`, also show spread-to-stop, total-cost-R, and break-even win
  rate; reject spread-to-stop above `0.20` or total-cost-R above `0.25`.

## Session Stops

- Count stops by exact `session_id`. After the first reported stop in that
  session, require a fresh core-universe scan and one completed trigger bar;
  cap the next eligible trade at `0.5%` confirmed-equity risk.
- Do not open another trade after two consecutive losses in the same session.
  Reset this ladder when the next named session begins.
- If broker execution cannot be reconciled with the public-reference path,
  activate `BASIS_INCIDENT_LOCK_ACTIVE` for that account, symbol, and contract.
  Continue non-executable public-reference plans, but issue no new quantity or
  numeric platform ticket for the affected contract until a current platform
  quote reconciles symbol, bid/ask, spread, quote time, and contract basis.
- Stop for the day when realized plus worst-case open loss reaches USD 40.
- Stop for the week when realized loss reaches USD 100.
- Every intraday ticket must include a time stop and a scheduled-event cutoff.
