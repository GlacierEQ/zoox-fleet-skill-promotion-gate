"""Auto-generated tests for Autonomous Vehicle Safety & Perception."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import math
from zoox_fleet_skill_promotion_gate.core import OccupancyCell, OccupancyGrid, SafetyEnvelope

def test_cell_bayesian_update():
    cell = OccupancyCell(0, 0, probability=0.5)
    cell.update(0.9)
    assert cell.probability > 0.5

def test_cell_occupied():
    cell = OccupancyCell(0, 0, probability=0.5)
    cell.update(0.95)
    cell.update(0.95)
    assert cell.is_occupied

def test_cell_free():
    cell = OccupancyCell(0, 0, probability=0.5)
    cell.update(0.05)
    cell.update(0.05)
    assert cell.is_free

def test_grid_init():
    grid = OccupancyGrid(10, 10)
    assert abs(grid.free_space_ratio() - 0.0) < 0.01  # all unknown

def test_grid_update():
    grid = OccupancyGrid(5, 5)
    grid.update_cell(2, 2, 0.95)
    grid.update_cell(2, 2, 0.95)
    assert (2, 2) in grid.occupied_cells()

def test_safety_envelope_straight():
    env = SafetyEnvelope(max_speed_ms=30.0, min_following_distance_m=50.0)
    assert env.safe_speed(0.0) == 30.0

def test_safety_envelope_curve():
    env = SafetyEnvelope(max_speed_ms=30.0, min_following_distance_m=50.0)
    v = env.safe_speed(0.01)  # 100m radius
    assert v < 30.0
    assert v > 0.0

def test_stopping_distance():
    env = SafetyEnvelope(max_speed_ms=30.0, min_following_distance_m=50.0)
    d = env.stopping_distance(20.0)
    assert d > 0.0
    assert d < 100.0  # reasonable for 20 m/s

