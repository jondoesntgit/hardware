"""Ensures that the gyro plays nice with all of the hardware."""

import pytest
try:
    from hardware import u, log_filename, fog
except ImportError:
    pytestmark = pytest.mark.skip


def test_initialize():
    """Check that the fog object initializes properly."""
    assert fog.name
    with open(log_filename) as file:
        string = "Gyro '%s' loaded."
        assert string in file.read()


def test_scale_factor():
    """Ensure that the scale factor is timely and in the right units."""
    sf = fog.get_scale_factor()
    assert sf.units == (u.deg / u.hour) / u.volt


def test_tombstone():
    """Take a tombstone measurement, and make sure data makes sense."""
    seconds = 10  # currently set as the minimum amount of time
                  # to get noise

    # Run without a scale factor calibration
    tmb1 = fog.tombstone(seconds=seconds)
    print(tmb1.scale_factor)
    # Run with a scale factor calibration
    tmb2 = fog.tombstone(seconds=seconds, scale_factor=tmb1.scale_factor)

    # Check that their noises are roughly equivalent
    noise_ratio = tmb1.noise / tmb2.noise
    assert noise_ratio > .8 and noise_ratio < 1.2
