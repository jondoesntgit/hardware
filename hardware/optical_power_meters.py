# coding: utf-8
"""
Optical Power Meters
====================

.. module:: optical_power_meters
   :platform: Windows, Linux, OSX
   :synopsis: Python wrappers for optical power meters.

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>
.. moduleauthor:: Anjali Thontakudi

This module provides support for controlling optical power meters with Python.
Optical power meters can be loaded by

>>> import hardware
>>> opm = hardware.function_generators.Newport_1830_C('GPIB0:...')

"""

import visa
from hardware import u


class MockOpticalPowerMeter:
    """
    This class acts as a dummy optical power meter, used for testing

    Parameters:
        instr_name (str, optional): the name of the power meter

    Attributes:
        name (str): name of the power meter
        _power: the power (in Watts) the meter is set to
    """

    def __init__(self, instr_name = None):
        if not instr_name:
            self.name = "Optical Power Meter - Newport 1830C"
        else:
            self.name = instr_name
        self._power = 5 * u.milliwatt

    def identify(self):
        return self.name

    @property
    def power(self):
        return self._power

# link to manual: https://www.equipland.com/objects/catalog/product/extras/1030_1830-c.pdf
# Most basic measurements ususally done in Watts


class Newport_1830_C():
    """
    Hardware wrapper for Newport 1830C optical power meter.

    Parameters:
        visa_search_term (str): The address that is passed to
            ``visa.ResourceManager().open_resource()``

    Attributes:
        power (float): The measured power in Watts
    """
    def __init__(self, address):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(address)

    def identify(self):
        """
        Returns:
            str: The response from an ``*IDN?`` GPIB query.
        """
        return self.inst.query('*IDN?')[:-1]

    @property
    def power(self):
        return float(self.inst.query('D?')[:-1]) * u.milliwatt
