from hardware import u
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

    assert rfsa.center.units == u.megahertz
    assert rfsa.start.units == u.megahertz
    assert rfsa.stop.units == u.megahertz
    assert rfsa.rbw.units == u.megahertz
    assert rfsa.vbw.units == u.megahertz
    assert rfsa.time.units == u.second
    assert rfsa.reference.units == u.watt

    center = 10 * u.megahertz
    start = 8 * u.megahertz
    stop = 12 * u.megahertz

    # TODO: Store initial variables
    # TODO: Set new variables
    # TODO: Check the logs
    # TODO: Restore values to originals
