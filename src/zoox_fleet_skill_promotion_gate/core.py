"""Autonomous Vehicle Safety & Perception — Core Module"""

import math
from dataclasses import dataclass, field

@dataclass
class OccupancyCell:
    """A single cell in the occupancy grid."""
    x: int
    y: int
    probability: float = 0.5  # Prior: unknown

    def update(self, measurement_prob: float) -> None:
        """Bayesian update with new measurement."""
        # Log-odds update for numerical stability
        prior_lo = math.log(self.probability / (1.0 - self.probability + 1e-10))
        meas_lo = math.log(measurement_prob / (1.0 - measurement_prob + 1e-10))
        posterior_lo = prior_lo + meas_lo
        self.probability = 1.0 / (1.0 + math.exp(-posterior_lo))

    @property
    def is_occupied(self) -> bool:
        return self.probability > 0.7

    @property
    def is_free(self) -> bool:
        return self.probability < 0.3


class OccupancyGrid:
    """2D probabilistic occupancy grid."""

    def __init__(self, width: int, height: int, resolution_m: float = 0.1):
        self.width = width
        self.height = height
        self.resolution = resolution_m
        self.cells = [[OccupancyCell(x, y) for y in range(height)] for x in range(width)]

    def update_cell(self, x: int, y: int, prob: float) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[x][y].update(prob)

    def free_space_ratio(self) -> float:
        total = self.width * self.height
        free = sum(1 for row in self.cells for c in row if c.is_free)
        return free / total

    def occupied_cells(self) -> list[tuple[int, int]]:
        return [(c.x, c.y) for row in self.cells for c in row if c.is_occupied]


@dataclass
class SafetyEnvelope:
    """Dynamic safety envelope for vehicle operation."""
    max_speed_ms: float
    min_following_distance_m: float
    max_lateral_accel_g: float = 0.3
    max_decel_g: float = 0.5

    def safe_speed(self, curvature_1_per_m: float) -> float:
        """Max safe speed for a given road curvature."""
        if curvature_1_per_m <= 0:
            return self.max_speed_ms
        g = 9.80665
        radius = 1.0 / curvature_1_per_m
        v = math.sqrt(self.max_lateral_accel_g * g * radius)
        return min(v, self.max_speed_ms)

    def stopping_distance(self, speed_ms: float) -> float:
        """Minimum stopping distance at given speed."""
        g = 9.80665
        decel = self.max_decel_g * g
        return (speed_ms ** 2) / (2.0 * decel)

