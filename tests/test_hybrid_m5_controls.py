from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPOSITORY_ROOT / "skills"
CALCULATOR = (
    SKILLS_ROOT
    / "portfolio-risk-manager"
    / "scripts"
    / "calculate_position_size.py"
)
VALIDATOR = (
    SKILLS_ROOT
    / "order-execution-controls"
    / "scripts"
    / "validate_order.py"
)
SCANNER = (
    SKILLS_ROOT
    / "market-data-acquisition"
    / "scripts"
    / "scan_public_markets.mjs"
)


def run_json_script(
    script: Path, payload: dict
) -> tuple[subprocess.CompletedProcess[str], dict]:
    completed = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        cwd=REPOSITORY_ROOT,
        check=False,
    )
    return completed, json.loads(completed.stdout)


def valid_sizing_payload() -> dict:
    return {
        "realtime_execution_data_source": "USER_PROVIDED_REALTIME",
        "xtb_interaction_allowed": False,
        "side": "LONG",
        "entry_timing_mode": "HYBRID_M5",
        "strategy_validation_status": "RESEARCH_ONLY",
        "entry_price": 85.10,
        "stop_price": 84.50,
        "target_price": 86.30,
        "value_per_price_unit": 300,
        "quantity_step": 0.01,
        "minimum_quantity": 0.01,
        "equity": 2000,
        "risk_fraction": 0.0025,
        "remaining_daily_loss_budget": 40,
        "remaining_portfolio_heat_budget": 40,
        "remaining_correlated_heat_budget": 30,
        "estimated_round_trip_fee_per_unit": 0,
        "estimated_slippage_per_unit": 3,
        "financing_and_borrow_buffer_per_unit": 0,
        "platform_spread": 0.06,
        "spread_included_in_entry_exit_geometry": True,
        "maximum_spread_to_stop_fraction": 0.20,
        "maximum_total_cost_r": 0.25,
        "research_risk_cap_fraction": 0.0025,
        "contract_multiplier": 1,
        "minimum_net_reward_risk": 1.5,
    }


def valid_ticket_payload() -> dict:
    now_ms = int(time.time() * 1000)
    return {
        "execution_state": "PLATFORM_TICKET_READY",
        "realtime_execution_data_source": "USER_PROVIDED_REALTIME",
        "xtb_interaction_allowed": False,
        "decision_id": "decision-test",
        "risk_plan_id": "risk-test",
        "session_id": "test-US_CASH",
        "instrument": "OIL.WTI",
        "asset_class": "ENERGY",
        "public_reference_basis": "CL_FRONT_MONTH_REFERENCE",
        "side": "LONG",
        "entry_timing_mode": "HYBRID_M5",
        "strategy_validation_status": "RESEARCH_ONLY",
        "order_mode": "MARKET",
        "order_type": "MARKET",
        "checked_at_epoch_ms": now_ms,
        "signal_expires_at_epoch_ms": now_ms + 600_000,
        "platform_quote_observed_at_epoch_ms": now_ms - 5_000,
        "maximum_quote_age_seconds": 30,
        "trigger_bar_completed_at_epoch_ms": now_ms - 60_000,
        "maximum_trigger_bar_age_seconds": 300,
        "trigger_timeframe": "M5",
        "trigger_bar_completed": True,
        "higher_timeframe_alignment_confirmed": True,
        "entry_price_for_calculation": 85.10,
        "stop_loss": 84.50,
        "targets": [86.30],
        "platform_bid": 85.04,
        "platform_ask": 85.10,
        "platform_spread": 0.06,
        "maximum_spread_to_stop_fraction": 0.20,
        "valid_market_entry_low": 85.00,
        "valid_market_entry_high": 85.20,
        "optional_tick_size": 0.01,
        "optional_quantity": 0.02,
        "quantity_source": "RISK_CALCULATED",
        "optional_quantity_step": 0.01,
        "estimated_cost_per_unit": 0.01,
        "maximum_total_cost_r": 0.25,
        "minimum_reward_risk": 1.5,
        "account_profile_id": "user-cfd-usd-2000-v1",
        "account_profile_status": "ACTIVE_CONFIRMED",
        "confirmed_account_equity": 2000,
        "estimated_loss_at_stop": 3.66,
        "estimated_net_profit_at_target": 7.14,
        "existing_open_risk_amount": 0,
        "maximum_trade_risk_fraction": 0.0025,
        "research_risk_cap_fraction": 0.0025,
        "maximum_portfolio_heat_fraction": 0.02,
        "observed_public_price": 85.04,
        "maximum_reference_deviation_fraction": 0.01,
        "stated_delay_seconds": 600,
    }


class HybridM5ControlsTest(unittest.TestCase):
    def test_scanner_self_test(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("node executable is unavailable")
        completed = subprocess.run(
            [node, str(SCANNER), "--self-test"],
            text=True,
            capture_output=True,
            cwd=REPOSITORY_ROOT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "PASS")

    def test_hybrid_sizing_requires_explicit_costs(self) -> None:
        payload = valid_sizing_payload()
        for key in (
            "estimated_round_trip_fee_per_unit",
            "estimated_slippage_per_unit",
            "financing_and_borrow_buffer_per_unit",
        ):
            payload.pop(key)
        completed, result = run_json_script(CALCULATOR, payload)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(result["status"], "NOT_CALCULATED")
        self.assertIn("missing required field", result["errors"][0])

    def test_hybrid_sizing_applies_research_cap_and_cost_gates(self) -> None:
        completed, result = run_json_script(
            CALCULATOR, valid_sizing_payload()
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(result["status"], "CALCULATED")
        self.assertEqual(result["risk_budget"], "5")
        self.assertEqual(result["indicative_quantity"], "0.02")
        self.assertEqual(result["spread_to_stop_fraction"], "0.1")
        self.assertGreater(float(result["estimated_net_reward_risk"]), 1.8)

    def test_hybrid_research_cap_requires_confirmed_equity(self) -> None:
        payload = valid_sizing_payload()
        payload.pop("equity")
        payload.pop("risk_fraction")
        payload["explicit_risk_amount"] = 5
        completed, result = run_json_script(CALCULATOR, payload)
        self.assertEqual(completed.returncode, 2)
        self.assertIn(
            "HYBRID_M5 research sizing requires equity to enforce "
            "the research risk cap",
            result["errors"],
        )

    def test_stale_hybrid_quote_invalidates_and_empties_ticket(self) -> None:
        payload = valid_ticket_payload()
        payload["platform_quote_observed_at_epoch_ms"] = (
            payload["checked_at_epoch_ms"] - 120_000
        )
        completed, result = run_json_script(VALIDATOR, payload)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(result["status"], "MANUAL_TICKET_INVALID")
        self.assertIn(
            "platform quote is stale for HYBRID_M5", result["errors"]
        )
        self.assertIsNone(result["platform_ticket"]["button"])
        self.assertIsNone(result["platform_ticket"]["price"])

    def test_current_hybrid_ticket_passes_with_disclosed_delay(self) -> None:
        completed, result = run_json_script(
            VALIDATOR, valid_ticket_payload()
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(result["status"], "MANUAL_TICKET_WARNING")
        self.assertEqual(result["platform_ticket"]["button"], "BUY")
        self.assertEqual(result["hybrid_checks"]["trigger_timeframe"], "M5")
        self.assertEqual(
            result["total_cost_r"],
            "0.01666666666666666666666666667",
        )

    def test_suspended_strategy_cannot_size_or_create_ticket(self) -> None:
        sizing = valid_sizing_payload()
        sizing["strategy_validation_status"] = "SUSPENDED"
        sizing_process, sizing_result = run_json_script(CALCULATOR, sizing)
        self.assertEqual(sizing_process.returncode, 2)
        self.assertIn(
            "strategy_validation_status does not permit sizing",
            sizing_result["errors"],
        )

        ticket = valid_ticket_payload()
        ticket["strategy_validation_status"] = "SUSPENDED"
        ticket_process, ticket_result = run_json_script(VALIDATOR, ticket)
        self.assertEqual(ticket_process.returncode, 2)
        self.assertIn(
            "strategy_validation_status does not permit a ticket",
            ticket_result["errors"],
        )
        self.assertIsNone(ticket_result["platform_ticket"]["button"])


if __name__ == "__main__":
    unittest.main()
