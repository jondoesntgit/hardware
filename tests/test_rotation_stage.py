"""Ensures that the rotation stage is working properly."""

import pytest
from hardware import rot, Q_, u, log_filename
import time

pytest.initial_values = {
    "angle": rot.angle,
    "velocity": rot.velocity,
    "max_angle": rot.max_angle,
    "min_angle": rot.min_angle
}


def test_units():
    """Ensure the units are in compliance."""
    assert rot.angle.units == u.degree
    assert rot.velocity.units == u.degree/u.second
    assert rot.max_angle.units == u.degree
    assert rot.min_angle.units == u.degree


def test_rotation():
    """Run a simple jog and check that the time is correct."""
    start_angle = Q_(0, 'deg')
    distance = Q_(1, 'deg')
    velocity = Q_(1, 'deg/sec')
    rot.velocity = Q_(1, 'deg/sec')
    rot.angle = start_angle

    stop_angle = start_angle + distance

    start_time = time.time()
    rot.angle = stop_angle
    stop_time = time.time()

    actual_time = stop_time - start_time
    expected_time = (distance / velocity).to('seconds').magnitude

    assert abs(actual_time - expected_time) < 3

    with open(log_filename) as file:
        contents = file.read()
        strings = (
            "Angle set to %f" % start_angle.to('deg').magnitude,
            "Angular velocity set to %f deg/s"
            % velocity.to('deg/s').magnitude,
            "Angle set to %f" % stop_angle.to('deg').magnitude,
        )

        for string in strings:
            assert string in contents


def test_restore_settings():
    """Reset the rotation stage to its former state."""
    rot.angle = pytest.initial_values['angle']
    rot.velocity = pytest.initial_values['velocity']
    rot.max_angle = pytest.initial_values['max_angle']
    rot.min_angle = pytest.initial_values['min_angle']
