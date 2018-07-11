from hardware import lia
from hardware import u
from hardware import log_filename


def test_phase():
    # units in degrees
    phase = 1 * u.hectodegree
    lia.phase = phase
    assert lia.phase.units == u.degree

    try:
        lia.phase = 600 * u.degree
    except(ValueError):
        print("Invalid phase successfully caught in lia")

    # change in logging file
    with(open(log_filename)) as log_file:
        assert ("Phase set to %f degrees." % lia.phase.magnitude) in log_file.read()


def test_sensitivity():
    # units in volts
    sensitivity = .1 * u.hectovolt
    lia.sensitvity = sensitivity
    assert lia.sensitivity.units == u.volt

    # change in logging file
    with(open(log_filename)) as log_file:
        assert ("Sensitivity set to %f V." % lia.sensitivity.magnitude) in log_file.read()


def test_identify():
    print(lia.identify())


def test_time_const():
    time_const = 3 * u.second
    lia.time_constant = time_const
    assert lia.time_constant.units == u.second

    try:
        lia.time_constant = 2 * u.second
    except(ValueError):
        print("Invalid phase successfully caught in lia")

    with(open(log_filename)) as log_file:
        assert ("Time constant set to %f seconds." % lia.time_constant.magnitude) in log_file.read()
