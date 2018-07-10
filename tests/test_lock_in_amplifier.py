from hardware import lia
from hardware import u
from hardware import file


def test_phase():
    # units in degrees
    assert lia.phase.units == "degree"

    # Must be between -180 to 180 degrees
    try:
        lia.phase = 200 * u.degree
    except(ValueError):
        print("Invalid phase setting successfully caught in lia")

    lia.phase = 100 * u.degree

    # change in logging file
    assert ("Phase set to %f" % lia.phase.magnitude) in file.read()


def test_sensitivity():
    # units in volts
    assert lia.sensitivity.units == "volt"

    # Sensitivity must be within the length of the sensitivity dictionary
    try:
        lia.sensitivity = 30
    except(ValueError):
        print("Invalid sensitivity successfully caught in lia")

    lia.sensitvity = 5

    # change in logging file
    assert ("Sensitivity set to %f" % lia.sensitivity.magnitude) in file.read()


def test_identify():
    print(lia.indentify())


def test_time_const():
    assert lia.time_constant.units == "second"
    try:
        lia.time_constant = 2 * u.second
    except:
        print("Invalid time constant succesfully caught in lia")
    lia.time_constant = 3 * u.second
    assert ("Time constant set to %f" % lia.time_constant.magnitude) in file.read()
