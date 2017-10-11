# coding: utf-8
"""
Optical Power Meters
====================

.. module:: optical_power_meters
   :platform: Windows, Linux, OSX
   :synopsis: Python wrappers for optical power meters.

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>

This module provides support for controlling optical power meters with Python.
Optical power meters can be loaded by

>>> import hardware
>>> opm = hardware.function_generators.Newport_1830_C('GPIB0:...')

"""

import visa


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
        return float(self.inst.query('D?')[:-1])