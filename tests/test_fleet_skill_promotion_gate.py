from __future__ import annotations

import pytest

from fleet_skill_promotion_gate import (
    Decision,
    FleetSkillPromotionGate,
    PromotionContract,
    ValidationReceipt,
)


def contract(**overrides):
    data = dict(
        skill_version="v2",
        required_scenarios=("nominal", "sensor-loss", "remote-assist-loss"),
        min_units=3,
        min_failure_domains=2,
        max_receipt_age_s=60.0,
    )
    data.update(overrides)
    return PromotionContract(**data)


def receipt(unit, domain, *, passed=True, scenarios=None, observed_at=100.0, version="v2"):
    return ValidationReceipt(
        unit_id=unit,
        failure_domain=domain,
        skill_version=version,
        scenarios=scenarios or ("nominal", "sensor-loss", "remote-assist-loss"),
        passed=passed,
        observed_at=observed_at,
        evidence_digest=f"evidence-{unit}",
    )


def good_receipts():
    return [receipt("u1", "fd-a"), receipt("u2", "fd-a"), receipt("u3", "fd-b")]


def test_promotes_only_after_multi_unit_failure_domain_validation():
    out = FleetSkillPromotionGate().evaluate(good_receipts(), contract(), now=120.0)
    assert out.decision is Decision.PROMOTE
    assert out.validated_units == ("u1", "u2", "u3")
    assert out.failure_domains == ("fd-a", "fd-b")
    assert out.release_token
    assert out.quarantine_token is None


def test_single_failure_domain_quarantines_even_with_enough_units():
    receipts = [receipt("u1", "fd-a"), receipt("u2", "fd-a"), receipt("u3", "fd-a")]
    out = FleetSkillPromotionGate().evaluate(receipts, contract(), now=120.0)
    assert out.decision is Decision.QUARANTINE
    assert "insufficient_failure_domain_independence" in out.reasons
    assert out.quarantine_token


def test_failed_target_receipt_forces_quarantine():
    receipts = good_receipts() + [receipt("u4", "fd-c", passed=False)]
    out = FleetSkillPromotionGate().evaluate(receipts, contract(), now=120.0)
    assert out.decision is Decision.QUARANTINE
    assert "failed_validation_present" in out.reasons


def test_partial_scenario_receipt_does_not_count_as_validated_unit():
    receipts = [receipt("u1", "fd-a", scenarios=("nominal",)), receipt("u2", "fd-a"), receipt("u3", "fd-b")]
    out = FleetSkillPromotionGate().evaluate(receipts, contract(), now=120.0)
    assert out.decision is Decision.QUARANTINE
    assert "partial_scenario_receipt_present" in out.reasons
    assert "insufficient_validated_units" in out.reasons


def test_stale_receipt_does_not_count():
    receipts = [receipt("u1", "fd-a", observed_at=1.0), receipt("u2", "fd-a"), receipt("u3", "fd-b")]
    out = FleetSkillPromotionGate().evaluate(receipts, contract(), now=120.0)
    assert out.decision is Decision.QUARANTINE
    assert "stale_receipt_present" in out.reasons


def test_clean_evidence_can_release_a_prior_quarantine():
    gate = FleetSkillPromotionGate()
    quarantined = gate.evaluate([receipt("u1", "fd-a")], contract(), now=120.0)
    assert quarantined.quarantine_token
    released = gate.evaluate(good_receipts(), contract(), now=120.0, prior_quarantine_token=quarantined.quarantine_token)
    assert released.decision is Decision.PROMOTE
    assert released.release_token


def test_duplicate_unit_receipts_are_rejected_not_double_counted():
    with pytest.raises(ValueError, match="duplicate_unit_receipt"):
        FleetSkillPromotionGate().evaluate([receipt("u1", "a"), receipt("u1", "b")], contract(), now=120.0)
