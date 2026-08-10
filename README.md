# Fleet Skill Promotion Gate

Independent GlacierEQ portfolio exhibit aligned to **Zoox** operating themes.

> **Not affiliated.** This repository is not affiliated with, endorsed by, employed by, or deployed at Zoox. No proprietary access, production deployment, customer impact, or company partnership is claimed.

## Implemented mechanism

`FleetSkillPromotionGate` promotes a skill version only after fresh, scenario-complete validation receipts establish both multi-unit coverage and independent failure-domain coverage.

Hard boundaries:

- each unit may contribute only one receipt;
- target-version failures force quarantine;
- stale, future, or partial-scenario receipts do not count;
- promotion requires minimum distinct units and failure domains;
- required scenarios must be covered;
- incomplete evidence emits a deterministic quarantine token;
- a later complete evidence set can emit a release token bound to the prior quarantine.

## Proof surface

- `src/fleet_skill_promotion_gate.py` — multi-unit promotion/quarantine mechanism
- `tests/test_fleet_skill_promotion_gate.py` — unit count, failure domains, failure, staleness, partial coverage, release tests
- `scripts/operate.py` — direct three-unit/two-domain promotion execution
- `.github/workflows/tests.yml` — pytest + operate CI

## Current boundary

This is a synthetic safety-governance reference model. It does not use vehicle telemetry, proprietary autonomy systems, or production fleet data. The next gate is a richer non-vehicle failure simulation with explicit correlated-failure scenarios.
