"""A set of functions that test the LIA."""
import pytest
try:
    from hardware import Q_, u, log_filename, lia
except ImportError:
    pytestmark = pytest.mark.skip


def test_phase():
    """Test the LIA phase functions."""
    # units in degrees
    start_phase = lia.phase
    assert start_phase.units == "degree"

    # Must be between -180 to 180 degrees
    with pytest.raises(ValueError):
        lia.phase = 200 * u.degree

    # change in logging file
    with open(log_filename) as file:
        string = "Phase set to %f" % lia.phase.magnitude
        assert string in file.read()

    # Restore
    lia.phase = start_phase


def test_sensitivity():
    """Test the LIA sensitivity."""
    start_sensitivity = lia.sensitivity
    assert start_sensitivity.units == "volt"

    # Sensitivity must be within the length of the sensitivity dictionary
    with pytest.raises(ValueError):
        lia.sensitivity = Q_(30, 'volt')

    lia.sensitivity = Q_(.1, 'volt')

    # change in logging file
    with open(log_filename) as file:
        string = "Sensitivity set to %f V." % lia.sensitivity.magnitude
        assert string in file.read()

    # Restore
    lia.sensitivity = start_sensitivity


def test_identify():
    """Ensure LIA can identify itself and its serial numbers."""
    print(lia.identify())


def test_time_constant():
    """Test the LIA Time constant."""
    start_time_constant = lia.time_constant
    assert start_time_constant.units == "second"
    with pytest.raises(ValueError):
        lia.time_constant = 2 * u.second

    lia.time_constant = 3 * u.second
    with open(log_filename) as file:
        string = "Time constant set to %f" % lia.time_constant.magnitude
        assert string in file.read()

    # Restore
    lia.time_constant = start_time_constant
