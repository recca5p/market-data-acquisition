from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPOSITORY_ROOT / "skills"
ACQUISITION_SCHEMA = (
    SKILLS_ROOT
    / "market-data-acquisition"
    / "references"
    / "acquisition-schema.md"
)
SCANNER = (
    SKILLS_ROOT
    / "market-data-acquisition"
    / "scripts"
    / "scan_public_markets.mjs"
)
MARKET_ACQUISITION_SKILL = SKILLS_ROOT / "market-data-acquisition" / "SKILL.md"
CORE = REPOSITORY_ROOT / "core.md"
ORCHESTRATOR_SKILL = SKILLS_ROOT / "trade-orchestrator" / "SKILL.md"
WORKFLOW_CONTRACT = (
    SKILLS_ROOT
    / "trade-orchestrator"
    / "references"
    / "workflow-contract.md"
)
JOURNAL_SKILL = SKILLS_ROOT / "trade-journal-review" / "SKILL.md"
JOURNAL_SCHEMA = (
    SKILLS_ROOT
    / "trade-journal-review"
    / "references"
    / "journal-schema.md"
)


class MarketScanCoverageContractTest(unittest.TestCase):
    def test_schema_versions_and_canonical_audit_contract(self) -> None:
        acquisition_schema = ACQUISITION_SCHEMA.read_text(encoding="utf-8")
        scanner = SCANNER.read_text(encoding="utf-8")
        journal_schema = JOURNAL_SCHEMA.read_text(encoding="utf-8")

        self.assertIn('schema_version: "2.4"', acquisition_schema)
        self.assertIn('schema_version: "2.3"', journal_schema)
        self.assertIn('SCANNER_SCHEMA_VERSION = "1.2"', scanner)
        self.assertIn("coverage_audit:", acquisition_schema)
        self.assertIn("baseline_reuse:", acquisition_schema)
        self.assertIn("instrument_attempts:", acquisition_schema)
        self.assertIn("provider_market_state", acquisition_schema)
        self.assertIn("scan_coverage_audit:", journal_schema)
        self.assertIn("Existing append-only 2.2 events remain valid", journal_schema)

        required_buckets = (
            "FX",
            "EQUITY_INDICES",
            "RATES_SOVEREIGN_BONDS",
            "VOLATILITY",
            "PRECIOUS_METALS",
            "INDUSTRIAL_BASE_METALS",
            "ENERGY",
            "AGRICULTURE_SOFTS",
            "LIVESTOCK",
            "EMISSIONS_ENVIRONMENTAL",
            "FERTILIZER_CHEMICALS",
            "LIQUID_STOCKS",
        )
        for bucket in required_buckets:
            self.assertIn(bucket, acquisition_schema)
            self.assertIn(f'"{bucket}"', scanner)

        reason_codes = (
            "MARKET_CLOSED",
            "SESSION_INACTIVE",
            "STALE_TRIGGER_DATA",
            "NO_COMPLETED_TRIGGER",
            "MIXED_TIMEFRAME_STRUCTURE",
            "TRIGGER_INTEGRITY_FAILED",
            "OUTSIDE_VALID_ENTRY_ZONE",
            "OVEREXTENDED",
            "INSUFFICIENT_REWARD_RISK",
            "EVENT_RISK",
            "SOURCE_UNAVAILABLE",
            "IDENTITY_OR_BASIS_UNRESOLVED",
            "NO_LIQUID_IDENTIFIABLE_INSTRUMENT",
            "NOT_IN_REFRESH_SCOPE",
        )
        for reason_code in reason_codes:
            self.assertIn(reason_code, acquisition_schema)
        self.assertIn("NO_CONFIGURED_PUBLIC_REFERENCE", acquisition_schema)
        self.assertIn("ALUMINIUM", scanner)
        self.assertIn("EMISS", scanner)

    def test_handoff_and_vietnamese_response_instructions(self) -> None:
        contents = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                REPOSITORY_ROOT / "AGENTS.md",
                CORE,
                MARKET_ACQUISITION_SKILL,
                ORCHESTRATOR_SKILL,
                WORKFLOW_CONTRACT,
                JOURNAL_SKILL,
            )
        )

        for required_text in (
            "ĐÃ KHẢO SÁT",
            "SKIP/LOẠI VÀ LÝ DO",
            "coverage_audit",
            "NOT_IN_REFRESH_SCOPE",
            "NO_CONFIGURED_PUBLIC_REFERENCE",
            "Missing XTB",
            "baseline acquisition ID",
        ):
            self.assertIn(required_text, contents)
        self.assertIn("coverage_audit: {}", MARKET_ACQUISITION_SKILL.read_text(encoding="utf-8"))
        self.assertIn(
            "payload.scan_coverage_audit",
            JOURNAL_SKILL.read_text(encoding="utf-8"),
        )

    def test_scanner_offline_self_test_covers_audit_logic(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("node executable is unavailable")
        completed = subprocess.run(
            [node, str(SCANNER), "--self-test"],
            text=True,
            capture_output=True,
            cwd=REPOSITORY_ROOT,
            check=False,
            timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "PASS")
        self.assertIn(
            "coverage audit exposes aluminium and emissions configuration gaps",
            result["tests"],
        )
        self.assertIn(
            "session-core refresh marks non-core buckets NOT_IN_REFRESH_SCOPE",
            result["tests"],
        )


if __name__ == "__main__":
    unittest.main()
