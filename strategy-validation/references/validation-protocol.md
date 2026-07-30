# Strategy Validation Protocol

## Required Strategy Specification

```yaml
strategy_spec:
  strategy_id: null
  version: null
  code_or_config_hash: null
  universe: []
  instrument_basis: []
  sessions: []
  decision_horizon: null
  required_timeframes: []
  required_data_fields: []
  freshness_policy: {}
  feature_rules: []
  regime_rules: []
  setup_rules: []
  entry_rules: []
  stop_and_invalidation_rules: []
  exit_rules: []
  no_trade_rules: []
  sizing_interface: {}
  cost_model: {}
  parameters: {}
  predeclared_gates: {}
```

## Integrity Checklist

- Use point-in-time data available at each simulated decision.
- Use only completed bars unless the strategy explicitly models in-progress bars.
- Align signals, order eligibility, and fills so the fill cannot occur before the signal exists.
- Adjust equities for splits/dividends consistently and include delisted securities where relevant.
- Declare futures contract selection, roll dates, price adjustment, and expiry exclusions.
- Preserve original and revised macro release values when event data is used.
- Model bid/ask, fees, slippage, borrow, funding, roll, and currency conversion.
- Separate development data from the untouched final test.

## Minimum Evaluation Artifact

```yaml
validation:
  validation_id: null
  strategy_id: null
  strategy_version: null
  status: REJECTED | RESEARCH_ONLY | FORWARD_OBSERVATION | SUSPENDED | ADVISORY_VALIDATED
  evaluated_at_vn: null
  expires_at_vn: null
  data_references: []
  periods:
    train: null
    validation: null
    test: null
    paper_forward: null
  simulation:
    fill_model: null
    cost_model: null
    latency_model: null
    liquidity_constraints: null
  integrity_results: []
  metrics:
    trades: null
    net_expectancy: null
    profit_factor: null
    max_drawdown: null
    tail_loss: null
    turnover: null
    time_under_water: null
    risk_adjusted_return: null
    qualified_opportunities_per_session: null
    qualified_opportunities_per_week: null
    ready_now_frequency: null
    candidate_to_ticket_conversion: null
    platform_translation_miss_rate: null
    no_trade_market_rule_fraction: null
    no_trade_data_or_workflow_blocker_fraction: null
  regime_results: []
  stress_results: []
  probability_calibration: null
  predeclared_gate_results: []
  limitations: []
  monitoring_thresholds: {}
  next_review_at_vn: null
```

## Promotion Rules

- Reject any strategy whose primary underlying/reference is a cryptoasset with
  `UNSUPPORTED_ASSET_CLASS_CRYPTO`; do not run historical or forward tests.
- Do not invent universal performance thresholds; require them to be predeclared for the strategy and use case.
- Do not promote based only on in-sample or optimized results.
- Require a forward paper observation period before `ADVISORY_VALIDATED`.
- Evaluate opportunity throughput and candidate-to-ticket conversion against
  predeclared gates. Do not improve these metrics by weakening setup quality,
  reward-to-risk, session-loss, or asset-class rules.
- Treat changes to logic, data, parameters, universe, instrument basis, costs, or execution as a new version.
- Suspend on drift, drawdown, data-quality, execution, or operational thresholds defined in the artifact.
- Validation outputs may define review thresholds, but must not create
  autonomous alerts, monitors, or pre-trigger pending orders.
