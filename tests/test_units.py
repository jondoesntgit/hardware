import hardware
from hardware import u
import pint
import pytests

def test_unit_registry():
    assert type(u) == pint.registry.UnitRegistry

def test_ldd():
    from hardware import ldd
    assert ldd.current.units == u.milliamp

def test_opm():
    from hardware import opm
    assert opm.power.units == u.milliwatt

def test_spectum_analyzer():
    from hardware import rfsa

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


def test_lia():
    from hardware import lia

    new_phas = 1200 * u.decidegree
    new_time_const = 300 * u.millisecond
    lia.phase = new_phas
    lia.time_constant = new_time_const

    # TODO: Store initial variables
    # TODO: Set new variables
    # TODO: Check the logs
    # TODO: Restore values to originals

    assert lia.phase.units == u.degree
    assert lia.time_constant.units == u.second
