# coding: utf-8
"""
Spectrum Analyzers
===================

.. module::  spectrum_analyzers
   :platform: Windows, Linux, OSX
   :synopsis: Python wrappers for lock-in amplifiers

.. moduleauthor:: Jonathan Wheeler <jamwheel@stanford.edu>

This module provides support for controlling spectrum analyzers with Python.
Spectrum analyzers can be imported by

>>> import hardware
>>> lia = hardware.spectrum_analyzers.ANDO_AQ6317B('GPIB0:...')

"""

import visa
import numpy as np


class ANDO_AQ6317B:
    """
    Hardware wrapper for ANDO AQ6317B Optical Spectrum Analyzer

    Parameters:
        visa_search_term (str): The address that is passed to
            ``visa.ResourceManager().open_resource()``
    """
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)

    def identify(self):
        """
        Returns:
            str: The response from an ``*IDN?`` GPIB query.
        """
        return self.inst.query('*IDN?')

    def set_timeout(self, milliseconds):
        """
        Sets the timeout of the instrument in milliseconds.

        Args:
            milliseconds(float): The timeout in milliseconds
        """
        self.inst.timeout = milliseconds

    def get_spectrum(self):
        """
        Returns the measured spectrum from a single reading of the instrument.
        Aliases to acquire

        Returns:
            tuple of arrays:
                The first array contains the wavelengths in nanometers.
                The second array contains the optical power in dBm.
        """
        power_string = self.inst.query('LDATB')
        power = np.array(power_string[:-2].split(','))
        power = power.astype(np.float)[2:]

        wavelength_string = self.inst.query('WDATB')
        wavelength = np.array(wavelength_string[:-2].split(','))
        wavelength = wavelength.astype(np.float)[2:]

        return wavelength, power

    # Alias
    acquire = get_spectrum


class Rohde_Schwarz_FSEA_20:
    """
    Hardware wrapper for Rohde & Schwarz FSEA 20 RF Spectrum Analyzer

    Parameters:
        visa_search_term (str): The address that is passed to
            ``visa.ResourceManager().open_resource()``
    """
    def __init__(self, visa_search_term):
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(visa_search_term)
