import hardware
from hardware import u
import pint


def test_unit_registry():
    assert type(u) == pint.registry.UnitRegistry
