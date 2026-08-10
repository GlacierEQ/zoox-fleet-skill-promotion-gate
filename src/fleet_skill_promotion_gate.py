"""Fleet Skill Promotion Gate — independent reference implementation.

Promotes a skill only when fresh validation receipts cover the required scenarios
across enough distinct units and independent failure domains. Any failed receipt
for the target skill version quarantines the skill until a later evidence set
satisfies the release contract.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable


class Decision(str, Enum):
    PROMOTE = "PROMOTE"
    QUARANTINE = "QUARANTINE"


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class ValidationReceipt:
    unit_id: str
    failure_domain: str
    skill_version: str
    scenarios: tuple[str, ...]
    passed: bool
    observed_at: float
    evidence_digest: str


@dataclass(frozen=True)
class PromotionContract:
    skill_version: str
    required_scenarios: tuple[str, ...]
    min_units: int
    min_failure_domains: int
    max_receipt_age_s: float

    def validate(self) -> None:
        if not self.skill_version.strip() or not self.required_scenarios:
            raise ValueError("contract_identity_missing")
        if len(set(self.required_scenarios)) != len(self.required_scenarios):
            raise ValueError("duplicate_required_scenario")
        if self.min_units <= 0 or self.min_failure_domains <= 0:
            raise ValueError("minimums_non_positive")
        if self.min_failure_domains > self.min_units:
            raise ValueError("failure_domains_exceed_units")
        if not math.isfinite(self.max_receipt_age_s) or self.max_receipt_age_s <= 0:
            raise ValueError("receipt_age_invalid")


@dataclass(frozen=True)
class FleetSkillPromotionReceipt:
    decision: Decision
    reasons: tuple[str, ...]
    skill_version: str
    validated_units: tuple[str, ...]
    failure_domains: tuple[str, ...]
    covered_scenarios: tuple[str, ...]
    quarantine_token: str | None
    release_token: str | None
    digest: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reasons": list(self.reasons),
            "skill_version": self.skill_version,
            "validated_units": list(self.validated_units),
            "failure_domains": list(self.failure_domains),
            "covered_scenarios": list(self.covered_scenarios),
            "quarantine_token": self.quarantine_token,
            "release_token": self.release_token,
            "digest": self.digest,
        }


class FleetSkillPromotionGate:
    def evaluate(
        self,
        receipts: Iterable[ValidationReceipt],
        contract: PromotionContract,
        *,
        now: float,
        prior_quarantine_token: str | None = None,
    ) -> FleetSkillPromotionReceipt:
        contract.validate()
        if not math.isfinite(now):
            raise ValueError("non_finite_now")
        required = set(contract.required_scenarios)
        seen_units: set[str] = set()
        valid: list[ValidationReceipt] = []
        reasons: list[str] = []
        failed_target_receipt = False

        for receipt in receipts:
            if not receipt.unit_id.strip() or not receipt.failure_domain.strip() or not receipt.evidence_digest.strip():
                raise ValueError("receipt_identity_missing")
            if receipt.unit_id in seen_units:
                raise ValueError("duplicate_unit_receipt")
            seen_units.add(receipt.unit_id)
            if not math.isfinite(receipt.observed_at):
                raise ValueError("receipt_time_invalid")
            if receipt.observed_at > now:
                reasons.append("future_receipt_present")
                continue
            if receipt.skill_version != contract.skill_version:
                continue
            if not receipt.passed:
                failed_target_receipt = True
                continue
            if now - receipt.observed_at > contract.max_receipt_age_s:
                reasons.append("stale_receipt_present")
                continue
            if not required.issubset(set(receipt.scenarios)):
                reasons.append("partial_scenario_receipt_present")
                continue
            valid.append(receipt)

        units = tuple(sorted(r.unit_id for r in valid))
        domains = tuple(sorted({r.failure_domain for r in valid}))
        covered = tuple(sorted(set().union(*(set(r.scenarios) for r in valid)) if valid else set()))
        if failed_target_receipt:
            reasons.append("failed_validation_present")
        if len(units) < contract.min_units:
            reasons.append("insufficient_validated_units")
        if len(domains) < contract.min_failure_domains:
            reasons.append("insufficient_failure_domain_independence")
        if not required.issubset(set(covered)):
            reasons.append("required_scenarios_not_covered")

        reasons = list(dict.fromkeys(reasons))
        decision = Decision.QUARANTINE if reasons else Decision.PROMOTE
        evidence = {
            "skill_version": contract.skill_version,
            "units": units,
            "domains": domains,
            "covered": covered,
            "required": sorted(required),
            "decision": decision.value,
            "reasons": reasons,
            "prior_quarantine_token": prior_quarantine_token,
        }
        decision_digest = _digest(evidence)
        quarantine_token = _digest({"quarantine": evidence}) if decision is Decision.QUARANTINE else None
        release_token = None
        if decision is Decision.PROMOTE:
            release_token = _digest({
                "release": evidence,
                "releases_quarantine": prior_quarantine_token,
            })
        return FleetSkillPromotionReceipt(
            decision=decision,
            reasons=tuple(reasons or ["multi_unit_validation_satisfied"]),
            skill_version=contract.skill_version,
            validated_units=units,
            failure_domains=domains,
            covered_scenarios=covered,
            quarantine_token=quarantine_token,
            release_token=release_token,
            digest=decision_digest,
        )


Mechanism = FleetSkillPromotionGate
