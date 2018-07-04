"""
Laser Diode Drivers
===================

.. module:: laser_diode_drivers
   :synopsis: Python wrappers for laser diode drivers
   :platform: Windows, Unix, OS X

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>

This module provides support for controlling laser diode drivers using the
Python language.

Laser diode drivers can be imported by

>>> import hardware
>>> ldd = hardware.laser_diode_drivers.ILX_Lightwave_3724B('GPIB0:...')
"""

import visa
from hardware import u

class MockLaserDiodeDriver:
    def __init__(self, instr_name = None):
        if not instr_name:
            self.name = "Laser Diode Driver - ILX Lightwave 3724B"
        else:
            self.name = instr_name
        self._current = 2 * u.amp

    def identify(self):
        return self.name

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        self._current = value * u.amp

class ILX_Lightwave_3724B():
    """
    Hardware wrapper for ILX Lightwave 3724 laser diode driver

    Args:
        visa_search_term (str): The address that is passed to
            ``visa.ResourceManager().open_resource()``

    Attributes:
        current (float): The current of the laser diode driver
    """

    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

    def current(self):
        return float(self.inst.query('LAS:LDI?')[:-1]) * u.amp

    @current.setter
    def current(self, val):
        self.inst.write('LAS:LDI %f' % val)
