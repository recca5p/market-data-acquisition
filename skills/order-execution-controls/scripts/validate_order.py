#!/usr/bin/env python3
"""Validate a manual trade card from JSON without contacting a broker."""

from __future__ import annotations

import json
import sys
from decimal import Decimal, InvalidOperation


def decimal_value(
    payload: dict,
    key: str,
    errors: list[str],
    *,
    required: bool = True,
) -> Decimal | None:
    value = payload.get(key)
    if value is None:
        if required:
            errors.append(f"missing required field: {key}")
        return None
    try:
        result = Decimal(str(value))
        if not result.is_finite():
            raise InvalidOperation
        return result
    except (InvalidOperation, ValueError):
        errors.append(f"invalid decimal field: {key}")
        return None


def aligned(value: Decimal, step: Decimal) -> bool:
    return step > 0 and value % step == 0


def as_text(value: Decimal) -> str:
    return format(value.normalize(), "f")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("payload must be a JSON object")

        errors: list[str] = []
        warnings: list[str] = []

        if payload.get("execution_state") != "PLATFORM_TICKET_READY":
            errors.append("execution_state must be PLATFORM_TICKET_READY")
        if (
            payload.get("realtime_execution_data_source")
            != "USER_PROVIDED_REALTIME"
        ):
            errors.append(
                "realtime_execution_data_source must be "
                "USER_PROVIDED_REALTIME"
            )
        if payload.get("xtb_interaction_allowed") is not False:
            errors.append("xtb_interaction_allowed must be false")

        for key in (
            "decision_id",
            "risk_plan_id",
            "instrument",
            "public_reference_basis",
        ):
            if not payload.get(key):
                errors.append(f"missing required field: {key}")

        side = str(payload.get("side", "")).upper()
        if side not in {"LONG", "SHORT"}:
            errors.append("side must be LONG or SHORT")
        entry_timing_mode = str(
            payload.get("entry_timing_mode", "M15")
        ).upper()
        if entry_timing_mode not in {"M15", "HYBRID_M5"}:
            errors.append("entry_timing_mode must be M15 or HYBRID_M5")
        strategy_validation_status = str(
            payload.get("strategy_validation_status", "RESEARCH_ONLY")
        ).upper()
        if strategy_validation_status not in {
            "REJECTED",
            "RESEARCH_ONLY",
            "FORWARD_OBSERVATION",
            "SUSPENDED",
            "ADVISORY_VALIDATED",
        }:
            errors.append("invalid strategy_validation_status")
        elif strategy_validation_status in {"REJECTED", "SUSPENDED"}:
            errors.append(
                "strategy_validation_status does not permit a ticket"
            )

        raw_order_mode = payload.get("order_mode")
        raw_order_type = payload.get("order_type")
        order_mode = (
            str(raw_order_mode).upper() if raw_order_mode is not None else None
        )
        order_type = (
            str(raw_order_type).upper() if raw_order_type is not None else None
        )
        if order_mode is not None and order_mode not in {"MARKET", "STOP_LIMIT"}:
            errors.append("order_mode must be MARKET or STOP_LIMIT")
        if order_type is not None and order_type not in {
            "MARKET",
            "BUY_STOP",
            "SELL_STOP",
            "BUY_LIMIT",
            "SELL_LIMIT",
        }:
            errors.append(
                "order_type must be MARKET, BUY_STOP, SELL_STOP, "
                "BUY_LIMIT, or SELL_LIMIT"
            )
        if (order_mode is None) != (order_type is None):
            errors.append("order_mode and order_type must be supplied together")
        if order_mode == "MARKET" and order_type != "MARKET":
            errors.append("MARKET order_mode requires MARKET order_type")
        if order_mode == "STOP_LIMIT" and order_type == "MARKET":
            errors.append("STOP_LIMIT order_mode requires a pending order_type")
        if order_type in {"BUY_STOP", "BUY_LIMIT"} and side != "LONG":
            errors.append(f"{order_type} requires LONG side")
        if order_type in {"SELL_STOP", "SELL_LIMIT"} and side != "SHORT":
            errors.append(f"{order_type} requires SHORT side")

        now_ms = decimal_value(payload, "checked_at_epoch_ms", errors)
        expiry_ms = decimal_value(payload, "signal_expires_at_epoch_ms", errors)
        quote_time_ms = decimal_value(
            payload,
            "platform_quote_observed_at_epoch_ms",
            errors,
            required=entry_timing_mode == "HYBRID_M5",
        )
        maximum_quote_age_seconds = decimal_value(
            payload,
            "maximum_quote_age_seconds",
            errors,
            required=entry_timing_mode == "HYBRID_M5",
        )
        trigger_bar_time_ms = decimal_value(
            payload,
            "trigger_bar_completed_at_epoch_ms",
            errors,
            required=entry_timing_mode == "HYBRID_M5",
        )
        maximum_trigger_bar_age_seconds = decimal_value(
            payload,
            "maximum_trigger_bar_age_seconds",
            errors,
            required=entry_timing_mode == "HYBRID_M5",
        )
        trigger_timeframe = str(
            payload.get("trigger_timeframe", "")
        ).upper()
        trigger_bar_completed = payload.get("trigger_bar_completed")
        higher_timeframe_alignment_confirmed = payload.get(
            "higher_timeframe_alignment_confirmed"
        )
        if entry_timing_mode == "HYBRID_M5":
            if trigger_timeframe != "M5":
                errors.append("HYBRID_M5 requires trigger_timeframe M5")
            if trigger_bar_completed is not True:
                errors.append("HYBRID_M5 requires a completed M5 trigger bar")
            if higher_timeframe_alignment_confirmed is not True:
                errors.append(
                    "HYBRID_M5 requires confirmed H1/M15 directional alignment"
                )
            for label, value in (
                ("maximum_quote_age_seconds", maximum_quote_age_seconds),
                (
                    "maximum_trigger_bar_age_seconds",
                    maximum_trigger_bar_age_seconds,
                ),
            ):
                if value is not None and value <= 0:
                    errors.append(f"{label} must be positive")
            if now_ms is not None and quote_time_ms is not None:
                if quote_time_ms > now_ms:
                    errors.append(
                        "platform_quote_observed_at_epoch_ms cannot be in the future"
                    )
                elif (
                    maximum_quote_age_seconds is not None
                    and now_ms - quote_time_ms
                    > maximum_quote_age_seconds * Decimal("1000")
                ):
                    errors.append("platform quote is stale for HYBRID_M5")
            if now_ms is not None and trigger_bar_time_ms is not None:
                if trigger_bar_time_ms > now_ms:
                    errors.append(
                        "trigger_bar_completed_at_epoch_ms cannot be in the future"
                    )
                elif (
                    maximum_trigger_bar_age_seconds is not None
                    and now_ms - trigger_bar_time_ms
                    > maximum_trigger_bar_age_seconds * Decimal("1000")
                ):
                    errors.append("completed M5 trigger bar is stale")
        entry = decimal_value(payload, "entry_price_for_calculation", errors)
        stop = decimal_value(payload, "stop_loss", errors)
        platform_bid = decimal_value(
            payload, "platform_bid", errors, required=False
        )
        platform_ask = decimal_value(
            payload, "platform_ask", errors, required=False
        )
        for label, value in (
            ("platform_bid", platform_bid),
            ("platform_ask", platform_ask),
        ):
            if value is not None and value <= 0:
                errors.append(f"{label} must be positive")
        if (
            platform_bid is not None
            and platform_ask is not None
            and platform_bid > platform_ask
        ):
            errors.append("platform_bid cannot exceed platform_ask")
        platform_spread = decimal_value(
            payload,
            "platform_spread",
            errors,
            required=entry_timing_mode == "HYBRID_M5",
        )
        maximum_spread_to_stop_fraction = decimal_value(
            payload,
            "maximum_spread_to_stop_fraction",
            errors,
            required=entry_timing_mode == "HYBRID_M5",
        )
        if platform_spread is not None and platform_spread < 0:
            errors.append("platform_spread cannot be negative")
        if (
            maximum_spread_to_stop_fraction is not None
            and (
                maximum_spread_to_stop_fraction <= 0
                or maximum_spread_to_stop_fraction > 1
            )
        ):
            errors.append(
                "maximum_spread_to_stop_fraction must be greater than 0 "
                "and at most 1"
            )

        valid_entry_low = decimal_value(
            payload, "valid_market_entry_low", errors, required=False
        )
        valid_entry_high = decimal_value(
            payload, "valid_market_entry_high", errors, required=False
        )
        if (valid_entry_low is None) != (valid_entry_high is None):
            errors.append(
                "valid_market_entry_low and valid_market_entry_high "
                "must be supplied together"
            )
        elif (
            valid_entry_low is not None
            and valid_entry_high is not None
            and (
                valid_entry_low <= 0
                or valid_entry_high <= 0
                or valid_entry_low > valid_entry_high
            )
        ):
            errors.append("valid Market-entry zone is invalid")
        elif (
            order_mode == "MARKET"
            and valid_entry_low is not None
            and valid_entry_high is not None
        ):
            executable_price = platform_ask if side == "LONG" else platform_bid
            if executable_price is None:
                warnings.append(
                    "platform executable price is missing; Market-entry "
                    "zone must be reconfirmed manually"
                )
            elif not valid_entry_low <= executable_price <= valid_entry_high:
                errors.append(
                    "platform executable price is outside the valid "
                    "Market-entry zone"
                )

        if order_mode == "STOP_LIMIT":
            if platform_bid is None or platform_ask is None:
                warnings.append(
                    "platform bid/ask is incomplete; pending trigger side "
                    "must be reconfirmed manually"
                )
            elif entry is not None:
                if order_type == "BUY_STOP" and entry <= platform_ask:
                    errors.append("BUY_STOP trigger must be above platform_ask")
                elif order_type == "SELL_STOP" and entry >= platform_bid:
                    errors.append("SELL_STOP trigger must be below platform_bid")
                elif order_type == "BUY_LIMIT" and entry >= platform_ask:
                    errors.append("BUY_LIMIT trigger must be below platform_ask")
                elif order_type == "SELL_LIMIT" and entry <= platform_bid:
                    errors.append("SELL_LIMIT trigger must be above platform_bid")

        raw_targets = payload.get("targets")
        targets: list[Decimal] = []
        if not isinstance(raw_targets, list) or not raw_targets:
            errors.append("targets must be a non-empty list")
        else:
            for index, raw_target in enumerate(raw_targets):
                try:
                    target = Decimal(str(raw_target))
                    if not target.is_finite():
                        raise InvalidOperation
                    targets.append(target)
                except (InvalidOperation, ValueError):
                    errors.append(f"invalid target at index {index}")

        if now_ms is not None and expiry_ms is not None and now_ms >= expiry_ms:
            errors.append("signal has expired")

        positive_values = {
            "entry_price_for_calculation": entry,
            "stop_loss": stop,
        }
        for name, value in positive_values.items():
            if value is not None and value <= 0:
                errors.append(f"{name} must be positive")
        for index, target in enumerate(targets):
            if target <= 0:
                errors.append(f"target at index {index} must be positive")

        price_risk: Decimal | None = None
        spread_to_stop_fraction: Decimal | None = None
        if entry is not None and stop is not None and entry > 0 and stop > 0:
            price_risk = abs(entry - stop)
            if price_risk == 0:
                errors.append("entry and stop cannot be equal")
            elif side == "LONG" and stop >= entry:
                errors.append("LONG stop must be below entry")
            elif side == "SHORT" and stop <= entry:
                errors.append("SHORT stop must be above entry")
            elif platform_spread is not None:
                spread_to_stop_fraction = platform_spread / price_risk
                if (
                    maximum_spread_to_stop_fraction is not None
                    and spread_to_stop_fraction
                    > maximum_spread_to_stop_fraction
                ):
                    errors.append(
                        "platform spread exceeds "
                        "maximum_spread_to_stop_fraction"
                    )

        for index, target in enumerate(targets):
            if entry is None:
                break
            if side == "LONG" and target <= entry:
                errors.append(f"LONG target at index {index} must be above entry")
            if side == "SHORT" and target >= entry:
                errors.append(f"SHORT target at index {index} must be below entry")

        tick_size = decimal_value(
            payload, "optional_tick_size", errors, required=False
        )
        if tick_size is None:
            warnings.append("tick size is unknown; verify price increments manually")
        elif tick_size <= 0:
            errors.append("optional_tick_size must be positive")
        else:
            for label, value in (
                ("entry", entry),
                ("stop", stop),
                *[(f"target[{index}]", target) for index, target in enumerate(targets)],
            ):
                if value is not None and not aligned(value, tick_size):
                    errors.append(f"{label} is not aligned to tick size")

        quantity = decimal_value(
            payload, "optional_quantity", errors, required=False
        )
        raw_quantity_source = payload.get("quantity_source")
        quantity_source = (
            str(raw_quantity_source).upper()
            if raw_quantity_source is not None
            else None
        )
        if quantity_source is not None and quantity_source not in {
            "RISK_CALCULATED",
            "USER_SELECTED_NOT_APPROVED",
            "NOT_CALCULATED",
        }:
            errors.append(
                "quantity_source must be RISK_CALCULATED, "
                "USER_SELECTED_NOT_APPROVED, or NOT_CALCULATED"
            )
        account_profile_id = payload.get("account_profile_id")
        account_profile_status = str(
            payload.get("account_profile_status", "NOT_USED")
        ).upper()
        if account_profile_status not in {
            "PLANNED_PENDING_BROKER_CONFIRMATION",
            "ACTIVE_CONFIRMED",
            "NOT_USED",
        }:
            errors.append("invalid account_profile_status")
        if (
            quantity_source == "RISK_CALCULATED"
            and account_profile_id
            and account_profile_status != "ACTIVE_CONFIRMED"
        ):
            errors.append(
                "risk-calculated quantity cannot use an unconfirmed "
                "planned-equity profile"
            )
        quantity_step = decimal_value(
            payload, "optional_quantity_step", errors, required=False
        )
        if quantity is None:
            warnings.append("quantity is not calculated")
        elif quantity <= 0:
            errors.append("optional_quantity must be positive")
        elif quantity_step is None:
            warnings.append("quantity step is unknown; verify quantity manually")
        elif quantity_step <= 0 or not aligned(quantity, quantity_step):
            errors.append("quantity is not aligned to quantity step")

        gross_ratios: list[str] = []
        net_ratios: list[str] = []
        break_even_win_rates: list[str] = []
        total_cost_r: Decimal | None = None
        cost = decimal_value(
            payload, "estimated_cost_per_unit", errors, required=False
        )
        if cost is None:
            if entry_timing_mode == "HYBRID_M5":
                errors.append(
                    "HYBRID_M5 requires estimated_cost_per_unit"
                )
            else:
                warnings.append(
                    "costs are unknown; net reward-to-risk is unavailable"
                )
        elif cost < 0:
            errors.append("estimated_cost_per_unit cannot be negative")
        maximum_total_cost_r = decimal_value(
            payload,
            "maximum_total_cost_r",
            errors,
            required=entry_timing_mode == "HYBRID_M5",
        )
        if maximum_total_cost_r is not None and maximum_total_cost_r <= 0:
            errors.append("maximum_total_cost_r must be positive")

        minimum_ratio = decimal_value(
            payload, "minimum_reward_risk", errors, required=False
        )
        if minimum_ratio is not None and minimum_ratio <= 0:
            errors.append("minimum_reward_risk must be positive")

        if entry is not None and price_risk is not None and price_risk > 0:
            if cost is not None:
                total_cost_r = cost / price_risk
                if (
                    maximum_total_cost_r is not None
                    and total_cost_r > maximum_total_cost_r
                ):
                    errors.append(
                        "total execution cost exceeds maximum_total_cost_r"
                    )
            for target in targets:
                reward = abs(target - entry)
                gross = reward / price_risk
                gross_ratios.append(as_text(gross))
                if cost is not None:
                    net_risk = price_risk + cost
                    net_reward = reward - cost
                    net = net_reward / net_risk if net_risk > 0 else Decimal("-1")
                    net_ratios.append(as_text(net))
                    if net_reward > 0:
                        break_even_win_rates.append(
                            as_text(net_risk / (net_risk + net_reward))
                        )
                    if minimum_ratio is not None and net < minimum_ratio:
                        errors.append(
                            f"net reward-to-risk {as_text(net)} is below "
                            f"minimum {as_text(minimum_ratio)}"
                        )

        account_equity = decimal_value(
            payload, "confirmed_account_equity", errors, required=False
        )
        estimated_loss = decimal_value(
            payload, "estimated_loss_at_stop", errors, required=False
        )
        estimated_net_profit = decimal_value(
            payload, "estimated_net_profit_at_target", errors, required=False
        )
        existing_open_risk = decimal_value(
            payload, "existing_open_risk_amount", errors, required=False
        )
        maximum_trade_risk_fraction = decimal_value(
            payload, "maximum_trade_risk_fraction", errors, required=False
        )
        research_risk_cap_fraction = decimal_value(
            payload,
            "research_risk_cap_fraction",
            errors,
            required=False,
        )
        maximum_portfolio_heat_fraction = decimal_value(
            payload,
            "maximum_portfolio_heat_fraction",
            errors,
            required=False,
        )
        for label, value in (
            ("confirmed_account_equity", account_equity),
            ("estimated_loss_at_stop", estimated_loss),
            ("estimated_net_profit_at_target", estimated_net_profit),
        ):
            if value is not None and value <= 0:
                errors.append(f"{label} must be positive")
        if existing_open_risk is not None and existing_open_risk < 0:
            errors.append("existing_open_risk_amount cannot be negative")
        for label, value in (
            ("maximum_trade_risk_fraction", maximum_trade_risk_fraction),
            (
                "maximum_portfolio_heat_fraction",
                maximum_portfolio_heat_fraction,
            ),
            ("research_risk_cap_fraction", research_risk_cap_fraction),
        ):
            if value is not None and (value <= 0 or value > 1):
                errors.append(f"{label} must be greater than 0 and at most 1")
        if (
            entry_timing_mode == "HYBRID_M5"
            and strategy_validation_status != "ADVISORY_VALIDATED"
        ):
            if research_risk_cap_fraction is None:
                errors.append(
                    "HYBRID_M5 research ticket requires "
                    "research_risk_cap_fraction"
                )
            elif research_risk_cap_fraction > Decimal("0.0025"):
                errors.append(
                    "HYBRID_M5 research_risk_cap_fraction cannot exceed 0.0025"
                )
            if account_equity is None or estimated_loss is None:
                errors.append(
                    "HYBRID_M5 research ticket requires confirmed equity "
                    "and estimated loss"
                )
            if maximum_trade_risk_fraction is None:
                errors.append(
                    "HYBRID_M5 research ticket requires "
                    "maximum_trade_risk_fraction"
                )
            if (
                maximum_trade_risk_fraction is not None
                and research_risk_cap_fraction is not None
                and maximum_trade_risk_fraction
                > research_risk_cap_fraction
            ):
                errors.append(
                    "maximum_trade_risk_fraction exceeds the HYBRID_M5 "
                    "research cap"
                )

        trade_risk_fraction: Decimal | None = None
        resulting_heat_fraction: Decimal | None = None
        monetary_reward_risk: Decimal | None = None
        if account_equity is not None and estimated_loss is not None:
            trade_risk_fraction = estimated_loss / account_equity
            if (
                maximum_trade_risk_fraction is not None
                and trade_risk_fraction > maximum_trade_risk_fraction
            ):
                errors.append("estimated loss exceeds the single-trade risk cap")
            if existing_open_risk is not None:
                resulting_heat_fraction = (
                    existing_open_risk + estimated_loss
                ) / account_equity
                if (
                    maximum_portfolio_heat_fraction is not None
                    and resulting_heat_fraction
                    > maximum_portfolio_heat_fraction
                ):
                    errors.append(
                        "existing plus proposed risk exceeds the "
                        "portfolio-heat cap"
                    )
        if estimated_loss is not None and estimated_net_profit is not None:
            monetary_reward_risk = estimated_net_profit / estimated_loss
            if (
                minimum_ratio is not None
                and monetary_reward_risk < minimum_ratio
            ):
                errors.append(
                    "monetary net reward-to-risk is below the supplied minimum"
                )

        observed_price = decimal_value(
            payload, "observed_public_price", errors, required=False
        )
        max_deviation = decimal_value(
            payload,
            "maximum_reference_deviation_fraction",
            errors,
            required=False,
        )
        if observed_price is not None and entry is not None:
            if observed_price <= 0:
                errors.append("observed_public_price must be positive")
            elif max_deviation is None:
                warnings.append(
                    "no maximum reference deviation supplied; reconfirm entry manually"
                )
            elif max_deviation < 0:
                errors.append("maximum_reference_deviation_fraction cannot be negative")
            elif abs(observed_price - entry) / entry > max_deviation:
                warnings.append(
                    "public reference price moved beyond the supplied deviation"
                )

        stated_delay = decimal_value(
            payload, "stated_delay_seconds", errors, required=False
        )
        if stated_delay is None:
            warnings.append("source delay is unknown")
        elif stated_delay < 0:
            errors.append("stated_delay_seconds cannot be negative")
        elif stated_delay > 0:
            warnings.append(
                f"public source is delayed by {as_text(stated_delay)} seconds"
            )

        status = (
            "MANUAL_TICKET_INVALID"
            if errors
            else "MANUAL_TICKET_WARNING"
            if warnings
            else "MANUAL_TICKET_VALID"
        )
        button = (
            "BUY"
            if side == "LONG"
            else "SELL"
            if side == "SHORT"
            else None
        )
        ticket_tab = (
            "Lệnh theo giá thị trường"
            if order_mode == "MARKET"
            else "Lệnh Stop / Limit"
            if order_mode == "STOP_LIMIT"
            else None
        )
        display_type = (
            order_type.replace("_", " ").title()
            if order_type is not None
            else None
        )
        ticket_valid = not errors
        result = {
            "status": status,
            "gross_reward_risk_by_target": gross_ratios,
            "estimated_net_reward_risk_by_target": net_ratios,
            "break_even_win_rate_by_target": break_even_win_rates,
            "total_cost_r": (
                as_text(total_cost_r)
                if total_cost_r is not None
                else None
            ),
            "entry_timing_mode": entry_timing_mode,
            "strategy_validation_status": strategy_validation_status,
            "hybrid_checks": {
                "higher_timeframe_alignment_confirmed": (
                    higher_timeframe_alignment_confirmed
                ),
                "trigger_timeframe": trigger_timeframe or None,
                "trigger_bar_completed": trigger_bar_completed,
                "spread_to_stop_fraction": (
                    as_text(spread_to_stop_fraction)
                    if spread_to_stop_fraction is not None
                    else None
                ),
            },
            "errors": errors,
            "warnings": warnings,
            "account_risk": {
                "profile_id": account_profile_id,
                "profile_status": account_profile_status,
                "confirmed_equity": (
                    as_text(account_equity)
                    if account_equity is not None
                    else None
                ),
                "estimated_loss_at_stop": (
                    as_text(estimated_loss)
                    if estimated_loss is not None
                    else None
                ),
                "estimated_net_profit_at_target": (
                    as_text(estimated_net_profit)
                    if estimated_net_profit is not None
                    else None
                ),
                "estimated_trade_risk_fraction": (
                    as_text(trade_risk_fraction)
                    if trade_risk_fraction is not None
                    else None
                ),
                "resulting_portfolio_heat_fraction": (
                    as_text(resulting_heat_fraction)
                    if resulting_heat_fraction is not None
                    else None
                ),
                "monetary_net_reward_risk": (
                    as_text(monetary_reward_risk)
                    if monetary_reward_risk is not None
                    else None
                ),
            },
            "platform_ticket": {
                "tab": ticket_tab if ticket_valid else None,
                "type": display_type if ticket_valid else None,
                "button": button if ticket_valid else None,
                "quantity": (
                    as_text(quantity)
                    if ticket_valid and quantity is not None
                    else None
                ),
                "quantity_source": quantity_source if ticket_valid else None,
                "price": (
                    as_text(entry)
                    if ticket_valid and entry is not None
                    else None
                ),
                "stop_loss_enabled": ticket_valid and stop is not None,
                "stop_loss": (
                    as_text(stop)
                    if ticket_valid and stop is not None
                    else None
                ),
                "take_profit_enabled": ticket_valid and bool(targets),
                "take_profit": (
                    as_text(targets[0])
                    if ticket_valid and targets
                    else None
                ),
            },
            "agent_may_submit_orders": False,
            "broker_connection_required": False,
            "xtb_interaction_allowed": False,
            "user_platform_verification_required": True,
        }
        print(json.dumps(result, indent=2))
        return 2 if errors else 0
    except (json.JSONDecodeError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "MANUAL_TICKET_INVALID",
                    "errors": [str(exc)],
                    "warnings": [],
                    "agent_may_submit_orders": False,
                    "broker_connection_required": False,
                    "xtb_interaction_allowed": False,
                    "user_platform_verification_required": True,
                },
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
