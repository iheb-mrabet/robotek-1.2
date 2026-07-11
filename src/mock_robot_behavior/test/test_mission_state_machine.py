import math

import pytest

from mock_robot_behavior.mission_state_machine import (
    InvalidMissionTransition,
    MissionState,
    MissionStateMachine,
)
from mock_robot_behavior.mission_validation import DestinationValidator


def test_valid_mission_state_transitions() -> None:
    machine = MissionStateMachine()
    machine.begin_validation()
    machine.begin_navigation()
    assert machine.state == MissionState.NAVIGATING


def test_invalid_state_transition_is_rejected() -> None:
    machine = MissionStateMachine()
    with pytest.raises(InvalidMissionTransition):
        machine.begin_navigation()


def test_valid_destination_acceptance() -> None:
    validator = DestinationValidator(max_abs_coordinate=4.5)
    result = validator.validate(1.0, -1.0)
    assert result.accepted


def test_invalid_destination_rejection() -> None:
    validator = DestinationValidator(max_abs_coordinate=4.5)
    assert not validator.validate(math.inf, 0.0).accepted
    assert not validator.validate(8.0, 0.0).accepted


def test_mission_timeout_handling() -> None:
    machine = MissionStateMachine()
    machine.begin_validation()
    machine.begin_navigation()
    assert machine.fail_if_timed_out(elapsed_seconds=31.0, timeout_seconds=30.0)
    assert machine.state == MissionState.FAILED


def test_emergency_stop_state_transition() -> None:
    machine = MissionStateMachine()
    machine.begin_validation()
    machine.emergency_stop()
    assert machine.state == MissionState.EMERGENCY_STOPPED


def test_completed_mission_transition() -> None:
    machine = MissionStateMachine()
    machine.begin_validation()
    machine.begin_navigation()
    machine.complete()
    assert machine.state == MissionState.COMPLETED


def test_invalid_transition_message_includes_context() -> None:
    machine = MissionStateMachine()
    with pytest.raises(InvalidMissionTransition, match="manual test context"):
        machine.transition_to(MissionState.COMPLETED, "manual test context")


def test_emergency_stop_after_completion_and_repeated_stop() -> None:
    machine = MissionStateMachine()
    machine.begin_validation()
    machine.begin_navigation()
    machine.complete()
    machine.emergency_stop()
    machine.emergency_stop()
    assert machine.state == MissionState.EMERGENCY_STOPPED


def test_reset_and_non_running_timeout_paths() -> None:
    machine = MissionStateMachine()
    assert not machine.fail_if_timed_out(elapsed_seconds=100.0, timeout_seconds=1.0)
    machine.reset()
    machine.begin_validation()
    assert not machine.fail_if_timed_out(elapsed_seconds=100.0, timeout_seconds=0.0)
    assert not machine.fail_if_timed_out(elapsed_seconds=1.0, timeout_seconds=30.0)
    machine.emergency_stop()
    machine.reset()
    assert machine.state == MissionState.IDLE


def test_destination_too_close_is_rejected() -> None:
    validator = DestinationValidator(max_abs_coordinate=4.5, min_distance=0.1)
    result = validator.validate(1.05, 1.05, current_x=1.0, current_y=1.0)
    assert not result.accepted
