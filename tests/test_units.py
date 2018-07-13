import hardware
from hardware import u, Q_
import pint
import pytest

def test_unit_registry():
    assert type(u) == pint.registry.UnitRegistry

def test_ldd():
    try:
        from hardware import ldd
    except ImportError:
        pytest.skip("Cannot import ldd.")

    assert ldd.current.units == u.milliamp

def test_opm():
    try:
        from hardware import opm
    except ImportError:
        pytest.skip("Cannot import opm.")
    assert opm.power.units == u.milliwatt

def test_spectum_analyzer():
    try:
        from hardware import rfsa
    except ImportError:
        pytest.skip("Cannot import rfsa.")

    assert rfsa.center.units == u.hertz
    assert rfsa.start.units == u.hertz
    assert rfsa.stop.units == u.hertz
    assert rfsa.rbw.units == u.hertz
    assert rfsa.vbw.units == u.hertz
    assert rfsa.time.units == u.second
    assert rfsa.reference.units == u.watt

    # Make sure test values are within acceptable range for instrument
