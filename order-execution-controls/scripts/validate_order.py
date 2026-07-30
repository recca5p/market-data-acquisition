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
        if entry is not None and stop is not None and entry > 0 and stop > 0:
            price_risk = abs(entry - stop)
            if price_risk == 0:
                errors.append("entry and stop cannot be equal")
            elif side == "LONG" and stop >= entry:
                errors.append("LONG stop must be below entry")
            elif side == "SHORT" and stop <= entry:
                errors.append("SHORT stop must be above entry")

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
        cost = decimal_value(
            payload, "estimated_cost_per_unit", errors, required=False
        )
        if cost is None:
            warnings.append("costs are unknown; net reward-to-risk is unavailable")
        elif cost < 0:
            errors.append("estimated_cost_per_unit cannot be negative")

        minimum_ratio = decimal_value(
            payload, "minimum_reward_risk", errors, required=False
        )
        if minimum_ratio is not None and minimum_ratio <= 0:
            errors.append("minimum_reward_risk must be positive")

        if entry is not None and price_risk is not None and price_risk > 0:
            for target in targets:
                reward = abs(target - entry)
                gross = reward / price_risk
                gross_ratios.append(as_text(gross))
                if cost is not None:
                    net_risk = price_risk + cost
                    net_reward = reward - cost
                    net = net_reward / net_risk if net_risk > 0 else Decimal("-1")
                    net_ratios.append(as_text(net))
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
        ):
            if value is not None and (value <= 0 or value > 1):
                errors.append(f"{label} must be greater than 0 and at most 1")

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
        result = {
            "status": status,
            "gross_reward_risk_by_target": gross_ratios,
            "estimated_net_reward_risk_by_target": net_ratios,
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
                "tab": ticket_tab,
                "type": display_type,
                "button": button,
                "quantity": (
                    as_text(quantity) if quantity is not None else None
                ),
                "quantity_source": quantity_source,
                "price": as_text(entry) if entry is not None else None,
                "stop_loss_enabled": stop is not None,
                "stop_loss": as_text(stop) if stop is not None else None,
                "take_profit_enabled": bool(targets),
                "take_profit": as_text(targets[0]) if targets else None,
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
