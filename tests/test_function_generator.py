from hardware import awg
from hardware import u
from hardware import file


def test_frequency():
    assert awg.frequency.units == "hertz"
    try:
        awg.frequency = .5 * u.microhertz
    except(ValueError):
        print("Invalid frequency successfully caught in awg")
    awg.frequency = 100 * u.kilohertz
    assert ("Frequency set to %f" % awg.frequency.magnitude) in file.read()


def test_volt():
    assert awg.volt.units == "volt"
    awg.volt = 1 * u.volt
    assert ("Voltage set to %i" % awg.volt.magnitude) in file.read()


def test_phase():
    assert awg.phase.units == "degree"
    try:
        awg.phase = 700 * u.degree
    except(ValueError):
        print("Invalid phase successfully caught in awg")

    awg.phase = 120 * u.degree
    assert ("Phase set to %f" % awg.phase.magnitude) in file.read()
