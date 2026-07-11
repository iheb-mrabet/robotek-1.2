from __future__ import annotations

from dataclasses import dataclass
from math import hypot, isfinite


@dataclass(frozen=True)
class DestinationValidationResult:
    accepted: bool
    message: str


class DestinationValidator:
    def __init__(self, max_abs_coordinate: float = 4.5, min_distance: float = 0.05) -> None:
        self._max_abs_coordinate = max_abs_coordinate
        self._min_distance = min_distance

    def validate(
        self,
        target_x: float,
        target_y: float,
        current_x: float = 0.0,
        current_y: float = 0.0,
    ) -> DestinationValidationResult:
        if not isfinite(target_x) or not isfinite(target_y):
            return DestinationValidationResult(False, "Destination coordinates must be finite.")
        if abs(target_x) > self._max_abs_coordinate or abs(target_y) > self._max_abs_coordinate:
            return DestinationValidationResult(False, "Destination is outside the mock warehouse.")
        if hypot(target_x - current_x, target_y - current_y) < self._min_distance:
            return DestinationValidationResult(
                False, "Destination is too close to the current position."
            )
        return DestinationValidationResult(True, "Destination accepted.")
