#!/usr/bin/env python3
"""Calculate an indicative manual-trade quantity from a JSON payload.

Read JSON from stdin and write JSON to stdout. This script performs arithmetic
only; it does not fetch account data or submit orders.
"""

from __future__ import annotations

import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_FLOOR


def decimal_value(
    payload: dict,
    key: str,
    *,
    required: bool = True,
    default: str | None = None,
) -> Decimal | None:
    value = payload.get(key)
    if value is None:
        if required:
            raise ValueError(f"missing required field: {key}")
        if default is None:
            return None
        value = default
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal field: {key}") from exc
    if not result.is_finite():
        raise ValueError(f"non-finite decimal field: {key}")
    return result


def floor_to_step(value: Decimal, step: Decimal) -> Decimal:
    return (value / step).to_integral_value(rounding=ROUND_FLOOR) * step


def text_number(value: Decimal) -> str:
    return format(value.normalize(), "f")


def reject(errors: list[str]) -> None:
    print(
        json.dumps(
            {
                "status": "NOT_CALCULATED",
                "quantity_label": "NOT_CALCULATED",
                "agent_may_submit_orders": False,
                "broker_connection_required": False,
                "xtb_interaction_allowed": False,
                "errors": errors,
            },
            indent=2,
        )
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("payload must be a JSON object")

        if (
            payload.get("realtime_execution_data_source")
            != "USER_PROVIDED_REALTIME"
        ):
            raise ValueError(
                "realtime_execution_data_source must be "
                "USER_PROVIDED_REALTIME"
            )
        if payload.get("xtb_interaction_allowed") is not False:
            raise ValueError("xtb_interaction_allowed must be false")

        side = str(payload.get("side", "")).upper()
        if side not in {"LONG", "SHORT"}:
            raise ValueError("side must be LONG or SHORT")

        entry = decimal_value(payload, "entry_price")
        stop = decimal_value(payload, "stop_price")
        target = decimal_value(payload, "target_price", required=False)
        value_per_price_unit = decimal_value(payload, "value_per_price_unit")
        quantity_step = decimal_value(payload, "quantity_step")
        minimum_quantity = decimal_value(payload, "minimum_quantity")
        equity = decimal_value(payload, "equity", required=False)
        risk_fraction = decimal_value(payload, "risk_fraction", required=False)
        explicit_budget = decimal_value(
            payload, "explicit_risk_amount", required=False
        )
        if explicit_budget is None:
            explicit_budget = decimal_value(
                payload, "explicit_max_risk_amount", required=False
            )
        daily_budget = decimal_value(
            payload, "remaining_daily_loss_budget", required=False
        )
        heat_budget = decimal_value(
            payload, "remaining_portfolio_heat_budget", required=False
        )
        correlated_budget = decimal_value(
            payload, "remaining_correlated_heat_budget", required=False
        )
        maximum_risk_fraction = decimal_value(
            payload, "maximum_risk_fraction", required=False
        )
        minimum_net_reward_risk = decimal_value(
            payload, "minimum_net_reward_risk", required=False
        )
        entry_timing_mode = str(
            payload.get("entry_timing_mode", "M15")
        ).upper()
        if entry_timing_mode not in {"M15", "HYBRID_M5"}:
            raise ValueError("entry_timing_mode must be M15 or HYBRID_M5")
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
            raise ValueError("invalid strategy_validation_status")
        if strategy_validation_status in {"REJECTED", "SUSPENDED"}:
            raise ValueError(
                "strategy_validation_status does not permit sizing"
            )

        fee = decimal_value(
            payload,
            "estimated_round_trip_fee_per_unit",
            required=True,
        )
        slippage = decimal_value(
            payload, "estimated_slippage_per_unit", required=True
        )
        financing = decimal_value(
            payload,
            "financing_and_borrow_buffer_per_unit",
            required=True,
        )
        platform_spread = decimal_value(
            payload,
            "platform_spread",
            required=entry_timing_mode == "HYBRID_M5",
        )
        maximum_spread_to_stop_fraction = decimal_value(
            payload,
            "maximum_spread_to_stop_fraction",
            required=False,
            default="0.2" if entry_timing_mode == "HYBRID_M5" else None,
        )
        maximum_total_cost_r = decimal_value(
            payload,
            "maximum_total_cost_r",
            required=False,
            default="0.25" if entry_timing_mode == "HYBRID_M5" else None,
        )
        spread_geometry_flag = payload.get(
            "spread_included_in_entry_exit_geometry"
        )
        if (
            entry_timing_mode == "HYBRID_M5"
            and not isinstance(spread_geometry_flag, bool)
        ):
            raise ValueError(
                "spread_included_in_entry_exit_geometry must be supplied "
                "as true or false for HYBRID_M5"
            )
        spread_included_in_geometry = spread_geometry_flag is True
        research_risk_cap_fraction = decimal_value(
            payload,
            "research_risk_cap_fraction",
            required=False,
            default="0.0025" if entry_timing_mode == "HYBRID_M5" else None,
        )
        contract_multiplier = decimal_value(
            payload, "contract_multiplier", required=False, default="1"
        )

        errors: list[str] = []
        positive_fields = {
            "entry_price": entry,
            "stop_price": stop,
            "value_per_price_unit": value_per_price_unit,
            "quantity_step": quantity_step,
            "minimum_quantity": minimum_quantity,
            "contract_multiplier": contract_multiplier,
        }
        errors.extend(
            f"{name} must be positive"
            for name, value in positive_fields.items()
            if value <= 0
        )
        if equity is not None and equity <= 0:
            errors.append("equity must be positive")
        if risk_fraction is not None and (
            risk_fraction <= 0 or risk_fraction > 1
        ):
            errors.append("risk_fraction must be greater than 0 and at most 1")
        if maximum_risk_fraction is not None and (
            maximum_risk_fraction <= 0 or maximum_risk_fraction > 1
        ):
            errors.append(
                "maximum_risk_fraction must be greater than 0 and at most 1"
            )
        if minimum_net_reward_risk is not None and minimum_net_reward_risk <= 0:
            errors.append("minimum_net_reward_risk must be positive")
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
        if maximum_total_cost_r is not None and maximum_total_cost_r <= 0:
            errors.append("maximum_total_cost_r must be positive")
        if (
            research_risk_cap_fraction is not None
            and (
                research_risk_cap_fraction <= 0
                or research_risk_cap_fraction > 1
            )
        ):
            errors.append(
                "research_risk_cap_fraction must be greater than 0 and at most 1"
            )
        if (equity is None) != (risk_fraction is None):
            errors.append("equity and risk_fraction must be supplied together")
        if side == "LONG" and stop >= entry:
            errors.append("LONG stop_price must be below entry_price")
        if side == "SHORT" and stop <= entry:
            errors.append("SHORT stop_price must be above entry_price")
        if target is not None and target <= 0:
            errors.append("target_price must be positive")
        if target is not None and side == "LONG" and target <= entry:
            errors.append("LONG target_price must be above entry_price")
        if target is not None and side == "SHORT" and target >= entry:
            errors.append("SHORT target_price must be below entry_price")
        optional_budgets = [
            ("explicit_risk_amount", explicit_budget),
            ("remaining_daily_loss_budget", daily_budget),
            ("remaining_portfolio_heat_budget", heat_budget),
            ("remaining_correlated_heat_budget", correlated_budget),
        ]
        errors.extend(
            f"{name} must be positive when supplied"
            for name, value in optional_budgets
            if value is not None and value <= 0
        )
        if explicit_budget is None and equity is None:
            errors.append(
                "supply explicit_risk_amount or both equity and risk_fraction"
            )
        if min(fee, slippage, financing) < 0:
            errors.append("cost buffers cannot be negative")
        if (
            entry_timing_mode == "HYBRID_M5"
            and strategy_validation_status != "ADVISORY_VALIDATED"
            and equity is None
        ):
            errors.append(
                "HYBRID_M5 research sizing requires equity to enforce "
                "the research risk cap"
            )
        if (
            entry_timing_mode == "HYBRID_M5"
            and strategy_validation_status != "ADVISORY_VALIDATED"
            and research_risk_cap_fraction is not None
            and risk_fraction is not None
            and risk_fraction > research_risk_cap_fraction
        ):
            errors.append(
                "HYBRID_M5 research risk_fraction exceeds "
                "research_risk_cap_fraction"
            )
        if errors:
            reject(errors)
            return 2

        price_stop_distance = abs(entry - stop)
        price_risk_per_unit = price_stop_distance * value_per_price_unit
        spread_to_stop_fraction: Decimal | None = None
        spread_cost_per_unit = Decimal("0")
        if platform_spread is not None:
            spread_to_stop_fraction = platform_spread / price_stop_distance
            if not spread_included_in_geometry:
                spread_cost_per_unit = platform_spread * value_per_price_unit
            if (
                maximum_spread_to_stop_fraction is not None
                and spread_to_stop_fraction > maximum_spread_to_stop_fraction
            ):
                reject(
                    [
                        "platform spread exceeds "
                        "maximum_spread_to_stop_fraction"
                    ]
                )
                return 2
        total_cost_per_unit = (
            fee + slippage + financing + spread_cost_per_unit
        )
        total_cost_r = total_cost_per_unit / price_risk_per_unit
        if (
            maximum_total_cost_r is not None
            and total_cost_r > maximum_total_cost_r
        ):
            reject(["total execution cost exceeds maximum_total_cost_r"])
            return 2
        total_risk_per_unit = price_risk_per_unit + total_cost_per_unit
        if total_risk_per_unit <= 0:
            reject(["total_risk_per_unit must be positive"])
            return 2

        gross_reward_per_unit: Decimal | None = None
        estimated_net_reward_per_unit: Decimal | None = None
        gross_reward_risk: Decimal | None = None
        estimated_net_reward_risk: Decimal | None = None
        break_even_win_rate: Decimal | None = None
        if target is not None:
            gross_reward_per_unit = abs(target - entry) * value_per_price_unit
            estimated_net_reward_per_unit = (
                gross_reward_per_unit - total_cost_per_unit
            )
            gross_reward_risk = gross_reward_per_unit / price_risk_per_unit
            estimated_net_reward_risk = (
                estimated_net_reward_per_unit / total_risk_per_unit
            )
            if estimated_net_reward_per_unit <= 0:
                reject(["estimated net reward must be positive"])
                return 2
            if (
                minimum_net_reward_risk is not None
                and estimated_net_reward_risk < minimum_net_reward_risk
            ):
                reject(
                    [
                        "estimated net reward-to-risk is below "
                        "minimum_net_reward_risk"
                    ]
                )
                return 2
            break_even_win_rate = total_risk_per_unit / (
                total_risk_per_unit + estimated_net_reward_per_unit
            )

        risk_budget_candidates: list[Decimal] = []
        if equity is not None and risk_fraction is not None:
            risk_budget_candidates.append(equity * risk_fraction)
        if equity is not None and maximum_risk_fraction is not None:
            risk_budget_candidates.append(equity * maximum_risk_fraction)
        if explicit_budget is not None:
            risk_budget_candidates.append(explicit_budget)
        if (
            equity is not None
            and entry_timing_mode == "HYBRID_M5"
            and strategy_validation_status != "ADVISORY_VALIDATED"
            and research_risk_cap_fraction is not None
        ):
            risk_budget_candidates.append(
                equity * research_risk_cap_fraction
            )
        if daily_budget is not None:
            risk_budget_candidates.append(daily_budget)
        if heat_budget is not None:
            risk_budget_candidates.append(heat_budget)
        if correlated_budget is not None:
            risk_budget_candidates.append(correlated_budget)
        risk_budget = min(risk_budget_candidates)
        quantity_caps = [risk_budget / total_risk_per_unit]

        max_notional = payload.get("max_notional")
        if max_notional is not None:
            maximum = decimal_value(payload, "max_notional")
            if maximum <= 0:
                reject(["max_notional must be positive"])
                return 2
            quantity_caps.append(maximum / (entry * contract_multiplier))

        if payload.get("available_margin") is not None or payload.get("margin_per_unit") is not None:
            available_margin = decimal_value(payload, "available_margin")
            margin_per_unit = decimal_value(payload, "margin_per_unit")
            if available_margin <= 0 or margin_per_unit <= 0:
                reject(["available_margin and margin_per_unit must be positive"])
                return 2
            quantity_caps.append(available_margin / margin_per_unit)

        if payload.get("max_quantity") is not None:
            maximum_quantity = decimal_value(payload, "max_quantity")
            if maximum_quantity <= 0:
                reject(["max_quantity must be positive"])
                return 2
            quantity_caps.append(maximum_quantity)

        indicative_quantity = floor_to_step(min(quantity_caps), quantity_step)
        if indicative_quantity < minimum_quantity:
            reject(["calculated quantity is below minimum_quantity"])
            return 2

        requested_quantity = payload.get("requested_quantity")
        status = "CALCULATED"
        if requested_quantity is not None:
            requested = decimal_value(payload, "requested_quantity")
            if requested <= 0:
                reject(["requested_quantity must be positive"])
                return 2
            requested = floor_to_step(requested, quantity_step)
            if requested < indicative_quantity:
                indicative_quantity = requested
            elif requested > indicative_quantity:
                status = "REDUCED_TO_LIMIT"

        indicative_risk = indicative_quantity * total_risk_per_unit
        indicative_net_reward = (
            indicative_quantity * estimated_net_reward_per_unit
            if estimated_net_reward_per_unit is not None
            else None
        )
        indicative_notional = indicative_quantity * entry * contract_multiplier
        result = {
            "status": status,
            "indicative_quantity": text_number(indicative_quantity),
            "risk_budget": text_number(risk_budget),
            "entry_timing_mode": entry_timing_mode,
            "strategy_validation_status": strategy_validation_status,
            "price_stop_distance": text_number(price_stop_distance),
            "price_risk_per_unit": text_number(price_risk_per_unit),
            "spread_cost_per_unit": text_number(spread_cost_per_unit),
            "total_cost_per_unit": text_number(total_cost_per_unit),
            "spread_to_stop_fraction": (
                text_number(spread_to_stop_fraction)
                if spread_to_stop_fraction is not None
                else None
            ),
            "total_cost_r": text_number(total_cost_r),
            "total_risk_per_unit": text_number(total_risk_per_unit),
            "indicative_risk_amount": text_number(indicative_risk),
            "indicative_net_reward_amount": (
                text_number(indicative_net_reward)
                if indicative_net_reward is not None
                else None
            ),
            "gross_reward_risk": (
                text_number(gross_reward_risk)
                if gross_reward_risk is not None
                else None
            ),
            "estimated_net_reward_risk": (
                text_number(estimated_net_reward_risk)
                if estimated_net_reward_risk is not None
                else None
            ),
            "break_even_win_rate": (
                text_number(break_even_win_rate)
                if break_even_win_rate is not None
                else None
            ),
            "indicative_notional": text_number(indicative_notional),
            "quantity_step": text_number(quantity_step),
            "rounding": "DOWN",
            "quantity_label": "INDICATIVE_ONLY",
            "agent_may_submit_orders": False,
            "broker_connection_required": False,
            "xtb_interaction_allowed": False,
            "errors": [],
        }
        print(json.dumps(result, indent=2))
        return 0
    except (json.JSONDecodeError, ValueError) as exc:
        reject([str(exc)])
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
