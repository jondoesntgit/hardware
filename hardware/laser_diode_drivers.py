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
import pint

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
        self.ureg = pint.UnitRegistry()
        
    def current(self):
        return float(self.inst.query('LAS:LDI?')[:-1]) * self.ureg.amp

    @current.setter
    def current(self, val):
        self.inst.write('LAS:LDI %f' % val)
