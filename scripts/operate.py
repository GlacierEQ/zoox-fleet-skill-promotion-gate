#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fleet_skill_promotion_gate import FleetSkillPromotionGate, PromotionContract, ValidationReceipt


def main() -> int:
    contract = PromotionContract(
        skill_version="demo-v1",
        required_scenarios=("nominal", "sensor-loss", "remote-assist-loss"),
        min_units=3,
        min_failure_domains=2,
        max_receipt_age_s=60.0,
    )
    receipts = (
        ValidationReceipt("unit-1", "domain-a", "demo-v1", contract.required_scenarios, True, 100.0, "e1"),
        ValidationReceipt("unit-2", "domain-a", "demo-v1", contract.required_scenarios, True, 100.0, "e2"),
        ValidationReceipt("unit-3", "domain-b", "demo-v1", contract.required_scenarios, True, 100.0, "e3"),
    )
    receipt = FleetSkillPromotionGate().evaluate(receipts, contract, now=120.0)
    print(json.dumps(receipt.as_dict(), sort_keys=True))
    return 0 if receipt.decision.value == "PROMOTE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
