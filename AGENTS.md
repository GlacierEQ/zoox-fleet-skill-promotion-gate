# AGENTS.md — zoox-fleet-skill-promotion-gate

**Company:** Zoox
**Domain:** Autonomous Vehicle Safety & Perception

## Quick Rules
- **Test command:** `PYTHONPATH=src pytest tests/ -v`
- **Lint:** `ruff check src/ tests/`
- **No drive-by edits** — load the skill first.

## Architecture
- `src/zoox_fleet_skill_promotion_gate/core.py` — Domain logic (Autonomous Vehicle Safety & Perception)
- `tests/` — Verified test suite
- `.github/workflows/ci.yml` — Enforced CI pipeline
