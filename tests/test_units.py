from hardware import u, log_filename
import pint
import pytest

def test_unit_registry():
    assert type(u) == pint.registry.UnitRegistry

def test_ldd():
    try:
        from hardware import ldd
    except ImportError:
        pytest.skip("Hardware not defined")
    assert ldd.current.units == u.milliamp

def test_opm():
    try:
        from hardware import opm
    except ImportError:
        pytest.skip("Hardware not defined")
    assert opm.power.units == u.milliwatt

def test_spectum_analyzer():
    try:
        from hardware import rfsa
    except ImportError:
        pytest.skip("Hardware not defined")

    assert rfsa.center.units == u.hertz
    assert rfsa.start.units == u.hertz
    assert rfsa.stop.units == u.hertz
    assert rfsa.rbw.units == u.hertz
    assert rfsa.vbw.units == u.hertz
    assert rfsa.time.units == u.second
    assert rfsa.reference.units == u.watt

    initial_center = rfsa.center
    initial_stop = rfsa.stop
    inital_start = rfsa.start
    initial_rbw = rfsa.rbw
    initial_vbw = rfsa.vbw
    intial_time = rfsa.time
    intial_reference = rfsa.reference

    # Make sure test values are within acceptable range for instrument

    rfsa.center = 10 * u.megahertz
    rfsa.start = 8 * u.megahertz
    rfsa.stop = 12 * u.megahertz
    rfsa.rbw = 10 * u.hertz
    rfsa.vbw = 10 * u.hertz
    rfsa.time = .1 * u.hectoseconds
    rfsa.reference = 1 * u.milliwatt

    # TODO: Check if %s or %f should be used when writing to instrument and
    #       log file
    with open(log_filename) as file:
        assert "Center set to %f Hz." % rfsa.center.magnitude in file.read()
        assert "Start set to %f Hz." % rfsa.start.magnitude in file.read()
        assert "Stop set to %f Hz." % rfsa.stop.magnitude in file.read()
        assert "RBW set to %f Hz." % rfsa.rbw.magnitude in file.read()
        assert "VBW set to %f Hz." % rfsa.vbw.magnitude in file.read()
        assert "Sweep time set to %f seconds." % rfsa.time.magnitude in file.read()
        assert "Reference set to %f watts." % rfsa.center.magnitude in file.read()

    rfsa.center = initial_center
    rfsa.stop = initial_stop
    rfsa.start = initial_start
    rfsa.rbw = initial_rbw
    rfsa.vbw = initial_vbw
    rfsa.time = initial_time
    rfsa.reference = inital_reference
