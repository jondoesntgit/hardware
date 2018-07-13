"""General tests for all function generators."""

import pytest
from decimal import getcontext, Decimal


class Dummy:
    """Helps the decorators to mark functions to skip if awg isn't loaded."""

    pass


# if it's the HP awg, it won't have the output attribute
# TODO: HP awg can't change output from remote interface, find a way to test
try:
    from hardware import u, log_filename, awg
    pytest.initial_output_state = awg.output
    awg.output = False
except (ImportError, AttributeError, NameError):  # awg can't be imported
    pytestmark = pytest.mark.skip
    awg = Dummy()
    awg.output = True


@pytest.mark.skipif(hasattr(awg, "output") and awg.output, reason=("sheepishly"
                    "refusing to change settings while output is enabled"))
def test_frequency():
    """Ensure the hardware can modify the frequency."""
    freq = awg.frequency
    assert freq.units == "hertz"
    awg.frequency = 100 * u.kilohertz

    with open(log_filename) as file:
        string = "Frequency set to %f Hz." % awg.frequency.magnitude
        assert string in file.read()
    awg.frequency = freq


@pytest.mark.skipif(hasattr(awg, "output") and awg.output, reason=("sheepishly"
                    "refusing to change settings while output is enabled"))
def test_voltage():
    """Ensure the hardware can modify the voltage."""
    assert awg.volt.units == "volt"
    initial_voltage = awg.voltage
    awg.voltage = 1 * u.volt

    with open(log_filename) as file:
        string = "Voltage set to %f V." % awg.voltage.magnitude
        assert string in file.read()
    awg.voltage = initial_voltage


@pytest.mark.skipif(hasattr(awg, "output") and awg.output, reason=("sheepishly"
                    "refusing to change settings while output is enabled"))
def test_phase():
    """Ensure the hardware can modify the phase."""
    assert awg.phase.units == u.degree or awg.phase.units == u.radian
    try:
        awg.phase = 700 * u.degree
    except(ValueError):
        print("Invalid phase successfully caught in awg")

    awg.phase = 120 * u.degree

    with open(log_filename) as file:
        string1 = "Phase set to %f degrees." % awg.phase.magnitude
        getcontext().prec = 5
        value = Decimal(awg.phase.magnitude)/Decimal(1.0)
        string2 = "Phase set to %f radians." % value
        assert (string2 in file.read() or string1 in file.read())


def test_waveform():
    """Cycle through the various waveforms available to the hardware."""
    initial_waveform = awg.waveform

    waveforms = 'SIN', 'SQU'

    for w in waveforms:
        awg.waveform = w
        assert awg.waveform == w

    with open(log_filename) as file:
        contents = file.read()
        for w in waveforms:
            string = "Waveform set to %s." % w
            assert string in contents

    awg.waveform = initial_waveform


@pytest.mark.skipif(not hasattr(awg, "output"), reason=("HP awg does not have "
                                                        "output attribute"))
def test_restore_function_generator_output_state():
    """Finally, return the function generator to original output mode."""
    if awg.output != pytest.initial_output_state:
        awg.output = pytest.initial_output_state

    with open(log_filename) as file:
        string1 = "Output enabled."
        string2 = "Output disabled."
        assert string1 in file.read() or string2 in file.read()
