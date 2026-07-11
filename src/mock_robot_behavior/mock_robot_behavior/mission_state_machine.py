from __future__ import annotations

from enum import StrEnum


class MissionState(StrEnum):
    IDLE = "IDLE"
    VALIDATING = "VALIDATING"
    NAVIGATING = "NAVIGATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EMERGENCY_STOPPED = "EMERGENCY_STOPPED"


class InvalidMissionTransition(RuntimeError):
    """Raised when a mission state transition would hide a behavior bug."""


class MissionStateMachine:
    def __init__(self) -> None:
        self._state = MissionState.IDLE

    @property
    def state(self) -> MissionState:
        return self._state

    def transition_to(self, new_state: MissionState, message: str = "") -> None:
        allowed = {
            MissionState.IDLE: {MissionState.VALIDATING, MissionState.EMERGENCY_STOPPED},
            MissionState.VALIDATING: {
                MissionState.NAVIGATING,
                MissionState.FAILED,
                MissionState.EMERGENCY_STOPPED,
            },
            MissionState.NAVIGATING: {
                MissionState.COMPLETED,
                MissionState.FAILED,
                MissionState.EMERGENCY_STOPPED,
            },
            MissionState.COMPLETED: {MissionState.IDLE},
            MissionState.FAILED: {MissionState.IDLE},
            MissionState.EMERGENCY_STOPPED: {MissionState.IDLE},
        }
        if new_state not in allowed[self._state]:
            detail = f"Cannot transition from {self._state.value} to {new_state.value}"
            if message:
                detail = f"{detail}: {message}"
            raise InvalidMissionTransition(detail)
        self._state = new_state

    def begin_validation(self) -> None:
        self.transition_to(MissionState.VALIDATING)

    def begin_navigation(self) -> None:
        self.transition_to(MissionState.NAVIGATING)

    def complete(self) -> None:
        self.transition_to(MissionState.COMPLETED)

    def fail(self) -> None:
        self.transition_to(MissionState.FAILED)

    def emergency_stop(self) -> None:
        if self._state != MissionState.EMERGENCY_STOPPED:
            if self._state in {MissionState.COMPLETED, MissionState.FAILED}:
                self._state = MissionState.EMERGENCY_STOPPED
            else:
                self.transition_to(MissionState.EMERGENCY_STOPPED)

    def reset(self) -> None:
        if self._state != MissionState.IDLE:
            self.transition_to(MissionState.IDLE)

    def fail_if_timed_out(self, elapsed_seconds: float, timeout_seconds: float) -> bool:
        if self._state not in {MissionState.VALIDATING, MissionState.NAVIGATING}:
            return False
        if timeout_seconds <= 0.0:
            return False
        if elapsed_seconds >= timeout_seconds:
            self.fail()
            return True
        return False
