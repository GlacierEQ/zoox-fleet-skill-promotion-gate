# DEV_UP_INSTRUCTIONS — implementation receipt

**Repository:** `GlacierEQ/zoox-fleet-skill-promotion-gate`  
**Company lens:** Zoox (independent; no affiliation)  
**Innovation:** Fleet Skill Promotion Gate

## Completed implementation

The generic scaffold has been replaced by a deterministic multi-unit validation mechanism with explicit failure-domain independence, quarantine, and release semantics.

### Shipped boundaries

- minimum distinct validated units
- minimum independent failure domains
- required scenario coverage
- target-version failure forces quarantine
- stale/future/partial receipts do not count
- duplicate unit receipts are rejected
- quarantine token emitted on incomplete/failed evidence
- release token emitted when later evidence satisfies the contract

## Verification contract

`python -m pytest -q` and `python scripts/operate.py` must pass for the current head. This proves a synthetic reference mechanism only; it does not prove vehicle safety or fleet deployment.

## Remaining next gate

Run correlated-failure simulations using non-vehicle synthetic units, expand scenario independence criteria, and bind any promotion claims to fresh implementation proof and external promotion authority.
